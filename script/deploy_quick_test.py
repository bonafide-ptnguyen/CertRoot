import sys
import os
import glob
from moccasin.boa_tools import VyperContract
from moccasin.config import get_active_network

# --- FIX: INVALIDATE STALE ARTIFACTS IN PYTHON MEMORY ---
# The Moccasin/Anvil runner often keeps the old compiled contract module in memory (sys.modules),
# causing the runner to use stale function selectors (leading to the .0xb374012b error).
# We force a reload/re-import of the contract artifact.
if 'src.file_certifier' in sys.modules:
    del sys.modules['src.file_certifier']

try:
    # Assuming 'file_certifier' is the name of the compiled Vyper module
    from src import file_certifier 
except ImportError:
    print("Error: Could not import compiled 'file_certifier' contract. Ensure FileCertifier.vy is compiled in 'src'.")
    sys.exit(1)
# --- END FIX ---


# --- MOX PATH FIX: Dynamically Injecting Paths ---
# This block ensures 'blake3' and your local modules are visible to 'mox run'.

# 1. Grab the path of the active virtual environment using the VIRTUAL_ENV environment variable.
VENV_BASE = os.environ.get('VIRTUAL_ENV')

# Initialize path variables
MISSING_VENV_PATH = None
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

if VENV_BASE:
    # 2. Determine the site-packages path dynamically.
    lib_path_search = os.path.join(VENV_BASE, 'lib', 'python*', 'site-packages')
    lib64_path_search = os.path.join(VENV_BASE, 'lib64', 'python*', 'site-packages')
    
    site_packages_paths = glob.glob(lib_path_search) + glob.glob(lib64_path_search)
    
    if site_packages_paths:
        MISSING_VENV_PATH = site_packages_paths[0]
    
    # If the dynamic search failed, we check if the path is still None
    if MISSING_VENV_PATH is None:
        print("\n--- FATAL ENVIRONMENT ERROR ---")
        print("Could not automatically locate 'site-packages' within the VIRTUAL_ENV path.")
        print(f"VENV Base Path: {VENV_BASE}")
        sys.exit(1)
        
else:
    # --- EXIT IF VIRTUAL_ENV IS NOT SET ---
    print("\n--- FATAL ENVIRONMENT ERROR ---")
    print("VIRTUAL_ENV environment variable is not set.")
    print("Please ensure your Python virtual environment is activated before running 'mox run'.")
    sys.exit(1)


# --- If execution reaches here, VENV_BASE and MISSING_VENV_PATH are valid ---

# 3. Inject the VENV site-packages path to find 'blake3'
if MISSING_VENV_PATH not in sys.path:
    sys.path.insert(0, MISSING_VENV_PATH) 

# 4. Inject the project root (CertRoot) to fix local module imports
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
print("\n--- MOX RUN SYS.PATH FIX APPLIED ---")
print(f"Injected VENV Path: {MISSING_VENV_PATH}")
print(f"Injected Project Root: {PROJECT_ROOT}")
print("------------------------------------\n")


# The line below should now succeed because the required directory is in sys.path
try:
    from blake3 import blake3 
except ModuleNotFoundError:
    print("ModuleNotFoundError still occurred for 'blake3' after path injection.")
    print("Please confirm 'blake3' is installed in your active virtual environment.")
    sys.exit(1)

# Now that 'blake3' is imported, we import the hash utility using the user's preferred module name.
try:
    from script.utils.hashing_utility import hash_file
except ImportError as e:
    print("\n--- FATAL LOCAL IMPORT ERROR ---")
    print(f"Failed to import local utility file: {e}")
    print("Please confirm 'script/utils/hashing_utility.py' exists and package files (__init__.py) are present.")
    sys.exit(1)

# --- Configuration & Utility Functions ---
# FILE_TO_CERTIFY = "inputs/frog.jpg"
FILE_TO_CERTIFY = "inputs/earth.glb"

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


def deploy_certifier() -> VyperContract:
    active_network = get_active_network()
    print("Currently on network:", active_network.name)

    print(f"Attempting to hash file: {FILE_TO_CERTIFY}")
    print("-" * 30)
    
    if not os.path.exists(FILE_TO_CERTIFY):
        print(f"Error: File not found at '{FILE_TO_CERTIFY}'. Please ensure the path is correct.", file=sys.stderr)
        sys.exit(1)

    # --- Deploy the Contract ---

    # anvil
    # certifier_contract: VyperContract = file_certifier.at("0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9")

    # tenderly
    certifier_contract: VyperContract = file_certifier.at("0x8f2A07bb90F8591141242773a88969E9e88F2D6A")
    print("Contract connected successfully.")

    try:
        # 1. Generate hash
        raw_hash_result = hash_file(FILE_TO_CERTIFY)
        
        # 2. Convert hash for contract
        hash_bytes32 = hex_to_bytes32(raw_hash_result)
        
        print(f"File Hash (Hex): {raw_hash_result}")
        print(f"Contract Input (Bytes[32]): {hash_bytes32.hex()}...")

        # total record before storing file hash
        total_records = certifier_contract.get_total_records() 
        print(f"Total records before store:", total_records)

        # --- STORE HASH ---
        # This executes the state-changing transaction
        stored_record_id, stored_file_hash, stored_block_number, stored_timestamp = certifier_contract.store(hash_bytes32)
        print("Stored Record:")
        print(f"  - Record ID :         {stored_record_id}")
        print(f"  - File Hash (hex-64):       {bytes32_to_hex(stored_file_hash)}")
        print(f"  - Block Number:    {stored_block_number}")
        print(f"  - Block Timestamp:    {stored_timestamp}")

        # total record before storing file hash
        total_records = certifier_contract.get_total_records() 
        print(f"Total records after store:", total_records)

    except Exception as e:
        print(f"An error occurred during transaction or hashing: {e}", file=sys.stderr)
        sys.exit(1)

    # Get the ID of the stored record (which is 0 for the first one)
    total_records = certifier_contract.get_total_records() 
    record_id = total_records - 1 

    print(f"\nRecord stored at ID: {record_id}")
    print(f"Total records after store:", total_records)

    # latest record
    hash_retrieved_bytes, block_num, timestamp = certifier_contract.retrieve(record_id)

    # Convert retrieved bytes back to the readable hex string
    hash_retrieved_hex = bytes32_to_hex(hash_retrieved_bytes)
    
    print(f"Verification Record: {record_id}")
    print(f"  - Hash (Hex):         {hash_retrieved_hex}")
    print(f"  - Block Number:       {block_num}")
    print(f"  - Block Timestamp:    {timestamp}")

    # get the previous record
    record_id -= 1

    if (record_id >= 0):
        hash_retrieved_bytes, block_num, timestamp = certifier_contract.retrieve(record_id)

        # Convert retrieved bytes back to the readable hex string
        hash_retrieved_hex = bytes32_to_hex(hash_retrieved_bytes)
        
        print(f"Verification Record: {record_id}")
        print(f"  - Hash (Hex):         {hash_retrieved_hex}")
        print(f"  - Block Number:       {block_num}")
        print(f"  - Block Timestamp:    {timestamp}")
    
    return certifier_contract


def moccasin_main() -> VyperContract:
    """The main entry point for the 'mox run' command."""
    return deploy_certifier()
