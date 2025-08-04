import os
import json
import re
from transformers import pipeline

# === Configuration ===
MODEL_NAME = "deepseek-ai/deepseek-coder-1.3b-instruct"
CWE_ID = "CWE-125"
CWE_DESCRIPTION = "Out-of-bounds Read"
INPUT_JSON_PATH = "fine_sub_split_2.jsonl"
OUTPUT_FOLDER = "./vul-injected/CWE125/"
BATCH_SIZE = 64  # Adjust based on GPU memory

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load the model pipeline
pipe = pipeline(
    "text-generation",
    model=MODEL_NAME,
    trust_remote_code=True,
    device=0,
)

# === Prompt Formulation ===

def make_prompt(function_code):
    return f"""
### Instruction:
You are a C code transformer. Modify the function below to **intentionally introduce a vulnerability of type {CWE_ID} ({CWE_DESCRIPTION})**.

Only return ONE modified C function. DO NOT explain anything. Add one code comment indicating where vulnerability was introduced.

Your change MUST:
- Introduce a real vulnerability of the given CWE type.
- Inject the vulnerability directly into the existing function body.
- Modify the code in a non-trivial way (do not return the same function).

### Input Function:
```c
{function_code}

### Output:
"""


# === Extract C code from text string ===
def extract_code(text):
    match = re.search(r"```c(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

# === Load and prepare data ===
prompts = []
indices = []

# === Reads JSONL file line-by-line & processes each as a separate JSON object ===
with open(INPUT_JSON_PATH, "r") as infile:
    for line_num, line in enumerate(infile, 1):
        try:
            data = json.loads(line)
            func = data.get("func")
            idx = data.get("idx", line_num)
            if func:
                prompt = make_prompt(func)
                prompts.append(prompt)
                indices.append(idx)
            else:
                print(f"⚠️ Skipped line {line_num}: No function found.")
        except Exception as e:
            print(f"❌ Error parsing line {line_num}: {e}")

# === Process in batches with skipping already processed ===
for i in range(0, len(prompts), BATCH_SIZE):
    batch_prompts = []
    batch_indices = []

    # Filter out prompts for which output already exists
    for j in range(i, min(i + BATCH_SIZE, len(prompts))):
        output_filename = f"vul-{CWE_ID}-{indices[j]}-deepseek-coder.c"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        if os.path.exists(output_path):
            print(f"🟡 Skipping already processed: {output_filename}")
            continue
        batch_prompts.append(prompts[j])
        batch_indices.append(indices[j])

    if not batch_prompts:
        # Nothing to process in this batch, all already done
        continue

    try:
        outputs = pipe(
            batch_prompts,
            max_new_tokens=2048,
            temperature=0.3,
            top_p=0.95,
            do_sample=True
        )

        for j, output in enumerate(outputs):
            full_text = output[0]["generated_text"]
            prompt = batch_prompts[j]

            if full_text.startswith(prompt):
                full_text = full_text[len(prompt):].strip()

            vuln_func = extract_code(full_text)

            output_filename = f"vul-{CWE_ID}-{batch_indices[j]}-deepseek-coder.c"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, "w") as out_file:
                out_file.write(vuln_func)

            print(f"✅ Generated: {output_filename}")

    except Exception as e:
        print(f"❌ Error during batch {i // BATCH_SIZE + 1}: {e}")
