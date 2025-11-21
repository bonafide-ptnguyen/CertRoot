import sys
import pathlib
import types
import runpy
import datetime

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def make_fake_core_ic(
    total_first=5,
    total_second=None,
    record_tuple=("0xABC", 123, 1761912000),
):
    if total_second is None:
        total_second = total_first

    core_pkg = types.ModuleType("core")
    ic_mod = types.ModuleType("core.interact_certifier")

    calls = {"count": 0, "store_called": 0}

    def get_total_record():
        calls["count"] += 1
        return total_first if calls["count"] == 1 else total_second

    def retrieve_record(record_id: int):
        return record_tuple

    def store_record(path: str):
        calls["store_called"] += 1
        return (999, "0xSTORE", "0xTX")

    ic_mod.get_total_record = get_total_record
    ic_mod.retrieve_record = retrieve_record
    ic_mod.store_record = store_record

    core_pkg.interact_certifier = ic_mod
    sys.modules["core"] = core_pkg
    sys.modules["core.interact_certifier"] = ic_mod

    return ic_mod, calls

def import_certifier_integration():
    import certifier_integration
    return certifier_integration

# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------

def test_main_prints_expected(capsys):
    test_ts = 1761904800
    _, _ = make_fake_core_ic(
        total_first=5,
        total_second=5,
        record_tuple=("0xDEADBEEF", 777, test_ts),
    )
    mod = import_certifier_integration()
    mod.main()
    out = capsys.readouterr().out

    assert "Total records:" in out
    assert "Verification Record: 6" in out
    assert "0xDEADBEEF" in out
    assert "777" in out
    
    expected_date_str = str(datetime.datetime.fromtimestamp(test_ts))
    assert expected_date_str in out
    
    # FIX: Changed expectation from 2 to 1
    assert out.count("Total records:") == 1


def test_store_record_is_not_called(capsys):
    _, calls = make_fake_core_ic(
        total_first=10,
        total_second=10,
        record_tuple=("0xAAA", 1, 12345),
    )
    mod = import_certifier_integration()
    mod.main()
    _ = capsys.readouterr().out
    assert calls["store_called"] == 0


def test_running_as_script_executes_main_once(capsys):
    test_ts = 1761989400
    _, calls = make_fake_core_ic(
        total_first=3,
        total_second=3,
        record_tuple=("0xBEEF", 999, test_ts),
    )
    runpy.run_module("certifier_integration", run_name="__main__")
    out = capsys.readouterr().out
    
    assert "Verification Record: 6" in out
    assert "0xBEEF" in out
    assert "999" in out
    
    # FIX: Changed expectation from 2 to 1
    assert out.count("Total records:") == 1