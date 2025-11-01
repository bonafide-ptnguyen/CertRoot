import types
import pytest

from backend.core import database as db

# ----------------------------
# Fakes for Mongo behavior
# ----------------------------
class FakeBulkResult:
    def __init__(self, upserted=0, modified=0):
        self.upserted_count = upserted
        self.modified_count = modified


class FakeCollection:
    def __init__(self, find_one_result=None, bulk_result=None, bulk_raises=False):
        self._create_index_called = False
        self._find_one_result = find_one_result
        self._bulk_result = bulk_result or FakeBulkResult()
        self._bulk_raises = bulk_raises

    def create_index(self, *args, **kwargs):
        self._create_index_called = True

    def bulk_write(self, ops, ordered=False):
        if self._bulk_raises:
            raise RuntimeError("bulk write failed!")
        return self._bulk_result

    def find_one(self, filt):
        return self._find_one_result


class _AnyDB:
    """Key-agnostic DB: db['anything'] returns the FakeCollection directly."""
    def __init__(self, collection):
        self._collection = collection

    def __getitem__(self, _key):
        return self._collection


class FakeClientAny:
    """Key-agnostic Client: client['anything']['anything'] → FakeCollection."""
    def __init__(self, collection):
        self._db = _AnyDB(collection)

    def __getitem__(self, _dbname):
        return self._db


class FakeUpdateOne:
    def __init__(self, filter_doc, update_doc, upsert=False):
        self.filter_doc = filter_doc
        self.update_doc = update_doc
        self.upsert = upsert


# ----------------------------
# get_mongo_collection tests
# ----------------------------
def test_get_mongo_collection_no_uri(monkeypatch, capsys):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setattr(db, "MONGODB_URI", "", raising=True)

    col = db.get_mongo_collection()
    out = capsys.readouterr().out
    assert col is None
    assert "MONGODB_URI not set" in out


def test_get_mongo_collection_success(monkeypatch):
    fake_col = FakeCollection()
    monkeypatch.setattr(db, "MONGODB_URI", "mongodb://fake", raising=True)
    monkeypatch.setattr(db, "MongoClient", lambda uri: FakeClientAny(fake_col), raising=True)

    col = db.get_mongo_collection()
    assert isinstance(col, FakeCollection)
    assert col._create_index_called is True


def test_get_mongo_collection_failure(monkeypatch, capsys):
    monkeypatch.setattr(db, "MONGODB_URI", "mongodb://bad", raising=True)

    def _boom(_): 
        raise RuntimeError("cannot connect")

    monkeypatch.setattr(db, "MongoClient", _boom, raising=True)
    col = db.get_mongo_collection()
    out = capsys.readouterr().out
    assert col is None
    assert "MongoDB connection failed" in out


# ----------------------------
# upsert_hashes tests
# ----------------------------
def test_upsert_hashes_no_collection(monkeypatch):
    monkeypatch.setattr(db, "get_mongo_collection", lambda: None, raising=True)
    result = db.upsert_hashes([("a.txt", "H1", 3)])
    assert result is None


def test_upsert_hashes_empty_data(monkeypatch):
    fake_col = FakeCollection()
    monkeypatch.setattr(db, "get_mongo_collection", lambda: fake_col, raising=True)
    monkeypatch.setattr(db, "UpdateOne", FakeUpdateOne, raising=True)
    result = db.upsert_hashes([])
    assert result is None


def test_upsert_hashes_success(monkeypatch):
    fake_result = FakeBulkResult(upserted=2, modified=1)
    fake_col = FakeCollection(bulk_result=fake_result)
    monkeypatch.setattr(db, "get_mongo_collection", lambda: fake_col, raising=True)
    monkeypatch.setattr(db, "UpdateOne", FakeUpdateOne, raising=True)

    data = [("a.txt", "HASH_A", 10), ("b.txt", "HASH_B", 11)]
    result = db.upsert_hashes(data)
    assert result == {"upserted": 2, "modified": 1}


def test_upsert_hashes_bulkwrite_exception(monkeypatch, capsys):
    fake_col = FakeCollection(bulk_raises=True)
    monkeypatch.setattr(db, "get_mongo_collection", lambda: fake_col, raising=True)
    monkeypatch.setattr(db, "UpdateOne", FakeUpdateOne, raising=True)

    res = db.upsert_hashes([("a.txt", "H", 99)])
    out = capsys.readouterr().out
    assert res is None
    assert "Error writing to MongoDB" in out


# ----------------------------
# find_file_by_hash tests
# ----------------------------
def test_find_file_by_hash_no_collection(monkeypatch):
    monkeypatch.setattr(db, "get_mongo_collection", lambda: None, raising=True)
    assert db.find_file_by_hash("X") is None


def test_find_file_by_hash_found(monkeypatch):
    expected = {"filename": "z.txt", "hash": "Z_HASH", "recordId": 42}
    fake_col = FakeCollection(find_one_result=expected)
    monkeypatch.setattr(db, "get_mongo_collection", lambda: fake_col, raising=True)

    got = db.find_file_by_hash("Z_HASH")
    assert got == expected
