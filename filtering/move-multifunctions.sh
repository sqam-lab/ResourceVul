#!/bin/bash

# Directory to search; default is current directory
SEARCH_DIR="${1:-.}"

# Destination folder
DEST_DIR="$SEARCH_DIR/multi_function_files"
mkdir -p "$DEST_DIR"

echo "Scanning for misnamed C++ files (.c) in: $SEARCH_DIR"
echo "Moving files with >1 function to: $DEST_DIR"
echo ""

# Find files ending in .c (assumed to contain C++ code)
find "$SEARCH_DIR" -type f -name "*.c" | while read -r file; do
    # Force ctags to treat .c files as C++ source
    func_count=$(ctags -x --languages=+C++ --language-force=C++ --c++-kinds=f "$file" 2>/dev/null | wc -l)

    if [ "$func_count" -gt 1 ]; then
        echo "Moving $file (found $func_count functions as C++)"
        mv "$file" "$DEST_DIR/"
    fi
done