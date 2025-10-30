import os
import sys

# 1. Import the specific function from your utility file
# (Assuming your utility script is named 'hash_utility.py')
# from script.utils.hashing_utility import hash_file 
from utils.hashing_utility import hash_file 

def main():
    # 1. Define the path to the file you want to hash
    file_path = "/home/gerard/Software/Blockchain_Web_App/fyp/dev/CertRoot/inputs/frog.jpg" 

    print(f"Attempting to hash file: {file_path}")
    print("-" * 30)
    
    # Check if the file exists before attempting to hash
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'. Please ensure the path is correct.", file=sys.stderr)
        sys.exit(1)

    try:
        # 2. Use the imported hash_file function
        hash_result = hash_file(file_path)
        
        print(f"File: {file_path}")
        print(f"BLAKE3 Hash: {hash_result}")
        
    except Exception as e:
        print(f"An error occurred during hashing: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()