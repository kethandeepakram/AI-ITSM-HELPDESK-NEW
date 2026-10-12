import os
import json
from datetime import datetime
from copy import deepcopy
from pymongo import MongoClient
from app.config import settings

_mongo_client = None
_database_instance = None

class LocalCollection:
    """In-memory collection with JSON persistence fallback for zero-config demonstration."""
    def __init__(self, name: str, store: dict):
        self.name = name
        self.store = store
        if self.name not in self.store:
            self.store[self.name] = []

    def _matches(self, doc: dict, query: dict) -> bool:
        if not query:
            return True
        for k, v in query.items():
            if isinstance(v, dict):
                if "$regex" in v:
                    import re
                    pattern = v["$regex"]
                    if not re.search(pattern, str(doc.get(k, ""))):
                        return False
                elif "$exists" in v:
                    exists = k in doc
                    if exists != v["$exists"]:
                        return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    def insert_one(self, doc: dict):
        d = deepcopy(doc)
        if "_id" not in d:
            import uuid
            d["_id"] = str(uuid.uuid4())
        self.store[self.name].append(d)
        class Result:
            inserted_id = d["_id"]
        return Result()

    def insert_many(self, docs: list):
        results = []
        for doc in docs:
            res = self.insert_one(doc)
            results.append(res.inserted_id)
        return results

    def find_one(self, query: dict = None, projection: dict = None):
        results = self.find(query, projection)
        return results[0] if results else None

    def find(self, query: dict = None, projection: dict = None):
        query = query or {}
        matches = [d for d in self.store[self.name] if self._matches(d, query)]

        class Cursor:
            def __init__(self, items, projection):
                self.items = deepcopy(items)
                self.projection = projection

            def sort(self, key, direction=1):
                reverse = direction == -1
                self.items.sort(key=lambda x: str(x.get(key, "")), reverse=reverse)
                return self

            def limit(self, n):
                self.items = self.items[:n]
                return self

            def __iter__(self):
                for item in self.items:
                    yield self._project(item)

            def _project(self, item):
                if not self.projection:
                    return item
                if "_id" in self.projection and self.projection["_id"] == 0:
                    item.pop("_id", None)
                return item

            def __len__(self):
                return len(self.items)

        cursor = Cursor(matches, projection)
        return list(cursor)

    def count_documents(self, query: dict = None) -> int:
        return len(self.find(query))

    def update_one(self, query: dict, update: dict):
        for doc in self.store[self.name]:
            if self._matches(doc, query):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        doc[k] = v
                return {"modified_count": 1}
        return {"modified_count": 0}

    def delete_many(self, query: dict = None):
        before = len(self.store[self.name])
        if not query:
            self.store[self.name] = []
        else:
            self.store[self.name] = [d for d in self.store[self.name] if not self._matches(d, query)]
        return {"deleted_count": before - len(self.store[self.name])}

    def aggregate(self, pipeline: list):
        return []

class LocalDatabase:
    """Mock database instance used when MongoDB Atlas URI is not configured."""
    def __init__(self):
        self._store = {}

    def __getitem__(self, collection_name: str):
        return LocalCollection(collection_name, self._store)

_local_db = LocalDatabase()

def get_database():
    global _mongo_client, _database_instance

    if settings.MONGODB_URI:
        try:
            if _mongo_client is None:
                _mongo_client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
                # quick check
                _mongo_client.admin.command('ping')
            return _mongo_client[settings.MONGODB_DATABASE]
        except Exception as e:
            print(f"[Database] Warning: Could not connect to MongoDB Atlas ({e}). Falling back to local storage.")
            return _local_db
    return _local_db

def get_tickets_collection():
    db = get_database()
    return db["tickets"]

def get_knowledge_collection():
    db = get_database()
    return db["knowledge_articles"]

def get_audit_collection():
    db = get_database()
    return db["automation_audit"]

def get_provisioning_collection():
    db = get_database()
    return db["software_provisioning"]

def get_servicenow_collection():
    db = get_database()
    return db["servicenow_incidents"]