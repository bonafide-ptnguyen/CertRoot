import os, csv
from blake3 import blake3
from typing import List, Tuple
from .database import upsert_hashes
from .interact_certifier import store_record, retrieve_record, get_total_record

BLOCK_SIZE = 1024 * 1024
INPUT_DIR = "files"
OUTPUT_FILE = "output.csv"


def hash_file(filepath: str) -> str:
    """Return BLAKE3 hash of a file (streamed)."""
    h = blake3()
    with open(filepath, "rb") as f:
        while chunk := f.read(BLOCK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def get_existing_hashes_from_csv() -> dict:
    """Read CSV and return filename→hash dict."""
    if not os.path.exists(OUTPUT_FILE):
        return {}
    with open(OUTPUT_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["Filename"]: row["Hash"] for row in reader}


def write_csv(data: List[Tuple[str, str]]):
    """Write updated CSV with all known hashes."""
    try:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Filename", "Hash", "Record ID"])
            writer.writerows(data)
    except Exception as e:
        print(f"Error writing CSV: {e}")


def process_folder_once() -> List[Tuple[str, str]]:
    """
    Process only *new* files from INPUT_DIR.
    Hash them and update MongoDB and CSV.
    """
    os.makedirs(INPUT_DIR, exist_ok=True)
    existing = get_existing_hashes_from_csv()

    new_data = []
    for fname in os.listdir(INPUT_DIR):
        fpath = os.path.join(INPUT_DIR, fname)
        if os.path.isfile(fpath) and fname not in existing:
            try:
                digest = hash_file(fpath)
                # save record on blockchain - START
                new_record_Id, digest, tx_hash = store_record(fpath)
                print(f"  - Record ID :         {new_record_Id}")
                print(f"  - File hash :         {digest}")
                print(f"  - transaction hash :       {tx_hash}")
                print("------------------------------------\n")    
                # save record on blockchain - END
                new_data.append((fname, digest, new_record_Id))
                print(f"🔹 New file hashed: {fname}")
            except Exception as e:
                print(f" Error hashing {fname}: {e}")

    if new_data:
        all_data = list(existing.items()) + new_data
        write_csv(all_data)
        upsert_hashes(new_data)
        print(f"Added {len(new_data)} new file(s).")
    else:
        print(" No new files found.")

    return new_data

# def process_folder_test():
#     """
#     Process only *new* files from INPUT_DIR.
#     Hash them and update MongoDB and CSV.
#     """
#     sample_file_path = "sample_files"
#     os.makedirs(sample_file_path, exist_ok=True)

#     for fname in os.listdir(sample_file_path):
#         fpath = os.path.join(sample_file_path, fname)
#         if os.path.isfile(fpath):
#             try:
#                 digest = hash_file(fpath)
#                 print(f"New file hashed: {fname} - hash digest: {digest}\n")
#             except Exception as e:
#                 print(f" Error hashing {fname}: {e}")
