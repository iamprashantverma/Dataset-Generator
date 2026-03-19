"""
scripts/convert_to_qwen_format.py
──────────────────────────────────
Converts generated JSONL to proper Qwen2-VL fine-tuning format:
  - Removes null fields from content items
  - Converts image paths to file:/// URI format
  - Extracts assistant content as plain string

Usage
─────
python src/scripts/convert_to_qwen_format.py --input output/jsonl/train.jsonl --output output/jsonl/train_qwen.jsonl
"""

import sys
import json
import argparse
import jsonlines
from pathlib import Path

# allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def convert_path_to_uri(path: str) -> str:
    """Convert Windows/Unix path to file:/// URI format"""
    # Replace backslashes with forward slashes
    path = path.replace('\\', '/')
    # Prepend file:/// if not already present
    if not path.startswith('file:///'):
        path = 'file:///' + path
    return path


def clean_content_item(item: dict) -> dict:
    """Remove null fields from content items"""
    cleaned = {"type": item["type"]}
    
    if item["type"] == "image":
        # Convert path to URI format
        cleaned["image"] = convert_path_to_uri(item["image"])
    elif item["type"] == "text":
        cleaned["text"] = item["text"]
    
    return cleaned


def convert_entry(entry: dict) -> dict:
    """Convert a single JSONL entry to Qwen2-VL format"""
    messages = []
    
    for msg in entry["messages"]:
        if msg["role"] == "user":
            # Clean user content items
            cleaned_content = [clean_content_item(item) for item in msg["content"]]
            messages.append({
                "role": "user",
                "content": cleaned_content
            })
        elif msg["role"] == "assistant":
            # Extract text directly as string (not array)
            if isinstance(msg["content"], list) and len(msg["content"]) > 0:
                text_content = msg["content"][0]["text"]
            else:
                text_content = msg["content"]
            
            messages.append({
                "role": "assistant",
                "content": text_content
            })
    
    return {"messages": messages}


def convert_jsonl(input_path: str, output_path: str) -> None:
    """Convert entire JSONL file"""
    converted_count = 0
    
    with jsonlines.open(input_path) as reader, \
         jsonlines.open(output_path, mode='w') as writer:
        
        for entry in reader:
            converted = convert_entry(entry)
            writer.write(converted)
            converted_count += 1
    
    print(f"✅ Converted {converted_count} entries")
    print(f"   Input:  {input_path}")
    print(f"   Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert JSONL to Qwen2-VL format")
    parser.add_argument("--input", type=str, required=True, help="Input JSONL file")
    parser.add_argument("--output", type=str, required=True, help="Output JSONL file")
    args = parser.parse_args()
    
    print(f"{'='*60}")
    print(f"  Qwen2-VL Format Converter")
    print(f"{'='*60}\n")
    
    convert_jsonl(args.input, args.output)
    
    print(f"\n{'='*60}")
    print(f"  Conversion Complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
