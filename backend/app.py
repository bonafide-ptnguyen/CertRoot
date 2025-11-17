# # --- FILE HASHING + MONGO PERSISTENCE UTILITY ---
# # Reads all files in the 'input_files' directory, generates a cryptographic
# # BLAKE3 hash for each (via streaming in binary mode), writes the results to
# # MongoDB Atlas (filename + hashed data), and also exports a CSV.
# #
# # Notes:
# # - BLAKE3 is used as the primary hashing algorithm for performance and security.
# # - A file-type router is implemented so you can easily swap different hashing
# #   libraries per file type if desired.
# #
# # Dependencies:
# #   pip install blake3 pymongo
# #
# # MongoDB Atlas:
# #   - Set environment variables:
# #       MONGODB_URI="mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority"
# #       MONGODB_DB="file_hashes_db"             # optional, default shown
# #       MONGODB_COLLECTION="hashes"             # optional, default shown

# import os
# import csv
# from typing import List, Tuple, Callable, Optional

# # --- Third-party libs ---
# from blake3 import blake3
# from pymongo import MongoClient, UpdateOne

# # --- Configuration ---
# INPUT_DIR_NAME = "files"
# OUTPUT_FILE_NAME = "output.csv"
# BLOCK_SIZE = 1024 * 1024  # 1MB chunks for efficient reading of large files

# # Mongo configuration from env
# MONGODB_URI = os.getenv("MONGODB_URI", "")
# MONGODB_DB = os.getenv("MONGODB_DB", "file_hashes_db")
# MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "hashes")

# # --- File type groups (by extension) ---
# IMAGE_EXTS = {
#     "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "svg", "ico", "heic", "heif", "raw", "nef", "cr2", "dng"
# }
# VIDEO_EXTS = {
#     "mp4", "mov", "avi", "mkv", "webm", "wmv", "flv", "m4v", "mpg", "mpeg"
# }
# AUDIO_EXTS = {
#     "mp3", "wav", "flac", "aac", "m4a", "ogg", "oga", "opus", "wma", "aiff", "alac"
# }
# DOC_EXTS = {
#     "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "odt", "ods", "odp", "rtf"
# }
# TEXT_EXTS = {
#     "txt", "csv", "tsv", "json", "yaml", "yml", "xml", "md", "log", "ini", "cfg"
# }
# THREED_EXTS = {
#     # CAD / 3D
#     "step", "stp", "iges", "igs", "stl", "obj", "fbx", "dae", "3ds", "gltf", "glb", "ply",
#     "sldprt", "sldasm"
# }
# ARCHIVE_EXTS = {
#     "zip", "rar", "7z", "tar", "gz", "bz2", "xz"
# }


# # --- Hashers ---
# def hash_file_blake3(filepath: str) -> str:
#     """Stream-hash a file with BLAKE3 to a hex digest."""
#     h = blake3()
#     try:
#         with open(filepath, "rb") as f:
#             while True:
#                 chunk = f.read(BLOCK_SIZE)
#                 if not chunk:
#                     break
#                 h.update(chunk)
#         return h.hexdigest()
#     except FileNotFoundError:
#         return "FILE_NOT_FOUND"
#     except Exception as e:
#         return f"ERROR: {e}"


# def choose_hasher_for_file(filename: str) -> Callable[[str], str]:
#     """
#     Decide which hasher to use for a given file by extension.
#     Currently routes all types to BLAKE3 (cryptographic, fast),
#     but you can swap specific groups to other libraries if needed.
#     """
#     ext = os.path.splitext(filename)[1].lower().lstrip(".")

#     # Examples of how you might customize later:
#     # - return hash_file_image_phash for IMAGE_EXTS (perceptual hash, not cryptographic)
#     # - return hash_file_blake3 for everything else (cryptographic)

#     if ext in IMAGE_EXTS:
#         return hash_file_blake3
#     if ext in VIDEO_EXTS:
#         return hash_file_blake3
#     if ext in AUDIO_EXTS:
#         return hash_file_blake3
#     if ext in DOC_EXTS:
#         return hash_file_blake3
#     if ext in TEXT_EXTS:
#         return hash_file_blake3
#     if ext in THREED_EXTS:
#         return hash_file_blake3
#     if ext in ARCHIVE_EXTS:
#         return hash_file_blake3

#     # Default: hash anything else with BLAKE3 as well
#     return hash_file_blake3


# # --- Core functions ---
# def calculate_file_hash(filepath: str) -> str:
#     """Calculates the hash of a single file using a type-appropriate hasher."""
#     filename = os.path.basename(filepath)
#     hasher = choose_hasher_for_file(filename)
#     return hasher(filepath)


# def process_folder(input_folder: str) -> List[Tuple[str, str]]:
#     """
#     Iterates through all files in a folder (non-recursive) and generates their hashes.
#     Returns a list of (filename, digest).
#     """
#     results: List[Tuple[str, str]] = []

#     if not os.path.isdir(input_folder):
#         print(f"Error: Input directory '{input_folder}' not found.")
#         return results

#     print(f"Processing files in '{input_folder}'...")

#     for filename in os.listdir(input_folder):
#         filepath = os.path.join(input_folder, filename)

#         if os.path.isfile(filepath):
#             file_hash = calculate_file_hash(filepath)
#             results.append((filename, file_hash))
#             # Print first 12 chars to keep console tidy
#             print(f"  Hashed {filename}: {file_hash[:12]}...")

#     return results


# def write_results_to_csv(data: List[Tuple[str, str]], output_file: str):
#     """Writes the list of filenames and hashes to a CSV file."""
#     try:
#         with open(output_file, 'w', newline='', encoding="utf-8") as csvfile:
#             writer = csv.writer(csvfile)
#             # Keeping the schema to two columns as requested
#             writer.writerow(['Filename', 'Hash'])  # Using BLAKE3 under the hood
#             writer.writerows(data)
#         print(f"\nSuccessfully wrote results to '{output_file}'.")
#     except Exception as e:
#         print(f"Error writing to CSV: {e}")


# # --- MongoDB helpers ---
# def get_mongo_collection() -> Optional["MongoClient"]:
#     """Connects to MongoDB Atlas and returns the collection handle, or None on failure."""
#     if not MONGODB_URI:
#         print("Warning: MONGODB_URI not set. Skipping MongoDB write.")
#         return None

#     try:
#         client = MongoClient(MONGODB_URI)
#         db = client[MONGODB_DB]
#         collection = db[MONGODB_COLLECTION]
#         # Optional: ensure we upsert on filename (unique)
#         collection.create_index("filename", unique=True)
#         return collection
#     except Exception as e:
#         print(f"Error connecting to MongoDB: {e}")
#         return None


# def write_results_to_mongo(data: List[Tuple[str, str]]):
#     """Upserts (filename, hash) pairs into MongoDB Atlas."""
#     collection = get_mongo_collection()
#     if collection is None:
#         return

#     try:
#         ops = []
#         for filename, digest in data:
#             ops.append(
#                 UpdateOne(
#                     {"filename": filename},
#                     {"$set": {"filename": filename, "hash": digest}},
#                     upsert=True
#                 )
#             )
#         if not ops:
#             print("No MongoDB operations to perform.")
#             return

#         result = collection.bulk_write(ops, ordered=False)
#         inserted = result.upserted_count
#         modified = result.modified_count
#         print(f"MongoDB write complete. Upserted: {inserted}, Modified: {modified}")
#     except Exception as e:
#         print(f"Error writing to MongoDB: {e}")


# # --- Main ---
# if __name__ == "__main__":
#     # Determine absolute paths based on script location
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     input_path = os.path.join(script_dir, INPUT_DIR_NAME)
#     output_path = os.path.join(script_dir, OUTPUT_FILE_NAME)

#     # 1. Process folder and compute hashes
#     hashing_results = process_folder(input_path)

#     # 2. Write results to CSV
#     if hashing_results:
#         write_results_to_csv(hashing_results, output_path)
#     else:
#         print("No files were processed.")

#     # 3. Write results to MongoDB Atlas
#     if hashing_results:
#         write_results_to_mongo(hashing_results)






from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import os, tempfile, shutil
from contextlib import asynccontextmanager
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import logging

from core.file_hasher import hash_file, process_folder_once
from core.database import find_file_by_hash, upsert_hashes, get_mongo_collection
from core.interact_certifier import retrieve_record, store_record, get_total_record
import uvicorn
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up — scanning for new files...")
    process_folder_once()
    print("Initial sync complete.")
    yield
    print("Shutting down...")


app = FastAPI(
    title="File Integrity Service", 
    version="1.0.0", 
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(admin_id: str, expires_delta=None):
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "admin_id": admin_id,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token_from_header(authorization: Optional[str] = None):
    """Verify JWT token from Authorization header"""
    print(f"[DEBUG] Authorization header received: {authorization}")
    
    if authorization is None:
        print("[DEBUG] Authorization header is None")
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        parts = authorization.split()
        if len(parts) != 2:
            print(f"[DEBUG] Authorization header has {len(parts)} parts, expected 2")
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        scheme, token = parts
        if scheme.lower() != "bearer":
            print(f"[DEBUG] Scheme is '{scheme}', expected 'bearer'")
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        print(f"[DEBUG] Token extracted: {token[:20]}...")
    except ValueError as e:
        print(f"[DEBUG] ValueError parsing authorization header: {e}")
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    try:
        print(f"[DEBUG] Decoding token with SECRET_KEY...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("admin_id")
        
        if admin_id is None:
            print("[DEBUG] admin_id not found in token payload")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"[DEBUG] Token verified successfully for admin_id: {admin_id}")
        return admin_id
    except jwt.ExpiredSignatureError as e:
        print(f"[DEBUG] Token expired: {e}")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"[DEBUG] Invalid token: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_admin_collection():
    """Get admin collection from MongoDB"""
    try:
        col = get_mongo_collection()
        if col is None:
            print("[ERROR] get_mongo_collection returned None")
            return None
        
        client = col.client
        db = client[os.getenv("MONGODB_DB", "file_hashes_db")]
        admins_col = db["admins"]
        
        # Create index on username
        admins_col.create_index("username", unique=True)
        
        return admins_col
    except Exception as e:
        print(f"[ERROR] Error getting admin collection: {e}")
        return None

def cleanup_files_folder():
    """Delete all files from backend/files folder"""
    try:
        files_dir = "files"
        if os.path.exists(files_dir):
            for filename in os.listdir(files_dir):
                file_path = os.path.join(files_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"✓ Deleted: {filename}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f"✓ Deleted folder: {filename}")
                except Exception as e:
                    print(f"[ERROR] Error deleting {filename}: {e}")
            
            print("✓ Files folder cleaned successfully")
            return True
    except Exception as e:
        print(f"[ERROR] Error cleaning files: {str(e)}")
    return False

# ============= ADMIN AUTHENTICATION ENDPOINTS =============

@app.post("/admin/register")
async def register_admin(username: str, password: str, email: str, full_name: str):
    """
    Register a new admin user
    First admin can be registered with this endpoint
    """
    try:
        # Validate input
        if not username or len(username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        if not password or len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="Invalid email")
        if not full_name or len(full_name) < 2:
            raise HTTPException(status_code=400, detail="Full name required")
        
        admins_col = get_admin_collection()
        if admins_col is None:
            raise HTTPException(status_code=500, detail="Database not configured")
        

        existing = admins_col.find_one({"username": username})
        if existing:
            raise HTTPException(status_code=400, detail="Admin already exists")
        admin_doc = {
            "username": username,
            "password": hash_password(password),
            "email": email,
            "full_name": full_name,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = admins_col.insert_one(admin_doc)
        
        return {
            "status": "success",
            "message": "Admin registered successfully",
            "admin_id": str(result.inserted_id)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[ERROR] Registration error: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.post("/admin/login")
async def login_admin(username: str, password: str):
    """
    Login admin with username and password
    Returns JWT token
    """
    try:
        print(f"[DEBUG] Login attempt for username: {username}")
        
        admins_col = get_admin_collection()
        if admins_col is None:
            raise HTTPException(status_code=500, detail="Database not configured")
        
        # Find admin by username
        admin = admins_col.find_one({"username": username})
        if admin is None:
            print(f"[DEBUG] Admin not found: {username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        if not verify_password(password, admin["password"]):
            print(f"[DEBUG] Password verification failed for: {username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Check if admin is active
        if not admin.get("is_active", False):
            print(f"[DEBUG] Admin account inactive: {username}")
            raise HTTPException(status_code=403, detail="Admin account is inactive")
        
        # Create token
        access_token = create_access_token(str(admin["_id"]))
        print(f"[DEBUG] Token created successfully for admin_id: {admin['_id']}")
        
        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "admin": {
                "id": str(admin["_id"]),
                "username": admin["username"],
                "email": admin["email"],
                "full_name": admin["full_name"]
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.get("/admin/verify-token")
async def verify_admin_token(authorization: Optional[str] = Header(None)):
    """
    Verify if admin token is valid
    Expects: Authorization: Bearer <token> header
    """
    print(f"[DEBUG] /admin/verify-token endpoint called")
    print(f"[DEBUG] Headers received - Authorization: {authorization}")
    
    admin_id = verify_token_from_header(authorization)
    return {
        "status": "valid",
        "admin_id": admin_id
    }

# ============= USER ENDPOINTS =============

@app.post("/verify")
async def verify_uploaded_file(file: UploadFile = File(...)):
    """Upload a file, hash it, and check DB for match."""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        file_hash = hash_file(tmp_path)
        os.remove(tmp_path)

        record = find_file_by_hash(file_hash)
        if record:
            hash_retrieved_hex, block_num, timestamp = retrieve_record(record["recordId"])
            return {
                "status": "original",
                "matched_file": record["filename"],
                "hash": record["hash"],
                "recordId": record["recordId"],
                "block_num": block_num,
                "timestamp": timestamp,
                "hash_verified": hash_retrieved_hex
            }
        else:
            return {
                "status": "no_match",
                "message": "No such file in DB.",
                "hash": file_hash,
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============= ADMIN ENDPOINTS (Protected) =============

@app.post("/admin/upload")
async def admin_upload_files(
    files: List[UploadFile] = File(...),
    authorization: Optional[str] = Header(None)
):
    """
    Admin endpoint: Upload multiple files, hash them, and store them.
    Supports any file type including 3D models and zips.
    Requires valid JWT token in Authorization header.
    """
    try:
        print(f"[DEBUG] /admin/upload endpoint called")
        print(f"[DEBUG] Authorization header: {authorization}")
        
        # Verify admin token
        admin_id = verify_token_from_header(authorization)
        print(f"[DEBUG] Upload authorized for admin_id: {admin_id}")
        
        results = []
        os.makedirs("files", exist_ok=True)

        for file in files:
            try:
                # Save file to files folder (accept any file type)
                file_path = os.path.join("files", file.filename)
                
                # Create subdirectories if they don't exist
                os.makedirs(os.path.dirname(file_path) or "files", exist_ok=True)
                
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)

                # Hash the file
                file_hash = hash_file(file_path)

                # Store on blockchain
                new_record_Id, digest, tx_hash = store_record(file_path)

                # Save to database
                upsert_hashes([(file.filename, digest, new_record_Id)])

                # Convert tx_hash to string
                tx_hash_str = tx_hash.hex() if hasattr(tx_hash, "hex") else str(tx_hash)

                results.append({
                    "filename": file.filename,
                    "hash": file_hash,
                    "recordId": new_record_Id,
                    "status": "success",
                    "tx_hash": tx_hash_str,
                    "file_type": file.content_type or "unknown"
                })
                print(f"✓ Uploaded and verified: {file.filename}")

            except Exception as e:
                print(f"✗ Error processing {file.filename}: {str(e)}")
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })

        # After successful upload, cleanup files
        successful_count = len([r for r in results if r["status"] == "success"])
        cleanup_status = "pending"
        
        if successful_count > 0:
            print("\nCleaning up files folder...")
            if cleanup_files_folder():
                cleanup_status = "completed"
            else:
                cleanup_status = "failed"

        return {
            "uploaded_files": results,
            "total": len(results),
            "successful": successful_count,
            "failed": len([r for r in results if r["status"] == "error"]),
            "cleanup_status": cleanup_status
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[ERROR] Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/stats")
async def admin_stats(authorization: Optional[str] = Header(None)):
    """Get admin statistics - requires authentication"""
    try:
        print(f"[DEBUG] /admin/stats endpoint called")
        print(f"[DEBUG] Authorization header: {authorization}")
        
        # Verify admin token
        admin_id = verify_token_from_header(authorization)
        print(f"[DEBUG] Stats authorized for admin_id: {admin_id}")
        
        total_records = get_total_record()
        csv_entries = 0

        if os.path.exists("output.csv"):
            with open("output.csv", "r") as f:
                lines = f.readlines()
                csv_entries = len(lines) - 1 if len(lines) > 1 else 0

        return {
            "total_records": total_records,
            "csv_entries": csv_entries,
            "upload_folder": "files",
            "status": "ok"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"[ERROR] Stats error: {str(e)}")
        return {
            "total_records": 0,
            "csv_entries": 0,
            "upload_folder": "files",
            "error": str(e),
            "status": "error"
        }

@app.post("/admin/logout")
async def logout_admin(authorization: Optional[str] = Header(None)):
    """Logout admin - token becomes invalid on frontend"""
    try:
        admin_id = verify_token_from_header(authorization)
        return {
            "status": "success",
            "message": "Logged out successfully"
        }
    except HTTPException as e:
        raise e

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "File Integrity Service"}


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000

    print("\nServer starting...")
    print(f"Local:     http://{host}:{port}")
    print(f"API Docs:  http://{host}:{port}/docs\n")

    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)