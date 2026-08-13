import os
import shutil

def is_brackets_balanced(content):
    # Check if curly braces {} are all matched
    stack = []
    for char in content:
        if char == '{':
            stack.append(char)
        elif char == '}':
            if not stack:       # Bracket is unmatched
                return False  
            stack.pop()
    return len(stack) == 0  # True if all opened braces are closed

def move_truncated_files(src_dir, dest_dir, extensions=None):
    if extensions is None:
        extensions = ['.c', '.cpp']

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for root, _, files in os.walk(src_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")
                    continue

                if not is_brackets_balanced(content):
                    print(f"Moving truncated file: {full_path}")
                    # Keep directory structure the same throughout
                    rel_path = os.path.relpath(root, src_dir)
                    target_dir = os.path.join(dest_dir, rel_path)
                    os.makedirs(target_dir, exist_ok=True)
                    shutil.move(full_path, os.path.join(target_dir, file))

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Move truncated C/C++ files (unmatched brackets) to a separate folder.")
    parser.add_argument("src_dir", help="Source directory to search files")
    parser.add_argument("--dest_dir", default="./vul-injected/CWE416-copy-truncated_files", help="Destination directory for truncated files")
    args = parser.parse_args()

    move_truncated_files(args.src_dir, args.dest_dir)
