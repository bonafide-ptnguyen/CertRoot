import types
import json
import pytest
from backend.core import interact_certifier as ic
from backend.core import file_hasher as fh_module


class _CallObj:
    def __init__(self, value):
        self._value = value


    def call(self):
        return self._value


    def transact(self):
        return self._value



class _Functions:
    """Holds closures for retrieve/store/get_total_records, each returning a *_CallObj."""
    def __init__(self, retrieve_value=None, total_records=0, store_value="0xTX"):
        self._retrieve_value = retrieve_value
        self._total_records = total_records
        self._store_value = store_value


    def retrieve(self, record_id):
        return _CallObj(self._retrieve_value)


    def get_total_records(self):
        return _CallObj(self._total_records)


    def store(self, hash_bytes32):
        return _CallObj(self._store_value)



class _Eth:
    def __init__(self, contract_instance):
        self._contract_instance = contract_instance


    def contract(self, address=None, abi=None):
        return self._contract_instance



class FakeContract:
    def __init__(self, functions: _Functions):
        self.functions = functions



class FakeWeb3:
    def __init__(self, contract_instance):
        self.eth = _Eth(contract_instance)


    class HTTPProvider:
        def __init__(self, url):
            self.url = url



# -------------------------- hex<->bytes32 utilities --------------------------
def test_hex_to_bytes32_ok_roundtrip():
    hex64 = "ab" * 32
    b = ic.hex_to_bytes32(hex64)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) == 32
    assert ic.bytes32_to_hex(b) == hex64



def test_hex_to_bytes32_bad_length_raises():
    with pytest.raises(ValueError):
        ic.hex_to_bytes32("ab" * 31)  # 62 chars



def test_bytes32_to_hex_bad_length_raises():
    with pytest.raises(ValueError):
        ic.bytes32_to_hex(b"\x00" * 31)



# ------------------------------- connect_contract ----------------------------
def test_connect_contract_builds_contract(monkeypatch):
    config = ("http://rpc.test", "0xMY", [{"type": "function"}], "0xCONTRACT")
    monkeypatch.setattr(ic, "get_config", lambda fname: config, raising=True)


    functions = _Functions(total_records=5)
    contract_instance = FakeContract(functions)
    fake_w3 = FakeWeb3(contract_instance)


    class _W3Shim:
        HTTPProvider = FakeWeb3.HTTPProvider


        def __new__(cls, provider):
            return fake_w3


    monkeypatch.setattr(ic, "Web3", _W3Shim, raising=True)


    contract = ic.connect_contract()


    assert isinstance(contract, FakeContract)
    assert contract.functions.get_total_records().call() == 5



# -------------------------------- retrieve_record ----------------------------
def test_retrieve_record_converts_bytes_to_hex(monkeypatch):
    hash_bytes = bytes.fromhex("12" * 32)
    block_num = 123
    timestamp = "2025-10-31T00:00:00Z"


    fns = _Functions(retrieve_value=(hash_bytes, block_num, timestamp), total_records=10)
    contract = FakeContract(fns)
    monkeypatch.setattr(ic, "connect_contract", lambda: contract, raising=True)


    hex_hash, bnum, ts = ic.retrieve_record(3)


    assert hex_hash == "12" * 32
    assert bnum == 123
    assert ts == "2025-10-31T00:00:00Z"



def test_retrieve_record_raises_on_bad_bytes(monkeypatch):
    bad_bytes = b"\x00" * 31
    fns = _Functions(retrieve_value=(bad_bytes, 1, "T"), total_records=1)
    contract = FakeContract(fns)
    monkeypatch.setattr(ic, "connect_contract", lambda: contract, raising=True)


    with pytest.raises(ValueError):
        ic.retrieve_record(0)



# --------------------------------- store_record -------------------------------
def test_store_record_happy_path(monkeypatch):
    digest = "ab" * 32
    calls = {"store_called": False, "stored_bytes": None}


    def fake_hash_file(path):
        assert str(path).endswith("docs/report.txt")
        return digest


    # Monkeypatch hash_file in the file_hasher module
    monkeypatch.setattr(fh_module, "hash_file", fake_hash_file, raising=True)


    def _store_check(got_bytes):
        calls["store_called"] = True
        calls["stored_bytes"] = got_bytes
        return _CallObj("0xTXHASH")


    fns = _Functions(total_records=10)
    fns.store = _store_check
    contract = FakeContract(fns)


    monkeypatch.setattr(ic, "connect_contract", lambda: contract, raising=True)
    monkeypatch.setattr(ic, "hex_to_bytes32", lambda h: bytes.fromhex(h), raising=True)


    new_id, out_digest, tx_hash = ic.store_record("docs/report.txt")


    assert new_id == 9
    assert out_digest == digest
    assert tx_hash == "0xTXHASH"
    assert calls["store_called"] is True
    assert len(calls["stored_bytes"]) == 32
    assert calls["stored_bytes"].hex() == digest



def test_store_record_bad_digest_raises(monkeypatch):
    def fake_hash_file(p):
        return "abcd"

    # Monkeypatch hash_file in the file_hasher module
    monkeypatch.setattr(fh_module, "hash_file", fake_hash_file, raising=True)


    fns = _Functions(total_records=2)
    contract = FakeContract(fns)
    monkeypatch.setattr(ic, "connect_contract", lambda: contract, raising=True)
    monkeypatch.setattr(ic, "hex_to_bytes32", ic.hex_to_bytes32, raising=True)


    with pytest.raises(ValueError):
        ic.store_record("file.bin")



# ---------------------------------- decrypt_key -------------------------------
def test_decrypt_key_happy(monkeypatch, tmp_path, capsys):
    keystore_text = json.dumps({"address": "0xabc"})
    target = tmp_path / "keystore.json"
    target.write_text(keystore_text, encoding="utf-8")


    monkeypatch.setattr(ic, "KEYSTORE_PATH", target, raising=True)
    monkeypatch.setattr(ic.getpass, "getpass", lambda prompt="": "pw", raising=True)


    class FakeAcct:
        @staticmethod
        def decrypt(enc, pw):
            assert enc == keystore_text
            assert pw == "pw"
            return b"\x01\x02\xff"


    monkeypatch.setattr(ic, "Account", FakeAcct, raising=True)


    hex_key = ic.decrypt_key()
    out = capsys.readouterr().out
    assert hex_key == "0102ff"
    assert "Decrypted key!" in out



# -------------------------------- get_total_record ---------------------------
def test_get_total_record_calls_contract(monkeypatch):
    fns = _Functions(total_records=42)
    contract = FakeContract(fns)
    monkeypatch.setattr(ic, "connect_contract", lambda: contract, raising=True)


    assert ic.get_total_record() == 42
