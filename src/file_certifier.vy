# pragma version ^0.4.1
# @license MIT

# --- 1. DATA STRUCTURES ---
struct HashRecord:
    file_hash: Bytes[32]
    timestamp: uint256
    block_number: uint256

# --- 2. STORAGE VARIABLES ---

# PRIMARY STORAGE: Stores records sequentially using cheap uint256 IDs.
# Retrieval by hash will now be handled off-chain (in Python).
hash_records: public(HashMap[uint256, HashRecord])
next_record_id: uint256 # Counter for the next record ID

# --- 3. DEPLOYMENT ---
@deploy
def __init__():
    self.next_record_id = 0

# --- 4. EXTERNAL FUNCTIONS ---

@external
def store(file_hash_bytes: Bytes[32]) -> (uint256, Bytes[32], uint256, uint256):
    """
    Stores a file hash along with the current block details.
    
    NOTE: Duplicate hash check is removed to keep gas cost minimal.
    It is recommended to handle duplicate checks off-chain.
    """
    # 1. Create the new record using blockchain context variables
    new_record: HashRecord = HashRecord(
        file_hash = file_hash_bytes,
        timestamp = block.timestamp, 
        block_number = block.number
    )
    
    # 2. Store the record at the sequential ID (single state change)
    self.hash_records[self.next_record_id] = new_record
    
    # 3. record block ID
    record_id: uint256 = self.next_record_id

    # 4. Increment the counter for the next record
    self.next_record_id += 1

    return record_id, new_record.file_hash, new_record.block_number, new_record.timestamp

@external
@view
def retrieve(record_id: uint256) -> (Bytes[32], uint256, uint256):
    """
    Retrieves the details of a single hash record by its sequential ID.
    
    This is the ONLY way to retrieve a record from the contract's storage.
    """
    # Check 1: Ensure the requested ID is within the bounds of records created
    assert record_id < self.next_record_id, "Record ID out of bounds"
    
    record: HashRecord = self.hash_records[record_id]
    
    # # Check 2: Verify the hash field is not zero (meaning the record was actually stored)
    # assert record.file_hash != empty(Bytes[32]), "Record Not Found"

    # Return the file hash, block number, and block timestamp
    return record.file_hash, record.block_number, record.timestamp


@external
@view
def get_total_records() -> uint256:
    """Returns the total number of hashes stored."""
    return self.next_record_id
