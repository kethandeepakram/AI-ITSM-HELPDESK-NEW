from copy import deepcopy
import re
import uuid

from pymongo import MongoClient
from app.config import settings


_mongo_client = None


class LocalCursor:
    """Small in-memory cursor compatible with the PyMongo methods used by this app."""

    def __init__(self, items: list[dict], projection: dict | None = None):
        self.items = deepcopy(items)
        self.projection = projection or {}

    def sort(self, key_or_list, direction: int = 1):
        """Support PyMongo-style sort('field', -1) and sort([('field', -1)])."""
        if isinstance(key_or_list, str):
            sort_fields = [(key_or_list, direction)]
        else:
            sort_fields = list(key_or_list)

        # Stable sorts applied in reverse field order support multi-key sorting.
        for key, sort_direction in reversed(sort_fields):
            self.items.sort(
                key=lambda item: (item.get(key) is None, item.get(key)),
                reverse=sort_direction == -1,
            )
        return self

    def limit(self, count: int):
        self.items = self.items[:max(0, count)]
        return self

    def _project(self, item: dict) -> dict:
        result = deepcopy(item)
        # Support the projection forms used in this project.
        excluded = [key for key, value in self.projection.items() if value == 0]
        included = [key for key, value in self.projection.items() if value == 1 and key != "_id"]

        if included:
            projected = {key: result[key] for key in included if key in result}
            if self.projection.get("_id", 1) != 0 and "_id" in result:
                projected["_id"] = result["_id"]
            return projected

        for key in excluded:
            result.pop(key, None)
        return result

    def __iter__(self):
        return iter([self._project(item) for item in self.items])

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self._project(item) for item in self.items[index]]
        return self._project(self.items[index])


class LocalCollection:
    """In-memory demo collection implementing the PyMongo operations this app uses.

    This fallback is not durable: its contents are lost when the process restarts.
    """

    def __init__(self, name: str, store: dict):
        self.name = name
        self.store = store
        self.store.setdefault(self.name, [])

    def _matches(self, doc: dict, query: dict | None) -> bool:
        for key, expected in (query or {}).items():
            actual = doc.get(key)
            if isinstance(expected, dict):
                if "$regex" in expected:
                    flags = re.IGNORECASE if expected.get("$options") == "i" else 0
                    if not re.search(expected["$regex"], str(actual or ""), flags):
                        return False
                elif "$exists" in expected:
                    if (key in doc) != bool(expected["$exists"]):
                        return False
                else:
                    return False
            elif actual != expected:
                return False
        return True

    def insert_one(self, doc: dict):
        item = deepcopy(doc)
        item.setdefault("_id", str(uuid.uuid4()))
        self.store[self.name].append(item)

        class Result:
            inserted_id = item["_id"]

        return Result()

    def insert_many(self, docs: list[dict]):
        return [self.insert_one(doc).inserted_id for doc in docs]

    def find_one(self, query: dict | None = None, projection: dict | None = None):
        cursor = self.find(query, projection).limit(1)
        return cursor[0] if len(cursor) else None

    def find(self, query: dict | None = None, projection: dict | None = None):
        matches = [doc for doc in self.store[self.name] if self._matches(doc, query)]
        return LocalCursor(matches, projection)

    def count_documents(self, query: dict | None = None) -> int:
        return sum(1 for doc in self.store[self.name] if self._matches(doc, query))

    def update_one(self, query: dict, update: dict, upsert: bool = False):
        for doc in self.store[self.name]:
            if self._matches(doc, query):
                if "$set" in update:
                    doc.update(deepcopy(update["$set"]))
                return {"matched_count": 1, "modified_count": 1, "upserted_id": None}

        if upsert:
            new_doc = {
                key: deepcopy(value)
                for key, value in (query or {}).items()
                if not isinstance(value, dict)
            }
            if "$set" in update:
                new_doc.update(deepcopy(update["$set"]))
            result = self.insert_one(new_doc)
            return {"matched_count": 0, "modified_count": 0, "upserted_id": result.inserted_id}

        return {"matched_count": 0, "modified_count": 0, "upserted_id": None}

    def delete_many(self, query: dict | None = None):
        before = len(self.store[self.name])
        if not query:
            self.store[self.name] = []
        else:
            self.store[self.name] = [
                doc for doc in self.store[self.name] if not self._matches(doc, query)
            ]
        return {"deleted_count": before - len(self.store[self.name])}

    def aggregate(self, pipeline: list):
        # No current route depends on aggregation results in fallback mode.
        return []


class LocalDatabase:
    """Database-like wrapper for no-configuration local demonstrations."""

    def __init__(self):
        self._store = {}

    def __getitem__(self, collection_name: str):
        return LocalCollection(collection_name, self._store)


_local_db = LocalDatabase()


def get_database():
    global _mongo_client

    if settings.MONGODB_URI:
        try:
            if _mongo_client is None:
                _mongo_client = MongoClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=3000,
                )
            _mongo_client.admin.command("ping")
            return _mongo_client[settings.MONGODB_DATABASE]
        except Exception as exc:
            if _mongo_client is not None:
                try:
                    _mongo_client.close()
                except Exception:
                    pass
            _mongo_client = None
            print(
                f"[Database] Warning: Could not connect to MongoDB Atlas ({exc}). "
                "Using in-memory demo storage; changes will not persist after restart."
            )
            return _local_db

    return _local_db


def get_tickets_collection():
    return get_database()["tickets"]


def get_knowledge_collection():
    return get_database()["knowledge_articles"]


def get_audit_collection():
    return get_database()["automation_audit"]


def get_provisioning_collection():
    return get_database()["software_provisioning"]


def get_servicenow_collection():
    return get_database()["servicenow_incidents"]
