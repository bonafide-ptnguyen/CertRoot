# --- FILE HASHING + MONGO PERSISTENCE UTILITY ---
# Reads all files in the 'input_files' directory, generates a cryptographic
# BLAKE3 hash for each (via streaming in binary mode), writes the results to
# MongoDB Atlas (filename + hashed data), and also exports a CSV.
#
# Notes:
# - BLAKE3 is used as the primary hashing algorithm for performance and security.
# - A file-type router is implemented so you can easily swap different hashing
#   libraries per file type if desired.
#
# Dependencies:
#   pip install blake3 pymongo
#
# MongoDB Atlas:
#   - Set environment variables:
#       MONGODB_URI="mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority"
#       MONGODB_DB="file_hashes_db"             # optional, default shown
#       MONGODB_COLLECTION="hashes"             # optional, default shown

import os
import csv
from typing import List, Tuple, Callable, Optional

# --- Third-party libs ---
from blake3 import blake3
from pymongo import MongoClient, UpdateOne

# --- Configuration ---
INPUT_DIR_NAME = "files"
OUTPUT_FILE_NAME = "output.csv"
BLOCK_SIZE = 1024 * 1024  # 1MB chunks for efficient reading of large files

# Mongo configuration from env
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "file_hashes_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "hashes")

# --- File type groups (by extension) ---
IMAGE_EXTS = {
    "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "svg", "ico", "heic", "heif", "raw", "nef", "cr2", "dng"
}
VIDEO_EXTS = {
    "mp4", "mov", "avi", "mkv", "webm", "wmv", "flv", "m4v", "mpg", "mpeg"
}
AUDIO_EXTS = {
    "mp3", "wav", "flac", "aac", "m4a", "ogg", "oga", "opus", "wma", "aiff", "alac"
}
DOC_EXTS = {
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp", "rtf"
}
TEXT_EXTS = {
    "txt", "csv", "tsv", "json", "yaml", "yml", "xml", "md", "log", "ini", "cfg"
}
THREED_EXTS = {
    # CAD / 3D
    "step", "stp", "iges", "igs", "stl", "obj", "fbx", "dae", "3ds", "gltf", "glb", "ply",
    "sldprt", "sldasm"
}
ARCHIVE_EXTS = {
    "zip", "rar", "7z", "tar", "gz", "bz2", "xz"
}


# --- Hashers ---
def hash_file_blake3(filepath: str) -> str:
    """Stream-hash a file with BLAKE3 to a hex digest."""
    h = blake3()
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(BLOCK_SIZE)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return "FILE_NOT_FOUND"
    except Exception as e:
        return f"ERROR: {e}"


def choose_hasher_for_file(filename: str) -> Callable[[str], str]:
    """
    Decide which hasher to use for a given file by extension.
    Currently routes all types to BLAKE3 (cryptographic, fast),
    but you can swap specific groups to other libraries if needed.
    """
    ext = os.path.splitext(filename)[1].lower().lstrip(".")

    # Examples of how you might customize later:
    # - return hash_file_image_phash for IMAGE_EXTS (perceptual hash, not cryptographic)
    # - return hash_file_blake3 for everything else (cryptographic)

    if ext in IMAGE_EXTS:
        return hash_file_blake3
    if ext in VIDEO_EXTS:
        return hash_file_blake3
    if ext in AUDIO_EXTS:
        return hash_file_blake3
    if ext in DOC_EXTS:
        return hash_file_blake3
    if ext in TEXT_EXTS:
        return hash_file_blake3
    if ext in THREED_EXTS:
        return hash_file_blake3
    if ext in ARCHIVE_EXTS:
        return hash_file_blake3

    # Default: hash anything else with BLAKE3 as well
    return hash_file_blake3


# --- Core functions ---
def calculate_file_hash(filepath: str) -> str:
    """Calculates the hash of a single file using a type-appropriate hasher."""
    filename = os.path.basename(filepath)
    hasher = choose_hasher_for_file(filename)
    return hasher(filepath)


def process_folder(input_folder: str) -> List[Tuple[str, str]]:
    """
    Iterates through all files in a folder (non-recursive) and generates their hashes.
    Returns a list of (filename, digest).
    """
    results: List[Tuple[str, str]] = []

    if not os.path.isdir(input_folder):
        print(f"Error: Input directory '{input_folder}' not found.")
        return results

    print(f"Processing files in '{input_folder}'...")

    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)

        if os.path.isfile(filepath):
            file_hash = calculate_file_hash(filepath)
            results.append((filename, file_hash))
            # Print first 12 chars to keep console tidy
            print(f"  Hashed {filename}: {file_hash[:12]}...")

    return results


def write_results_to_csv(data: List[Tuple[str, str]], output_file: str):
    """Writes the list of filenames and hashes to a CSV file."""
    try:
        with open(output_file, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Keeping the schema to two columns as requested
            writer.writerow(['Filename', 'Hash'])  # Using BLAKE3 under the hood
            writer.writerows(data)
        print(f"\nSuccessfully wrote results to '{output_file}'.")
    except Exception as e:
        print(f"Error writing to CSV: {e}")


# --- MongoDB helpers ---
def get_mongo_collection() -> Optional["MongoClient"]:
    """Connects to MongoDB Atlas and returns the collection handle, or None on failure."""
    if not MONGODB_URI:
        print("Warning: MONGODB_URI not set. Skipping MongoDB write.")
        return None

    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLLECTION]
        # Optional: ensure we upsert on filename (unique)
        collection.create_index("filename", unique=True)
        return collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None


def write_results_to_mongo(data: List[Tuple[str, str]]):
    """Upserts (filename, hash) pairs into MongoDB Atlas."""
    collection = get_mongo_collection()
    if collection is None:
        return

    try:
        ops = []
        for filename, digest in data:
            ops.append(
                UpdateOne(
                    {"filename": filename},
                    {"$set": {"filename": filename, "hash": digest}},
                    upsert=True
                )
            )
        if not ops:
            print("No MongoDB operations to perform.")
            return

        result = collection.bulk_write(ops, ordered=False)
        inserted = result.upserted_count
        modified = result.modified_count
        print(f"MongoDB write complete. Upserted: {inserted}, Modified: {modified}")
    except Exception as e:
        print(f"Error writing to MongoDB: {e}")


# --- Main ---
if __name__ == "__main__":
    # Determine absolute paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, INPUT_DIR_NAME)
    output_path = os.path.join(script_dir, OUTPUT_FILE_NAME)

    # 1. Process folder and compute hashes
    hashing_results = process_folder(input_path)

    # 2. Write results to CSV
    if hashing_results:
        write_results_to_csv(hashing_results, output_path)
    else:
        print("No files were processed.")

    # 3. Write results to MongoDB Atlas
    if hashing_results:
        write_results_to_mongo(hashing_results)