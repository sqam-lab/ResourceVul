import re
import os

# normalizer that deletes white spaces and comments

def normalize_code_spacing(content):
    # Normalize spaces around operators and parentheses
    operators = ['==', '!=', '<=', '>=', '=', r'\+', '-', r'\*', '/', '<', '>']
    for op in operators:
        pattern = rf'\s*{op}\s*'
        content = re.sub(pattern, lambda m: m.group(0).strip().replace(' ', ''), content)

    # Remove spaces before closing parentheses
    content = re.sub(r'\s+\)', ')', content)

    # Remove spaces after opening parentheses
    content = re.sub(r'\(\s+', '(', content)

    # Remove leading/trailing spaces on each line
    content = '\n'.join(line.strip() for line in content.splitlines())

    # Replace multiple spaces with a single space
    content = re.sub(r'\s+', ' ', content)

    return content.strip()

def preprocess_and_flatten(file_path):
    with open(file_path, 'r') as f:
        code = f.read()

    # Remove comments (both // and /* */)
    code = re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.DOTALL | re.MULTILINE)

    # Flatten multi-line function headers
    lines = code.splitlines()
    flattened_lines = []
    collecting = False
    buffer = ''
    paren_depth = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if not collecting:
            if '(' in stripped and not stripped.endswith(';'):
                buffer = stripped
                paren_depth = stripped.count('(') - stripped.count(')')
                collecting = True
            else:
                flattened_lines.append(stripped)
        else:
            buffer += ' ' + stripped
            paren_depth += stripped.count('(') - stripped.count(')')

            if paren_depth == 0 and '{' in stripped:
                flattened_lines.append(buffer)
                buffer = ''
                collecting = False

    if buffer.strip():
        flattened_lines.append(buffer)

    flattened_code = '\n'.join(flattened_lines)
    # Normalize whitespace to single spaces
    flattened_code = re.sub(r'\s+', ' ', flattened_code).strip()
    # Put a newline before next function or static keyword after a closing brace for readability
    flattened_code = re.sub(r'\}\s*(?=static|[a-zA-Z_])', '}\n', flattened_code)

     # === NEW: normalize operator and parentheses spacing ===
    flattened_code = normalize_code_spacing(flattened_code)

    with open(file_path, 'w') as f:
        f.write(flattened_code)

    return flattened_code


def process_directory(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".c"):
                path = os.path.join(root, file)
                try:
                    preprocess_and_flatten(path)
                    print(f"Processed: {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    process_directory("./vul-injected/CWE20-copy/")  # Change as needed
