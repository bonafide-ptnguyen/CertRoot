import sys
import pathlib
import types
from fastapi.testclient import TestClient



BACKEND_DIR = pathlib.Path(__file__).resolve().parents[2]  
PROJECT_ROOT = BACKEND_DIR.parent                          

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))



core_pkg = types.ModuleType("core")
file_hasher = types.ModuleType("core.file_hasher")
database = types.ModuleType("core.database")
interact_certifier = types.ModuleType("core.interact_certifier")

_calls = {"process_folder_once": 0}

def _fake_hash_file(path: str) -> str:
    return "FAKE_HASH"

def _fake_process_folder_once():
    _calls["process_folder_once"] += 1

def _fake_find_file_by_hash(h: str):
    return None

def _fake_retrieve_record(record_id: str):
    return ("CHAIN_HASH", 321, "2025-10-31T00:00:00Z")

file_hasher.hash_file = _fake_hash_file
file_hasher.process_folder_once = _fake_process_folder_once
database.find_file_by_hash = _fake_find_file_by_hash
interact_certifier.retrieve_record = _fake_retrieve_record

core_pkg.file_hasher = file_hasher
core_pkg.database = database
core_pkg.interact_certifier = interact_certifier

sys.modules["core"] = core_pkg
sys.modules["core.file_hasher"] = file_hasher
sys.modules["core.database"] = database
sys.modules["core.interact_certifier"] = interact_certifier

try:
    from app import app as fastapi_app
except ImportError:
    # fallback if app.py is one directory above backend/
    sys.path.insert(0, str(PROJECT_ROOT))
    from backend.app import app as fastapi_app


def _client():
    return TestClient(fastapi_app)


def test_startup_calls_process_folder_once():
    _calls["process_folder_once"] = 0
    with _client() as c:
        c.get("/openapi.json")
    assert _calls["process_folder_once"] == 1


def test_verify_returns_no_match_when_db_misses(monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "find_file_by_hash", lambda h: None, raising=True)
    monkeypatch.setattr(app_module, "hash_file", lambda p: "HASH_NO_MATCH", raising=True)

    with _client() as c:
        files = {"file": ("note.txt", b"hello world", "text/plain")}
        r = c.post("/verify", files=files)
        body = r.json()
        assert r.status_code == 200
        assert body["status"] == "no_match"
        assert body["hash"] == "HASH_NO_MATCH"
        assert "No such file" in body["message"]


def test_verify_returns_original_when_record_exists(monkeypatch):
    import app as app_module
    record = {"filename": "report.pdf", "hash": "REC_HASH", "recordId": "RID-007"}
    monkeypatch.setattr(app_module, "find_file_by_hash", lambda h: record, raising=True)
    monkeypatch.setattr(app_module, "hash_file", lambda p: "REC_HASH", raising=True)
    monkeypatch.setattr(
        app_module,
        "retrieve_record",
        lambda rid: ("CHAIN_OK", 777, "2025-10-30T12:34:56Z"),
        raising=True,
    )

    with _client() as c:
        files = {"file": ("doc.pdf", b"%PDF-1.4 ...", "application/pdf")}
        r = c.post("/verify", files=files)
        body = r.json()
        assert r.status_code == 200
        assert body["status"] == "original"
        assert body["matched_file"] == "report.pdf"
        assert body["hash_verified"] == "CHAIN_OK"


def test_verify_handles_hash_errors(monkeypatch):
    import app as app_module

    def boom(_p: str):
        raise RuntimeError("hash failure!")

    monkeypatch.setattr(app_module, "hash_file", boom, raising=True)

    with _client() as c:
        files = {"file": ("bad.bin", b"\x00\x01\x02", "application/octet-stream")}
        r = c.post("/verify", files=files)
        body = r.json()
        assert r.status_code == 200
        assert body["status"] == "error"
        assert "hash failure" in body["error"].lower()


def test_verify_removes_temp_file(monkeypatch):
    import app as app_module
    removed = {"path": None}
    monkeypatch.setattr(app_module.os, "remove", lambda p: removed.update(path=p), raising=True)
    monkeypatch.setattr(app_module, "hash_file", lambda p: "TMP_HASH", raising=True)
    monkeypatch.setattr(app_module, "find_file_by_hash", lambda h: None, raising=True)

    with _client() as c:
        files = {"file": ("tmp.txt", b"data", "text/plain")}
        r = c.post("/verify", files=files)
        assert r.status_code == 200
        assert r.json()["status"] == "no_match"
        assert removed["path"] is not None


def test_verify_reads_uploaded_bytes(monkeypatch):
    import app as app_module
    captured = {"bytes": None}

    def _inspect_hash_file(path: str) -> str:
        with open(path, "rb") as f:
            captured["bytes"] = f.read()
        return "INSPECTED_HASH"

    monkeypatch.setattr(app_module, "hash_file", _inspect_hash_file, raising=True)
    monkeypatch.setattr(app_module, "find_file_by_hash", lambda h: None, raising=True)

    payload = b"The quick brown fox jumps over the lazy dog"
    with _client() as c:
        files = {"file": ("payload.txt", payload, "text/plain")}
        r = c.post("/verify", files=files)
        body = r.json()
        assert body["status"] == "no_match"
        assert body["hash"] == "INSPECTED_HASH"
        assert captured["bytes"] == payload


def test_multiple_requests_are_isolated(monkeypatch):
    import app as app_module
    seq = {"i": 0}

    def _hash_file(_p: str) -> str:
        seq["i"] += 1
        return f"HASH_{seq['i']}"

    monkeypatch.setattr(app_module, "hash_file", _hash_file, raising=True)
    monkeypatch.setattr(app_module, "find_file_by_hash", lambda h: None, raising=True)

    with _client() as c:
        r1 = c.post("/verify", files={"file": ("a.txt", b"a", "text/plain")})
        r2 = c.post("/verify", files={"file": ("b.txt", b"b", "text/plain")})
        assert r1.status_code == r2.status_code == 200
        assert r1.json()["hash"] == "HASH_1"
        assert r2.json()["hash"] == "HASH_2"
