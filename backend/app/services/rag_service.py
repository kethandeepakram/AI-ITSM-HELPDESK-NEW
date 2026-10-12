import os
import math
import numpy as np
from app.config import settings
from app.database.mongodb import get_knowledge_collection
from seed_knowledge import KNOWLEDGE_ARTICLES

_local_model = None

def _get_embedding_model():
    global _local_model
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Load lightweight all-MiniLM-L6-v2
            _local_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[RAG] SentenceTransformer load warning: {e}. Using TF-IDF vectorizer fallback.")
            _local_model = "fallback"
    return _local_model

def calculate_cosine_similarity(vec1: list, vec2: list) -> float:
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
    if v1.size == 0 or v2.size == 0 or v1.shape != v2.shape:
        return 0.0
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def _tokenize(text: str) -> set:
    return set(re.findall(r"\w+", text.lower())) if "re" in globals() else set(text.lower().replace(",", " ").replace(".", " ").split())

import re

def compute_lexical_similarity(query: str, article: dict) -> float:
    """Score how much meaningful query vocabulary is supported by an article."""
    stop_words = {
        "the", "and", "for", "with", "from", "that", "this", "how", "what",
        "when", "where", "why", "can", "you", "are", "not", "but", "into",
        "please", "help", "need", "want", "have", "has", "since", "about",
        "tell", "show", "give", "does", "cannot", "unable"
    }

    def terms(value: str) -> set[str]:
        return {
            word.lower()
            for word in re.findall(r"\\b[a-zA-Z0-9_]+\\b", str(value or ""))
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
    # Category metadata can be a useful signal, but should not dominate.
    keyword_terms.update(terms(article.get("category", "")))
    keyword_terms.update(terms(article.get("subcategory", "")))

    def coverage(corpus_terms: set[str]) -> float:
        return len(query_terms.intersection(corpus_terms)) / len(query_terms)

    keyword_coverage = coverage(keyword_terms)
    title_coverage = coverage(title_terms)
    content_coverage = coverage(content_terms)

    # Exact keywords/title evidence is stronger than a common word in long text.
    score = (
        0.50 * keyword_coverage
        + 0.30 * title_coverage
        + 0.20 * content_coverage
    )
    return round(min(score, 0.98), 4)

def search_knowledge_base(query: str, top_k: int = 3) -> list:
    """
    RAG Semantic Retrieval pipeline:
    Document -> Chunking -> Embedding -> Vector Distance -> Semantic Re-Ranking -> Grounded Context
    """
    collection = get_knowledge_collection()
    articles = list(collection.find({}, {"_id": 0}))

    # Fallback to in-memory articles if database is not seeded yet
    if not articles:
        articles = KNOWLEDGE_ARTICLES

    results = []
    model = _get_embedding_model()

    query_embedding = None
    if model != "fallback" and hasattr(model, "encode"):
        try:
            query_embedding = model.encode(query).tolist()
        except Exception:
            query_embedding = None

    for article in articles:
        sem_score = 0.0
        # If pre-computed or on-the-fly embedding available
        if query_embedding:
            article_text = f"{article.get('title', '')} {article.get('content', '')}"
            if "embedding" not in article:
                try:
                    article_embedding = model.encode(article_text).tolist()
                except Exception:
                    article_embedding = None
            else:
                article_embedding = article.get("embedding")

            if article_embedding:
                sem_score = calculate_cosine_similarity(query_embedding, article_embedding)

        lex_score = compute_lexical_similarity(query, article)
        
        # Combined hybrid score (Dense Semantic + Sparse Keyword)
        if sem_score > 0:
            combined_score = (sem_score * 0.65) + (lex_score * 0.35)
        else:
            combined_score = lex_score

        # Format clean response chunk
        results.append({
            "article": {
                "id": article.get("id"),
                "title": article.get("title"),
                "category": article.get("category"),
                "subcategory": article.get("subcategory", article.get("category")),
                "content": article.get("content"),
                "source": article.get("source", f"IT Knowledge Base / {article.get('id')}"),
                "keywords": article.get("keywords", [])
            },
            "score": round(float(combined_score), 4),
            "relevance_percentage": f"{min(int(combined_score * 100), 99)}%"
        })

    # Filter irrelevant matches before applying top_k so a low-scoring article
    # cannot crowd out a more relevant article later in the list.
    relevant_results = [item for item in results if item["score"] >= 0.22]
    relevant_results.sort(key=lambda item: item["score"], reverse=True)

    try:
        result_limit = max(0, int(top_k))
    except (TypeError, ValueError):
        result_limit = 3
    return relevant_results[:result_limit]