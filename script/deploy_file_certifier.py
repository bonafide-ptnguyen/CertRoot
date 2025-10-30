import sys
import os
from moccasin.boa_tools import VyperContract
from moccasin.config import get_active_network

# Assuming your compiled FileCertifier contract is available via 'src'
# The source of the contract (FileCertifier.vy) must be available in your project.
try:
    # NOTE: You may need to change 'file_certifier' based on how your Vyper files are compiled
    from src import file_certifier 
except ImportError:
    print("Error: Could not import compiled 'file_certifier' contract. Ensure FileCertifier.vy is compiled in 'src'.")
    sys.exit(1)

# --- External Utility Import (DISABLED) ---
# The import block below is commented out to hardcode the hash and bypass the ModuleNotFoundError.
# try:
#     from script.utils.hash_utility import hash_file
# except ImportError:
#     # Fallback/Error handling if the utility script import fails
#     print("Error: Could not import hash_file utility. Check your script.utils import path.")
#     sys.exit(1)
# -----------------------------------------------------------


# --- Configuration ---
FILE_TO_CERTIFY = "inputs/frog.jpg"
TEST_HASH1 = "56b7930836a2b45e8d52db5ff60951f9a25044b4a9b526b8ad118f94b259c4fe" # 64-char hex BLAKE3 hash
TEST_HASH2 = "a1a81972fa6c39438a1179b7a777a1da572b6e3782349848d445af6bfdfb2a14"
TEST_HASH3 = "56b7930836a2b45e8d52db5ff60951f9a25044b4a9b526b8ad118f94b259c4fe"
TEST_HASH4 = "427e934190ed968ecbaeebdd0865d05c5d98a1fe187f360b35587e33cdf511d1"
TEST_HASH5 = "04c194692dc41d0073a40603d8fac31e0d93482927874c86e6d455413f28bade"
TEST_HASH6 = "8567d32ba227b413aeeae8f5437a6995f61c31e68821cd5ef058f049497a6ac5"

def hex_to_bytes32(hex_hash: str) -> bytes:
    """
    Converts a 64-character hexadecimal string hash to a 32-byte byte string.
    This is required for the Bytes[32] type in the Vyper contract.
    """
    if len(hex_hash) != 64:
        raise ValueError("Hash must be a 64-character hex string.")
    return bytes.fromhex(hex_hash)


def deploy_certifier() -> VyperContract:
    active_network = get_active_network()
    print("Currently on network:", active_network.name)
    
    # --- HARDCODED HASH INJECTION ---
    # We skip file existence checks and utility calls and use the TEST_HASH directly.
    file_hash_hex = TEST_HASH1
    file_hash_hex2 = TEST_HASH2
    file_hash_hex3 = TEST_HASH3
    file_hash_hex4 = TEST_HASH4
    file_hash_hex5 = TEST_HASH5
    file_hash_hex6 = TEST_HASH6
    print(f"Using hardcoded BLAKE3 Hash (Hex): {file_hash_hex}")
    
    # 2. Convert the 64-char hex string to the 32-byte format required by Vyper
    hash_bytes32 = hex_to_bytes32(file_hash_hex)
    hash_bytes32_2 = hex_to_bytes32(file_hash_hex2)
    hash_bytes32_3 = hex_to_bytes32(file_hash_hex3)
    hash_bytes32_4 = hex_to_bytes32(file_hash_hex4)
    hash_bytes32_5 = hex_to_bytes32(file_hash_hex5)
    hash_bytes32_6 = hex_to_bytes32(file_hash_hex6)
    print(f"Hash (Bytes[32]): {hash_bytes32.hex()}...")

    # --- Deploy the Contract ---
    certifier_contract: VyperContract = file_certifier.deploy()
    print("Contract deployed successfully.")
    
    # --- Store the Hash ---
    print(f"\n--- Storing Record ID: 0 ---")
    
    # The store function is called with the Bytes[32] hash
    certifier_contract.store(hash_bytes32)
    certifier_contract.store(hash_bytes32_2)
    certifier_contract.store(hash_bytes32_3)
    certifier_contract.store(hash_bytes32_4)
    certifier_contract.store(hash_bytes32_5)
    certifier_contract.store(hash_bytes32_6)
    
    print(f"Total records after store:", certifier_contract.get_total_records())

    # --- Retrieve the Record 1 ---
    record_id_to_retrieve = 0
    print(f"\n--- Retrieving Record ID: {record_id_to_retrieve} ---")
    
    # The retrieve function returns a tuple (Bytes[32], uint256, uint256)
    hash_retrieved, block_num, timestamp = certifier_contract.retrieve(record_id_to_retrieve)
    
    print("Verification Record:")
    print(f"  - Hash (Hex):         {hash_retrieved.hex()}")
    print(f"  - Block Number:       {block_num}")
    print(f"  - Block Timestamp:    {timestamp}")

    if hash_retrieved.hex() == file_hash_hex:
        print("\nVerification SUCCESS: Retrieved hash matches stored hash!")
    else:
        print("\nVerification FAILED: Hashes do not match.")

    # --- Retrieve the Record 4 ---
    record_id_to_retrieve = 3
    print(f"\n--- Retrieving Record ID: {record_id_to_retrieve} ---")
    
    # The retrieve function returns a tuple (Bytes[32], uint256, uint256)
    hash_retrieved, block_num, timestamp = certifier_contract.retrieve(record_id_to_retrieve)
    
    print("Verification Record:")
    print(f"  - Hash (Hex):         {hash_retrieved.hex()}")
    print(f"  - Block Number:       {block_num}")
    print(f"  - Block Timestamp:    {timestamp}")

    if hash_retrieved.hex() == file_hash_hex4:
        print("\nVerification SUCCESS: Retrieved hash matches stored hash!")
    else:
        print("\nVerification FAILED: Hashes do not match.")

    # # Boilerplate verification for Moccasin/Explorer
    # if active_network.has_explorer():
    #     print("Verifying contract on explorer...")
    #     result = active_network.moccasin_verify(certifier_contract)
    #     result.wait_for_verification()
    
    return certifier_contract


def moccasin_main() -> VyperContract:
    """The main entry point for the 'mox run' command."""
    return deploy_certifier()
