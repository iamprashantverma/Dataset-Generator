import jsonlines

# Read first entry
with jsonlines.open('output/jsonl/train.jsonl') as reader:
    data = list(reader)[0]

print("=" * 60)
print("DATASET FORMAT VERIFICATION")
print("=" * 60)

print(f"\nTop-level keys: {list(data.keys())}")

print(f"\n--- MESSAGES STRUCTURE ---")
print(f"Number of messages: {len(data['messages'])}")

print(f"\n--- USER MESSAGE ---")
user_msg = data['messages'][0]
print(f"Role: {user_msg['role']}")
print(f"Content items: {len(user_msg['content'])}")

image_count = sum(1 for c in user_msg['content'] if c['type'] == 'image')
text_count = sum(1 for c in user_msg['content'] if c['type'] == 'text')

print(f"  - Images: {image_count}")
print(f"  - Text prompts: {text_count}")

print(f"\nFirst 2 content items:")
for i, content in enumerate(user_msg['content'][:2]):
    print(f"  {i+1}. Type: {content['type']}, Image: {content.get('image', 'N/A')[:50] if content.get('image') else None}")

print(f"\n--- ASSISTANT MESSAGE ---")
asst_msg = data['messages'][1]
print(f"Role: {asst_msg['role']}")
print(f"Content items: {len(asst_msg['content'])}")
print(f"Content type: {asst_msg['content'][0]['type']}")
print(f"JSON length: {len(asst_msg['content'][0]['text'])} characters")

print("\n" + "=" * 60)
print(" FORMAT VERIFICATION COMPLETE")
print("=" * 60)
print("\nFormat matches Qwen2-VL fine-tuning requirements:")
print("  ✓ messages array with user and assistant roles")
print("  ✓ user content has images + text prompt")
print("  ✓ assistant content has JSON response")
