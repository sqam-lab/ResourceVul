import json
import os

input_jsonl = "/home/lkwn6/data/primeVul_final/fine_sub_split_4.jsonl"
output_dir = "/home/lkwn6/data/primeVul_final/CWE-20-fine-for-preprocessing/"
os.makedirs(output_dir, exist_ok = True)

with open(input_jsonl, "r") as infile:
    for line in infile:
        data = json.loads(line)
        func = data.get("func")
        idx = data.get("idx")

        if func:
            filename = f"nonvul_{idx}.c"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w") as f:
                f.write(func)