
import hashlib
import os
import time
import json

# Configuration
MONITOR_DIR = "./monitor"  # Directory to monitor
HASH_FILE = "file_hashes.json"  # File to store hashes
INTERVAL = 10  # Time interval for checking changes (in seconds)

def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None

def load_hashes():
    """Load stored hashes from the JSON file."""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    """Save updated hashes to the JSON file."""
    with open(HASH_FILE, 'w') as f:
        json.dump(hashes, f, indent=4)

def monitor_changes():
    """Monitor directory for file changes."""
    previous_hashes = load_hashes()
    while True:
        current_hashes = {}
        for root, _, files in os.walk(MONITOR_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = calculate_hash(file_path)
                if file_hash:
                    current_hashes[file_path] = file_hash
                    
                    if file_path in previous_hashes:
                        if previous_hashes[file_path] != file_hash:
                            print(f"[MODIFIED] {file_path}")
                    else:
                        print(f"[NEW] {file_path}")

        for file_path in previous_hashes:
            if file_path not in current_hashes:
                print(f"[DELETED] {file_path}")

        save_hashes(current_hashes)
        previous_hashes = current_hashes.copy()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    print("Starting file integrity monitor...")
    monitor_changes()

