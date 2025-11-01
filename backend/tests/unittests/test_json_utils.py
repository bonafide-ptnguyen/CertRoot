import json
import pathlib
import pytest

from backend.core import json_utils as ju  


def _repoint_module_file(monkeypatch, base_dir: pathlib.Path):
    """Force json_utils.get_config_path to use a temporary base path."""
    fake_core = base_dir / "core"
    fake_core.mkdir(parents=True, exist_ok=True)
    fake_json_utils_py = fake_core / "json_utils.py"
    fake_json_utils_py.write_text("# placeholder", encoding="utf-8")
    monkeypatch.setattr(ju, "__file__", str(fake_json_utils_py), raising=True)


# ----------------------- get_config_path tests -----------------------
def test_get_config_path_points_to_configs_folder(tmp_path, monkeypatch):
    _repoint_module_file(monkeypatch, tmp_path)

    cfg_path = ju.get_config_path("file_certifier.json")
    cfg = pathlib.Path(cfg_path)

    assert cfg.is_absolute()
    assert cfg.name == "file_certifier.json"
    assert cfg.parent.name == "configs"
    assert cfg.parent.parent.resolve() == tmp_path.resolve()


# ----------------------- load_hash_config tests ----------------------
def test_load_hash_config_happy(tmp_path):
    cfg = tmp_path / "ok.json"
    data = {"a": 1, "b": "x"}
    cfg.write_text(json.dumps(data), encoding="utf-8")

    got = ju.load_hash_config(str(cfg))
    assert got == data


def test_load_hash_config_file_missing_exits(tmp_path, capsys):
    missing = tmp_path / "nope.json"
    with pytest.raises(SystemExit) as ei:
        ju.load_hash_config(str(missing))
    assert ei.value.code == 1
    err = capsys.readouterr().err
    assert "Configuration file not found" in err
    assert str(missing) in err


def test_load_hash_config_bad_json_exits(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{not: json", encoding="utf-8")
    with pytest.raises(SystemExit) as ei:
        ju.load_hash_config(str(bad))
    assert ei.value.code == 1
    err = capsys.readouterr().err
    assert "Failed to parse JSON file" in err
    assert str(bad) in err


# --------------------------- get_config tests -------------------------
def test_get_config_happy_prints_and_returns_tuple(tmp_path, monkeypatch, capsys):
    _repoint_module_file(monkeypatch, tmp_path)

    configs_dir = tmp_path / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    cfg = configs_dir / "file_certifier.json"
    expected = {
        "RPC_URL": "http://rpc.local",
        "wallet_address": "0xABC",
        "abi": [{"type": "function", "name": "f"}],
        "contract_address": "0xDEAD",
    }
    cfg.write_text(json.dumps(expected), encoding="utf-8")

    rpc_url, wallet, abi, contract_addr = ju.get_config("file_certifier.json")

    assert rpc_url == expected["RPC_URL"]
    assert wallet == expected["wallet_address"]
    assert abi == expected["abi"]
    assert contract_addr == expected["contract_address"]

    out = capsys.readouterr().out
    assert "--- JSON Configuration Loader ---" in out
    assert "Attempting to load config from:" in out

    printed_path = out.split("Attempting to load config from: ", 1)[1].strip().splitlines()[0]
    assert pathlib.Path(printed_path).resolve() == cfg.resolve()


def test_get_config_missing_key_raises(tmp_path, monkeypatch):
    _repoint_module_file(monkeypatch, tmp_path)

    configs_dir = tmp_path / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    cfg = configs_dir / "file_certifier.json"

    base = {
        "RPC_URL": "http://x",
        "wallet_address": "0xW",
        "abi": [],
        "contract_address": "0xC",
    }
    for missing in ["RPC_URL", "wallet_address", "abi", "contract_address"]:
        data = dict(base)
        data.pop(missing)
        cfg.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(EnvironmentError):
            ju.get_config("file_certifier.json")
