# from vyper import compile_code
from web3 import Web3
from dotenv import load_dotenv
import os
from .encrypt_key import KEYSTORE_PATH
import getpass
from eth_account import Account
from .json_utils import get_config

# RPC_URL=os.getenv("RPC_URL")
# MY_ADDRESS=os.getenv("MY_ADDRESS")

# if MY_ADDRESS is None or RPC_URL is None:
#     # A safer approach would be to raise an exception if any required variable is missing
#     raise EnvironmentError("Missing required environment variables (RPC_URL or MY_ADDRESS).")

# w3 = Web3(Web3.HTTPProvider(RPC_URL))

# # Convert and store the checksum address
# MY_ADDRESS_CS = w3.to_checksum_address(MY_ADDRESS)

def hex_to_bytes32(hex_hash: str) -> bytes:
    """Converts a 64-character hexadecimal string hash to a 32-byte byte string."""
    if len(hex_hash) != 64:
        raise ValueError("Hash must be a 64-character hex string.")
    return bytes.fromhex(hex_hash)

def bytes32_to_hex(hash_bytes: bytes) -> str:
    """Converts a 32-byte hash (Python 'bytes') back into its 64-character hexadecimal string."""
    if len(hash_bytes) != 32:
        raise ValueError("Input must be a 32-byte string.")
    return hash_bytes.hex()

def connect_contract():
    rpc_url, wallet_address, abi, contract_address = get_config("file_certifier.json")

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    contract_instance = w3.eth.contract(address=contract_address, abi=abi)

    return contract_instance

def retrieve_record(recordId):
    contract_instance = connect_contract()

    # latest record
    hash_retrieved_bytes, block_num, timestamp = contract_instance.functions.retrieve(recordId).call()

    # Convert retrieved bytes back to the readable hex string
    hash_retrieved_hex = bytes32_to_hex(hash_retrieved_bytes)
    # breakpoint()

    return hash_retrieved_hex, block_num, timestamp

def store_record(singleFilePath):
    contract_instance = connect_contract()

    # lazy import to avoid circular import between core modules
    from .file_hasher import hash_file
    digest = hash_file(singleFilePath)

    # Convert hash for contract
    hash_bytes32 = hex_to_bytes32(digest)

    # --- STORE HASH ---
    # This executes the state-changing transaction
    tx_hash = contract_instance.functions.store(hash_bytes32).transact()
    new_record_Id = contract_instance.functions.get_total_records().call() - 1

    return new_record_Id, digest, tx_hash

def decrypt_key() -> str:
    with open(KEYSTORE_PATH, "r") as fp:
        encrypted_account = fp.read()
        password = getpass.getpass("Enter your password: ")
        key = Account.decrypt(encrypted_account, password)
        print("Decrypted key!")

        # Convert the key object to a hexadecimal string to satisfy the -> str annotation
        # The .hex() method provides the string format needed for signing.
        return key.hex()

def get_total_record():
    contract_instance = connect_contract()
    return contract_instance.functions.get_total_records().call()
