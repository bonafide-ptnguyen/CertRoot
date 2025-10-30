# pragma version ^0.4.1
# @license MIT

# --- 1. DATA STRUCTURES ---

# The HashRecord stores all necessary data for a single file hash submission.
struct HashRecord:
    # BLAKE3 hash is 64 hex characters (32 bytes). Use Bytes[32] for efficiency.
    # We will convert the 64-char string hash to Bytes[32] before storing.
    file_hash: Bytes[32]
    timestamp: uint256  # Block timestamp
    block_number: uint256 # Block number

# --- 2. STORAGE VARIABLES ---

# Mapping: Maps a sequential ID (uint256) to a HashRecord.
# This allows for unlimited records and retrieval by index.
hash_records: public(HashMap[uint256, HashRecord])

# Counter for the next record ID (also represents the total number of records).
next_record_id: uint256

# --- 3. DEPLOYMENT ---

@deploy
def __init__():
    self.next_record_id = 0

# --- 4. EXTERNAL FUNCTIONS ---

@external
def store(file_hash_bytes: Bytes[32]):
    # 1. Create the new record using blockchain context variables
    new_record: HashRecord = HashRecord(
        file_hash = file_hash_bytes,
        timestamp = block.timestamp, 
        block_number = block.number
    )
    
    # 2. Store the record at the current ID
    self.hash_records[self.next_record_id] = new_record
    
    # 3. Increment the counter for the next record
    self.next_record_id += 1


@external
@view
def retrieve(record_id: uint256) -> (Bytes[32], uint256, uint256):
    # Ensure the requested ID is valid
    assert record_id < self.next_record_id, "Record ID out of bounds"
    
    record: HashRecord = self.hash_records[record_id]
    
    # Return the file hash, block number, and block timestamp
    return record.file_hash, record.block_number, record.timestamp


@external
@view
def get_total_records() -> uint256:
    return self.next_record_id