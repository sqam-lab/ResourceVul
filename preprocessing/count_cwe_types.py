import json
from collections import Counter
import glob

# Adjust the file path pattern to match your dataset location
file_paths = glob.glob("/Users/isoo0301/Desktop/REU_Summer2025/InfectPrompt/diverseVul/diversevul_parsed_as_vul.jsonl", recursive=True)

cwe_counter = Counter()

for file_path in file_paths:
    with open(file_path, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                cwe = data.get('cwe') 
                target = data.get('target')
                if target == 1 and cwe and cwe != 'None':
                    # If multiple CWEs are stored as a comma-separated string
                    for c in str(cwe).split(','):
                        # cwe_counter[c.strip()] += 1
                        clean_cwe = c.strip().strip("[]'\"")
                        if clean_cwe:
                            cwe_counter[clean_cwe] += 1
            except json.JSONDecodeError:
                print(f"Invalid JSON in {file_path}, skipping line.")

# Print results
print("DiverseVul Dataset CWE Type Counts:")
i = 0
for cwe, count in cwe_counter.most_common():
    #print(f"'{cwe}'")
    i += 1
    print(f"{cwe}: {count}")
print(i)
print(f"Total CWE Instances: {sum(cwe_counter.values())}")