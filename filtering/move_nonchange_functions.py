import os
import shutil
import hashlib

def compute_file_hash(path):
    """Return SHA256 hash of a file's content."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def build_content_hash_map(folder):
    """Build a set of file hashes for all files in a folder."""
    content_hashes = set()
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_hash = compute_file_hash(file_path)
                content_hashes.add(file_hash)
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
    return content_hashes

def move_matching_files(source_folder, reference_folder, destination_folder):
    # Create destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    # Step 1: Build hash set for reference (B) folder
    reference_hashes = build_content_hash_map(reference_folder)

    # Step 2: Go through A folder, move files to C if hash matches
    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_hash = compute_file_hash(file_path)
                if file_hash in reference_hashes:
                    # Preserve relative path
                    rel_path = os.path.relpath(file_path, source_folder)
                    dest_path = os.path.join(destination_folder, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.move(file_path, dest_path)
                    print(f"✅ Moved: {file_path} → {dest_path}")
            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")

# === CONFIGURE YOUR FOLDERS HERE ===
folder_a = './vul-injected/CWE20-copy/'
folder_b = './vul-injected/CWE20-fine-normalized/'
folder_c = './vul-injected/dump/'

if __name__ == '__main__':
    move_matching_files(folder_a, folder_b, folder_c)
