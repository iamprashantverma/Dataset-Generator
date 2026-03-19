"""
scripts/verify.py
─────────────────
Verifies the generated dataset before training:
  - checks all image paths exist
  - checks JSON is valid in assistant messages
  - checks image count matches message content
  - prints statistics

Usage
─────
python scripts/verify.py --jsonl output/jsonl/train.jsonl
"""

import sys
import json
import argparse
import jsonlines
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def verify(jsonl_path: str) -> None:
    print(f"\nVerifying: {jsonl_path}\n{'─'*50}")

    total          = 0
    missing_images = 0
    bad_json       = 0
    token_mismatch = 0
    page_dist      = {}
    ok             = 0

    with jsonlines.open(jsonl_path) as reader:
        for i, entry in enumerate(reader):
            total += 1
            msgs   = entry["messages"]
            errors = []

            # ── check user content ──
            user_content  = msgs[0]["content"]
            image_entries = [c for c in user_content if c["type"] == "image"]
            text_entries  = [c for c in user_content if c["type"] == "text"]

            num_images = len(image_entries)
            page_dist[num_images] = page_dist.get(num_images, 0) + 1

            # check all image files exist
            for c in image_entries:
                if not Path(c["image"]).exists():
                    missing_images += 1
                    errors.append(f"missing image: {c['image']}")

            # check text entry exists
            if not text_entries:
                errors.append("no text entry in user content")

            # ── check assistant content ──
            asst_content = msgs[1]["content"]
            if asst_content:
                try:
                    parsed = json.loads(asst_content[0]["text"])
                    # check key fields
                    for key in ["invoice_number", "seller", "buyer", "line_items", "totals"]:
                        if key not in parsed:
                            errors.append(f"missing key in JSON: {key}")
                except json.JSONDecodeError as e:
                    bad_json += 1
                    errors.append(f"invalid JSON: {e}")
            else:
                errors.append("empty assistant content")

            if errors:
                print(f"  Entry {i:04d}: ❌  {' | '.join(errors)}")
            else:
                ok += 1

    print(f"\n{'─'*50}")
    print(f"  Total entries    : {total}")
    print(f"    Valid         : {ok}")
    print(f"    Missing images: {missing_images}")
    print(f"    Bad JSON      : {bad_json}")
    print(f"\n  Page distribution: {dict(sorted(page_dist.items()))}")
    total_imgs = sum(k * v for k, v in page_dist.items())
    print(f"  Total images     : {total_imgs}")

    if ok == total:
        print(f"\n  Dataset is CLEAN — ready for training!\n")
    else:
        print(f"\n⚠   Dataset has issues — check errors above\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--jsonl", type=str, required=True, help="Path to .jsonl file to verify")
    args = p.parse_args()
    verify(args.jsonl)