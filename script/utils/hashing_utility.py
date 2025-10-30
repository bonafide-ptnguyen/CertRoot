# CertRoot/script/utils/hash_utility.py

import sys
import os
import site

# --- BEGIN PATH FIX ---
# This code block manually adds the site-packages directory to the path, 
# ensuring blake3 is found even when mox run fails to set the environment correctly.
try:
    # Get the path to the currently active virtual environment's site-packages
    # site.getsitepackages() is a reliable way to find this.
    site_packages_dir = next(p for p in site.getsitepackages() if os.path.exists(p) and 'CertRoot' in p)
    
    if site_packages_dir not in sys.path:
        sys.path.append(site_packages_dir)
        # print(f"DEBUG: Added {site_packages_dir} to sys.path") # Optional debug line

except Exception as e:
    # Fallback/Log if the venv site-packages path can't be found
    # print(f"DEBUG: Could not automatically find site-packages: {e}") 
    pass
# --- END PATH FIX ---

# The import blake3 line will now look in the injected path
from blake3 import blake3 

# ... rest of your code ...
BLOCK_SIZE = 1024 * 1024

def hash_file(filepath: str) -> str:
    """Return BLAKE3 hash of a file (streamed)."""
    # ... your hash_file logic ...
    h = blake3()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(BLOCK_SIZE):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at '{filepath}'") 
    except Exception as e:
        raise IOError(f"Error reading file '{filepath}': {e}")