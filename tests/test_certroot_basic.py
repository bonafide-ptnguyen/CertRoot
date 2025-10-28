import re
import hashlib
from certroot import hello
from certroot.hashing import sha256_hex
from certroot.blockchain import link_cert_to_chain

# ---------- hello() ----------
def test_hello_default_message():
    assert hello() == "Hello, world!"

def test_hello_custom_name():
    assert hello("CertRoot") == "Hello, CertRoot!"

def test_hello_type():
    result = hello("Tester")
    assert isinstance(result, str)
    assert "Tester" in result

# ---------- sha256_hex() ----------
def test_sha256_known_vector():
    assert sha256_hex(b"abc") == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )

def test_sha256_empty_string():
    assert sha256_hex(b"") == hashlib.sha256(b"").hexdigest()

def test_sha256_hex_format():
    out = sha256_hex(b"123")
    assert re.fullmatch(r"[0-9a-f]{64}", out)

# ---------- link_cert_to_chain() ----------
def test_link_cert_to_chain_format():
    txid = link_cert_to_chain("ABC123")
    assert txid.startswith("txid-for-")
    assert txid.endswith("ABC123")

def test_link_cert_to_chain_multiple_ids():
    t1 = link_cert_to_chain("A")
    t2 = link_cert_to_chain("B")
    assert t1 != t2
    assert t1.startswith("txid-for-")
    assert t2.startswith("txid-for-")
