import hashlib
import os
import time
import json
from flask import Flask, jsonify
from flask_cors import CORS
import threading

# Configuration
MONITOR_DIR = "./monitor"
HASH_FILE = "file_hashes.json"
INTERVAL = 10

app = Flask(__name__)
CORS(app)

logs = []  # Store file change logs

# ✅ Function to calculate hash
def calculate_hash(file_path):
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None

# ✅ Function to load hashes
def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return json.load(f)
    return {}

# ✅ Function to save hashes
def save_hashes(hashes):
    with open(HASH_FILE, 'w') as f:
        json.dump(hashes, f, indent=4)

# ✅ Function to monitor file changes
def monitor_changes():
    global logs
    previous_hashes = load_hashes()  # ✅ No NameError now!

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
                            logs.append({"type": "MODIFIED", "file": file_path})
                            print(f"[MODIFIED] {file_path}")
                    else:
                        logs.append({"type": "NEW", "file": file_path})
                        print(f"[NEW] {file_path}")

        for file_path in previous_hashes:
            if file_path not in current_hashes:
                logs.append({"type": "DELETED", "file": file_path})
                print(f"[DELETED] {file_path}")

        save_hashes(current_hashes)
        previous_hashes = current_hashes.copy()
        time.sleep(INTERVAL)

# ✅ API Endpoint to get logs
@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(logs)

if __name__ == "__main__":
    print("Starting file integrity monitor with Flask API...")

    # ✅ Start monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_changes, daemon=True)
    monitor_thread.start()

    # ✅ Run Flask API
    app.run(host="0.0.0.0", port=5000)
