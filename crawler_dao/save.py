# save.py

import json
import os

def save_jsonl(documents, out_path):
    with open(out_path, "w") as f:
        for doc in documents:
            f.write(json.dumps(doc) + "\n")
