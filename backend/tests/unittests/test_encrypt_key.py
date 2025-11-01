
import json
import pathlib
import pytest
from backend.core import encrypt_key as mod


def test_main_happy_path(monkeypatch, tmp_path, capsys):
    """Happy path: prompts → from_key → encrypt → JSON written to KEYSTORE_PATH."""
    target = tmp_path / "keystore.json"
    monkeypatch.setattr(mod, "KEYSTORE_PATH", target, raising=True)

    # Fake getpass to return private key then password
    inputs = iter(["0xdeadbeefcafebabe", "super-secret-pass"])
    monkeypatch.setattr(
        mod.getpass, "getpass",
        lambda prompt="": next(inputs),
        raising=True,
    )


    class FakeAcct:
        def __init__(self, pk): self.pk = pk
        def encrypt(self, pw):
            return {"address": "0xAbC", "crypto": {"cipher": "aes-128-ctr"}, "meta": {"pw": pw, "pk": self.pk}}

    monkeypatch.setattr(mod.Account, "from_key", lambda pk: FakeAcct(pk), raising=True)

    mod.main()

    out = capsys.readouterr().out
    assert "Saving to" in out and str(target) in out
    assert target.exists()

    data = json.loads(target.read_text())
    assert data["address"] == "0xAbC"
    assert data["crypto"]["cipher"] == "aes-128-ctr"
    assert data["meta"]["pw"] == "super-secret-pass"
    assert data["meta"]["pk"] == "0xdeadbeefcafebabe"


def test_main_raises_on_bad_private_key(monkeypatch, tmp_path):
    monkeypatch.setattr(mod, "KEYSTORE_PATH", tmp_path / "k.json", raising=True)
    monkeypatch.setattr(mod.getpass, "getpass", lambda prompt="": "not-a-valid-key", raising=True)
    monkeypatch.setattr(mod.Account, "from_key", lambda _: (_ for _ in ()).throw(ValueError("invalid key")), raising=True)

    with pytest.raises(ValueError):
        mod.main()


def test_main_raises_when_write_fails(monkeypatch, tmp_path):
    target = tmp_path / "k.json"
    monkeypatch.setattr(mod, "KEYSTORE_PATH", target, raising=True)

    seq = iter(["0xdead", "pw"])
    monkeypatch.setattr(mod.getpass, "getpass", lambda prompt="": next(seq), raising=True)

    class FakeAcct:
        def encrypt(self, pw): return {"ok": True, "pw": pw}
    monkeypatch.setattr(mod.Account, "from_key", lambda _pk: FakeAcct(), raising=True)

    real_open = pathlib.Path.open

    def fake_open(self, *args, **kwargs):
        if self == target:
            raise OSError("disk full")
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "open", fake_open, raising=True)

    with pytest.raises(OSError):
        mod.main()
