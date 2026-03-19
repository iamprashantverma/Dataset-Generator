"""
Fix image paths in JSONL dataset to file:/// URI format
Converts: output\images\invoice_0001_0.jpg
To:       file:///D:/Training/Practice-python/output/images/invoice_0001_0.jpg
"""

import jsonlines
import os
from pathlib import Path

def fix_image_path(relative_path: str) -> str:
    """Convert relative path to absolute file:/// URI"""
    # Get absolute path
    abs_path = os.path.abspath(relative_path)
    
    # Convert backslashes to forward slashes
    abs_path = abs_path.replace('\\', '/')
    
    # Add file:/// prefix
    return f"file:///{abs_path}"


def fix_jsonl_file(input_file: str, output_file: str):
    """Fix image paths in a JSONL file"""
    
    fixed_count = 0
    total_entries = 0
    
    with jsonlines.open(input_file) as reader, \
         jsonlines.open(output_file, mode='w') as writer:
        
        for entry in reader:
            total_entries += 1
            
            # Fix user message content
            for content_item in entry['messages'][0]['content']:
                if content_item['type'] == 'image':
                    # Fix the image path
                    old_path = content_item['image']
                    content_item['image'] = fix_image_path(old_path)
                    fixed_count += 1
                    
                    # Remove null text field if present
                    if 'text' in content_item:
                        del content_item['text']
                
                elif content_item['type'] == 'text':
                    # Remove null image field if present
                    if 'image' in content_item:
                        del content_item['image']
            
            # Fix assistant message content (convert array to string if needed)
            asst_content = entry['messages'][1]['content']
            if isinstance(asst_content, list) and len(asst_content) > 0:
                # Extract text from first content item
                entry['messages'][1]['content'] = asst_content[0]['text']
            
            writer.write(entry)
    
    return total_entries, fixed_count


if __name__ == "__main__":
    import sys
    
    # Process train.jsonl
    print("=" * 60)
    print("FIXING IMAGE PATHS IN JSONL FILES")
    print("=" * 60)
    
    files_to_fix = [
        ('output/jsonl/train.jsonl', 'output/jsonl/train_fixed.jsonl'),
        ('output/jsonl/val.jsonl', 'output/jsonl/val_fixed.jsonl'),
    ]
    
    for input_file, output_file in files_to_fix:
        if not os.path.exists(input_file):
            print(f"\n⚠ Skipping {input_file} (not found)")
            continue
        
        print(f"\nProcessing: {input_file}")
        total, fixed = fix_jsonl_file(input_file, output_file)
        print(f"  ✓ Entries processed: {total}")
        print(f"  ✓ Image paths fixed: {fixed}")
        print(f"  ✓ Output: {output_file}")
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)
    print("\nFixed files created:")
    print("  - output/jsonl/train_fixed.jsonl")
    print("  - output/jsonl/val_fixed.jsonl")
    print("\nChanges made:")
    print("  1. Image paths converted to file:/// URI format")
    print("  2. Removed null 'text' fields from image entries")
    print("  3. Removed null 'image' fields from text entries")
    print("  4. Assistant content converted to plain string")
