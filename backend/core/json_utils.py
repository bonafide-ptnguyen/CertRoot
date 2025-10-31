import os
import sys
import json

# The 'pathlib' module is also excellent for handling paths cleanly, 
# but we will stick with 'os' as it's consistent with your other files.

# --- Configuration ---
# CONFIG_DIR = "configs"
# CONFIG_FILE = "file_certifier.json"

def get_config_path(configFileName) -> str:
    """
    Constructs the absolute path to the hash_config.json file.
    
    The script's directory is where execution starts.
    Path: script/hello_world.py -> script/configs/hash_config.json
    """
    # 1. Get the directory of the current script (e.g., /.../CertRoot/script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Join the directory, the config folder, and the filename
    config_path = os.path.join(script_dir, "..", "configs", configFileName)
    
    return config_path


def load_hash_config(filepath: str) -> dict:
    """Reads and parses the JSON configuration file."""
    try:
        with open(filepath, 'r') as f:
            config_data = json.load(f)
            return config_data
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON file at {filepath}", file=sys.stderr)
        sys.exit(1)


def get_config(configFileName):
    config_path = get_config_path(configFileName)
    
    print("--- JSON Configuration Loader ---")
    print(f"Attempting to load config from: {config_path}")
    
    # Load the configuration data
    config = load_hash_config(config_path)

    # Access the data (Example: accessing the file_path key)
    rpc_url = config.get("RPC_URL", None)
    wallet_address = config.get("wallet_address", None)
    abi = config.get("abi", None)
    contract_address = config.get("contract_address", None)

    if rpc_url is None or wallet_address is None or abi is None or contract_address is None:
        # A safer approach would be to raise an exception if any required variable is missing
        raise EnvironmentError("Missing required environment variables.")
    
    # print("\nConfiguration successfully loaded.")
    # print(f"Key 'abi' value: {abi}")

    return rpc_url, wallet_address, abi, contract_address

# if __name__ == "__main__":
#     main()
