import types
import pathlib
import csv
import pytest
import warnings
from backend.core import file_hasher as fh

# Suppress websockets deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets")

# Create and install blake3 stub BEFORE importing file_hasher
if "blake3" not in __import__("sys").modules:
    blake3_stub = types.ModuleType("blake3")


    class _FakeBlake3Ctx:
        def __init__(self):
            self._buf = bytearray()


        def update(self, b: bytes):
            self._buf.extend(b)


        def hexdigest(self):
            # deterministic "hash" that shows what was read
            return "HEX(" + self._buf.decode("utf-8", errors="ignore") + ")"


    def blake3():
        return _FakeBlake3Ctx()


    blake3_stub.blake3 = blake3
    __import__("sys").modules["blake3"] = blake3_stub


# --- Stub web3 (since file_hasher indirectly imports interact_certifier → web3) ---
if "web3" not in __import__("sys").modules:
    web3_stub = types.ModuleType("web3")


    class _Web3Shim:
        class HTTPProvider:
            def __init__(self, url):
                self.url = url


        def __new__(cls, provider):
            return object()


    web3_stub.Web3 = _Web3Shim
    __import__("sys").modules["web3"] = web3_stub




def test_hash_file_streams_in_chunks(tmp_path, monkeypatch):
    # Patch the blake3 import in file_hasher module
    class _FakeBlake3Ctx:
        def __init__(self):
            self._buf = bytearray()

        def update(self, b: bytes):
            self._buf.extend(b)

        def hexdigest(self):
            return "HEX(" + self._buf.decode("utf-8", errors="ignore") + ")"

    monkeypatch.setattr(fh, "blake3", lambda: _FakeBlake3Ctx(), raising=True)
    monkeypatch.setattr(fh, "BLOCK_SIZE", 4, raising=True)
    filep = tmp_path / "chunked.txt"
    filep.write_text("abcdefghij")  # 10 bytes; with BLOCK_SIZE=4 → 3 reads
    hexed = fh.hash_file(str(filep))
    assert hexed == "HEX(abcdefghij)"



def test_hash_file_empty(tmp_path, monkeypatch):
    class _FakeBlake3Ctx:
        def __init__(self):
            self._buf = bytearray()

        def update(self, b: bytes):
            self._buf.extend(b)

        def hexdigest(self):
            return "HEX(" + self._buf.decode("utf-8", errors="ignore") + ")"

    monkeypatch.setattr(fh, "blake3", lambda: _FakeBlake3Ctx(), raising=True)
    filep = tmp_path / "empty.bin"
    filep.write_bytes(b"")
    assert fh.hash_file(str(filep)) == "HEX()"



# -------------------------
# get_existing_hashes_from_csv tests
# -------------------------
def test_get_existing_hashes_from_csv_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(tmp_path / "no.csv"), raising=True)
    d = fh.get_existing_hashes_from_csv()
    assert d == {}



def test_get_existing_hashes_from_csv_reads(tmp_path, monkeypatch):
    out = tmp_path / "out.csv"
    out.write_text(
        "Filename,Hash,Record ID\n"
        "a.txt,H1,1\n"
        "b.pdf,H2,2\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(out), raising=True)
    d = fh.get_existing_hashes_from_csv()
    assert d == {"a.txt": "H1", "b.pdf": "H2"}



# -------------------------
# write_csv tests
# -------------------------
def test_write_csv_happy(tmp_path, monkeypatch):
    out = tmp_path / "out.csv"
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(out), raising=True)


    rows = [
        ("a.txt", "H1", 1),
        ("b.pdf", "H2", 2),
    ]
    fh.write_csv(rows)
    assert out.exists()


    with out.open("r", encoding="utf-8") as f:
        rdr = list(csv.reader(f))
    # write_csv writes 3 columns: Filename, Hash, Record ID
    assert rdr[0] == ["Filename", "Hash", "Record ID"]
    assert rdr[1] == ["a.txt", "H1", "1"]
    assert rdr[2] == ["b.pdf", "H2", "2"]



def test_write_csv_prints_on_error(tmp_path, monkeypatch, capsys):
    out = tmp_path / "x.csv"
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(out), raising=True)


    import builtins
    real_open = builtins.open


    def boom_open(file, *args, **kwargs):
        if file == str(out):
            raise OSError("disk full")
        return real_open(file, *args, **kwargs)


    monkeypatch.setattr(builtins, "open", boom_open, raising=True)


    fh.write_csv([("a.txt", "H1", 1)])
    assert "Error writing CSV: disk full" in capsys.readouterr().out



# -------------------------
# process_folder_once tests
# -------------------------
def _setup_input_dir(tmp_path, files):
    """Create files dict: {filename: bytes} inside tmp INPUT_DIR."""
    d = tmp_path / "files"
    d.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        p = d / name
        p.write_bytes(data if isinstance(data, (bytes, bytearray)) else str(data).encode())
    return d



def test_process_folder_once_no_new_files(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fh, "INPUT_DIR", str(tmp_path / "files"), raising=True)
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(tmp_path / "out.csv"), raising=True)


    out = pathlib.Path(fh.OUTPUT_FILE)
    out.write_text("Filename,Hash,Record ID\nold.txt,HX,1\n", encoding="utf-8")


    _setup_input_dir(tmp_path, {"old.txt": b"data"})


    new = fh.process_folder_once()
    assert new == []
    assert "No new files found" in capsys.readouterr().out



def test_process_folder_once_adds_new_files_and_updates_db_csv(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fh, "INPUT_DIR", str(tmp_path / "files"), raising=True)
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(tmp_path / "out.csv"), raising=True)


    out = pathlib.Path(fh.OUTPUT_FILE)
    out.write_text("Filename,Hash,Record ID\na.txt,H1,1\n", encoding="utf-8")


    input_dir = _setup_input_dir(tmp_path, {"a.txt": b"A", "b.txt": b"B"})


    calls = {"upsert": None, "write_csv": None, "store": []}


    def fake_store_record(fpath):
        rid = 99
        digest = "ON_CHAIN_DIGEST"
        tx = "0xDEADBEEF"
        calls["store"].append((fpath, rid, digest, tx))
        return (rid, digest, tx)


    def fake_upsert_hashes(data):
        calls["upsert"] = list(data)


    def fake_write_csv(data):
        calls["write_csv"] = list(data)


    monkeypatch.setattr(fh, "store_record", fake_store_record, raising=True)
    monkeypatch.setattr(fh, "upsert_hashes", fake_upsert_hashes, raising=True)
    monkeypatch.setattr(fh, "write_csv", fake_write_csv, raising=True)


    new = fh.process_folder_once()


    assert new == [("b.txt", "ON_CHAIN_DIGEST", 99)]
    out_text = capsys.readouterr().out
    assert "New file hashed: b.txt" in out_text
    assert "Added 1 new file(s)." in out_text


    full_b = str(pathlib.Path(input_dir) / "b.txt")
    assert calls["store"][0][0] == full_b
    assert calls["upsert"] == [("b.txt", "ON_CHAIN_DIGEST", 99)]
    # get_existing_hashes_from_csv returns dict {filename: hash}, so when combined with new_data
    # the all_data will contain 2-tuples for existing and 3-tuples for new entries
    assert calls["write_csv"][0] == ("a.txt", "H1")
    assert calls["write_csv"][1] == ("b.txt", "ON_CHAIN_DIGEST", 99)



def test_process_folder_once_ignores_dirs(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fh, "INPUT_DIR", str(tmp_path / "files"), raising=True)
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(tmp_path / "out.csv"), raising=True)
    pathlib.Path(fh.OUTPUT_FILE).write_text("Filename,Hash,Record ID\n", encoding="utf-8")


    d = _setup_input_dir(tmp_path, {"keep.txt": "ok"})
    (d / "subdir").mkdir()


    monkeypatch.setattr(fh, "store_record", lambda f: (1, "D", "0x"), raising=True)
    monkeypatch.setattr(fh, "upsert_hashes", lambda data: None, raising=True)
    monkeypatch.setattr(fh, "write_csv", lambda data: None, raising=True)


    new = fh.process_folder_once()
    assert new == [("keep.txt", "D", 1)]
    assert "New file hashed: keep.txt" in capsys.readouterr().out



def test_process_folder_once_prints_error_when_hash_raises(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fh, "INPUT_DIR", str(tmp_path / "files"), raising=True)
    monkeypatch.setattr(fh, "OUTPUT_FILE", str(tmp_path / "out.csv"), raising=True)
    pathlib.Path(fh.OUTPUT_FILE).write_text("Filename,Hash,Record ID\n", encoding="utf-8")


    _setup_input_dir(tmp_path, {"bad.txt": "boom"})


    def boom(_p):
        raise RuntimeError("explode!")


    monkeypatch.setattr(fh, "hash_file", boom, raising=True)
    monkeypatch.setattr(fh, "store_record", lambda f: (0, "", ""), raising=True)
    monkeypatch.setattr(fh, "upsert_hashes", lambda data: None, raising=True)
    monkeypatch.setattr(fh, "write_csv", lambda data: None, raising=True)


    new = fh.process_folder_once()
    assert new == []
    out = capsys.readouterr().out
    assert "Error hashing bad.txt: explode!" in out