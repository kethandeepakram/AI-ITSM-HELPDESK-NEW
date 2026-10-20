import hashlib
import json
import re
from pathlib import Path

import numpy as np

from app.config import settings
from app.database.mongodb import get_knowledge_collection
from seed_knowledge import KNOWLEDGE_ARTICLES


_local_model = None
_chroma_client = None
_chroma_collection = None
_vector_index_signature = None
_chroma_warning_logged = False


def _get_embedding_model():
    """Load the configured open-source sentence-transformers model, or mark fallback mode."""
    global _local_model
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _local_model = SentenceTransformer(settings.HF_EMBEDDING_MODEL)
        except Exception as exc:
            print(
                f"[RAG] Embedding model unavailable ({exc}). "
                "Using lexical-overlap fallback until the backend is restarted."
            )
            _local_model = "fallback"
    return _local_model


def calculate_cosine_similarity(vec1: list, vec2: list) -> float:
    v1 = np.asarray(vec1, dtype=float)
    v2 = np.asarray(vec2, dtype=float)
    if v1.size == 0 or v2.size == 0 or v1.shape != v2.shape:
        return 0.0
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def compute_lexical_similarity(query: str, article: dict) -> float:
    """Score query vocabulary coverage, giving title and article keywords extra weight."""
    stop_words = {
        "the", "and", "for", "with", "from", "that", "this", "how", "what",
        "when", "where", "why", "can", "you", "are", "not", "but", "into",
        "please", "help", "need", "want", "have", "has", "since", "about",
        "tell", "show", "give", "does", "cannot", "unable", "your", "our",
    }

    def terms(value: str) -> set[str]:
        return {
            word.lower()
            for word in re.findall(r"\b[a-zA-Z0-9_]+\b", str(value or ""))
            if len(word) >= 3 and word.lower() not in stop_words
        }

    query_terms = terms(query)
    if not query_terms:
        return 0.0

    title_terms = terms(article.get("title", ""))
    content_terms = terms(article.get("content", ""))
    keyword_terms = set()
    for keyword in article.get("keywords", []) or []:
        keyword_terms.update(terms(str(keyword)))
    keyword_terms.update(terms(article.get("category", "")))
    keyword_terms.update(terms(article.get("subcategory", "")))

    def coverage(corpus_terms: set[str]) -> float:
        return len(query_terms.intersection(corpus_terms)) / len(query_terms)

    score = (
        0.50 * coverage(keyword_terms)
        + 0.30 * coverage(title_terms)
        + 0.20 * coverage(content_terms)
    )
    return round(min(score, 0.98), 4)


def chunk_text(text: str, chunk_words: int = 120, overlap_words: int = 20) -> list[str]:
    """Split an article into overlapping word chunks while retaining useful context."""
    words = str(text or "").split()
    if not words:
        return []
    chunk_words = max(20, int(chunk_words))
    overlap_words = min(max(0, int(overlap_words)), chunk_words - 1)

    chunks = []
    step = chunk_words - overlap_words
    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + chunk_words]).strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_words >= len(words):
            break
    return chunks


def _load_articles() -> list[dict]:
    collection = get_knowledge_collection()
    articles = list(collection.find({}, {"_id": 0}))
    return articles if articles else KNOWLEDGE_ARTICLES


def _build_chunk_records(articles: list[dict]) -> list[dict]:
    records = []
    for article in articles:
        article_id = str(article.get("id") or article.get("title") or "knowledge-article")
        title = str(article.get("title", "IT Support Article"))
        keywords = article.get("keywords", []) or []
        if isinstance(keywords, str):
            keywords = [item.strip() for item in keywords.split(",") if item.strip()]
        source = str(article.get("source") or f"IT Knowledge Base / {article_id}")
        category = str(article.get("category") or "General IT")
        subcategory = str(article.get("subcategory") or category)
        chunks = chunk_text(article.get("content", ""))
        for chunk_index, chunk in enumerate(chunks):
            # Embed the title and taxonomy alongside each chunk so short passages
            # keep the meaning of their parent article.
            embedding_text = (
                f"Title: {title}\nCategory: {category}\n"
                f"Subcategory: {subcategory}\nKeywords: {' '.join(map(str, keywords))}\n"
                f"Source: {source}\nContent: {chunk}"
            )
            records.append({
                "id": f"{article_id}::chunk-{chunk_index:04d}",
                "article_id": article_id,
                "chunk_index": chunk_index,
                "title": title,
                "category": category,
                "subcategory": subcategory,
                "source": source,
                "keywords": keywords,
                "version": str(article.get("version", "")),
                "content": chunk,
                "embedding_text": embedding_text,
            })
    return records


def _get_chroma_collection():
    """Create or reuse the persistent Chroma collection."""
    global _chroma_client, _chroma_collection

    if _chroma_collection is not None:
        return _chroma_collection

    import chromadb

    persist_path = Path(settings.CHROMA_PERSIST_DIRECTORY).expanduser()
    if not persist_path.is_absolute():
        # Treat relative paths as backend-relative no matter which directory
        # the developer used to launch uvicorn.
        persist_path = Path(__file__).resolve().parents[2] / persist_path
    persist_path.mkdir(parents=True, exist_ok=True)
    _chroma_client = chromadb.PersistentClient(path=str(persist_path))
    _chroma_collection = _chroma_client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"[RAG] Chroma collection ready: {settings.CHROMA_COLLECTION_NAME}")
    return _chroma_collection


def _sync_chroma_index(articles: list[dict], model) -> list[dict]:
    """Index article chunks into Chroma only when source content has changed."""
    global _vector_index_signature

    records = _build_chunk_records(articles)
    signature_payload = [
        {key: value for key, value in record.items() if key != "embedding_text"}
        for record in records
    ]
    signature = hashlib.sha256(
        json.dumps(signature_payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()

    chroma_collection = _get_chroma_collection()
    if _vector_index_signature == signature:
        return records

    if records:
        embedding_matrix = model.encode(
            [record["embedding_text"] for record in records],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        embeddings = np.asarray(embedding_matrix, dtype=float).tolist()
        metadatas = [
            {
                "article_id": record["article_id"],
                "chunk_index": record["chunk_index"],
                "title": record["title"],
                "category": record["category"],
                "subcategory": record["subcategory"],
                "source": record["source"],
                "keywords": " | ".join(map(str, record["keywords"])),
                "version": record["version"],
            }
            for record in records
        ]
        chroma_collection.upsert(
            ids=[record["id"] for record in records],
            documents=[record["content"] for record in records],
            metadatas=metadatas,
            embeddings=embeddings,
        )

    # Remove chunks for articles that were deleted or shortened.
    existing = chroma_collection.get(include=["metadatas"])
    wanted_ids = {record["id"] for record in records}
    stale_ids = [doc_id for doc_id in existing.get("ids", []) if doc_id not in wanted_ids]
    if stale_ids:
        chroma_collection.delete(ids=stale_ids)

    _vector_index_signature = signature
    print(f"[RAG] Chroma index synchronized with {len(records)} knowledge chunks.")
    return records


def _article_from_hit(document: str, metadata: dict) -> dict:
    keyword_string = metadata.get("keywords", "")
    return {
        "id": metadata.get("article_id"),
        "title": metadata.get("title"),
        "category": metadata.get("category"),
        "subcategory": metadata.get("subcategory", metadata.get("category")),
        "content": document,
        "source": metadata.get("source"),
        "keywords": [item.strip() for item in keyword_string.split("|") if item.strip()],
        "version": metadata.get("version", ""),
        "chunk_index": metadata.get("chunk_index", 0),
    }


def _search_with_chroma(query: str, articles: list[dict], model, top_k: int) -> list[dict]:
    global _chroma_warning_logged

    try:
        records = _sync_chroma_index(articles, model)
        if not records:
            return []

        query_embedding = np.asarray(
            model.encode(query, normalize_embeddings=True, show_progress_bar=False),
            dtype=float,
        ).tolist()
        chroma_collection = _get_chroma_collection()
        n_results = min(len(records), max(top_k * 5, top_k, 1))
        response = chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        documents = (response.get("documents") or [[]])[0]
        metadatas = (response.get("metadatas") or [[]])[0]
        distances = (response.get("distances") or [[]])[0]
        results = []
        seen_articles = set()
        # Chroma stores flattened word chunks for semantic search. Reattach the
        # original source article after ranking so answers and fallbacks retain
        # full text and line breaks instead of showing one flattened chunk.
        source_articles = {
            str(source.get("id")): source
            for source in articles
            if source.get("id") is not None
        }

        for document, metadata, distance in zip(documents, metadatas, distances):
            metadata = metadata or {}
            article = _article_from_hit(document or "", metadata)
            article_id = article.get("id")
            # Return the best matching chunk per source article. The vector search
            # can return several chunks from the same article.
            if article_id in seen_articles:
                continue
            seen_articles.add(article_id)

            source_article = source_articles.get(str(article_id))
            if source_article:
                article.update({
                    "title": source_article.get("title", article.get("title")),
                    "category": source_article.get("category", article.get("category")),
                    "subcategory": source_article.get("subcategory", article.get("subcategory")),
                    "content": source_article.get("content", article.get("content")),
                    "source": source_article.get("source", article.get("source")),
                    "keywords": source_article.get("keywords", article.get("keywords")),
                    "version": source_article.get("version", article.get("version")),
                })

            semantic_score = max(0.0, min(1.0, 1.0 - float(distance or 0.0)))
            lexical_score = compute_lexical_similarity(query, article)
            combined_score = 0.70 * semantic_score + 0.30 * lexical_score
            results.append({
                "article": article,
                "score": round(float(combined_score), 4),
                "semantic_score": round(float(semantic_score), 4),
                "lexical_score": round(float(lexical_score), 4),
                "relevance_percentage": f"{min(int(combined_score * 100), 99)}%",
            })

        results.sort(key=lambda item: item["score"], reverse=True)
        return [item for item in results if item["score"] >= 0.22][:top_k]
    except Exception as exc:
        if not _chroma_warning_logged:
            print(f"[RAG] Chroma retrieval unavailable ({exc}). Falling back to lexical retrieval.")
            _chroma_warning_logged = True
        return []


def _search_lexically(query: str, articles: list[dict], top_k: int) -> list[dict]:
    results = []
    for article in articles:
        lexical_score = compute_lexical_similarity(query, article)
        if lexical_score < 0.22:
            continue
        results.append({
            "article": {
                "id": article.get("id"),
                "title": article.get("title"),
                "category": article.get("category"),
                "subcategory": article.get("subcategory", article.get("category")),
                "content": article.get("content"),
                "source": article.get("source", f"IT Knowledge Base / {article.get('id')}"),
                "keywords": article.get("keywords", []),
                "version": article.get("version", ""),
                "chunk_index": 0,
            },
            "score": lexical_score,
            "semantic_score": 0.0,
            "lexical_score": lexical_score,
            "relevance_percentage": f"{min(int(lexical_score * 100), 99)}%",
        })
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def search_knowledge_base(query: str, top_k: int = 3) -> list:
    """Search knowledge chunks with Chroma + embeddings; use lexical fallback if unavailable."""
    if not str(query or "").strip():
        return []

    try:
        result_limit = max(1, min(int(top_k), 10))
    except (TypeError, ValueError):
        result_limit = 3

    articles = _load_articles()
    model = _get_embedding_model()

    if model != "fallback" and hasattr(model, "encode"):
        results = _search_with_chroma(query.strip(), articles, model, result_limit)
        if results:
            return results

    return _search_lexically(query.strip(), articles, result_limit)
