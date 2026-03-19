"""
src/process_example.py
──────────────────────
Two functions used during Qwen2-VL fine-tuning:

  process_example(example)
    - Called via dataset.map()
    - Cleans message format, applies chat template
    - Returns {text, image_paths}  — NO tensors, NO images in RAM

  collate_fn(batch)
    - Called by DataLoader per batch
    - Loads images fresh from disk
    - Tokenizes + encodes with processor
    - Returns tensors ready for model.forward()

Usage
─────
  from src.process_example import process_example, collate_fn, get_processor

  processor = get_processor("Qwen/Qwen2-VL-7B-Instruct")

  dataset = load_dataset("json", data_files={"train": "output/jsonl/train.jsonl"})["train"]
  dataset = dataset.map(process_example, batched=False, remove_columns=dataset.column_names)

  loader  = DataLoader(dataset, batch_size=2, collate_fn=collate_fn, shuffle=True)
"""

from PIL import Image

# ── processor is set once at startup ──────────────────────────
_processor = None

def get_processor(model_name: str = "Qwen/Qwen2-VL-7B-Instruct"):
    """
    Load and cache the processor with invoice-optimised pixel limits.
    Call this ONCE before map() or DataLoader.
    """
    global _processor
    from transformers import AutoProcessor

    _processor = AutoProcessor.from_pretrained(
        model_name,
        min_pixels = 512  * 28 * 28,   # floor — keeps invoice text readable
        max_pixels = 1024 * 28 * 28,   # ceiling — safe for multi-page invoices
    )
    return _processor


def _get_processor():
    if _processor is None:
        raise RuntimeError("Call get_processor() before using process_example / collate_fn")
    return _processor


# ─────────────────────────────────────────────────────────────
# STEP 1 — lightweight .map() function
# ─────────────────────────────────────────────────────────────

def process_example(example: dict) -> dict:
    """
    Cleans one dataset example and applies the chat template.
    Returns plain strings/lists only — no PIL images, no tensors.
    Safe for HuggingFace .map() + Arrow serialisation.

    Input format (from jsonl):
        example["messages"] = [
            { "role": "user",
              "content": [
                {"type":"image","image":"path/to/img.jpg","text":null},
                {"type":"text", "image":null, "text":"Extract..."}
              ]
            },
            { "role": "assistant",
              "content": [{"type":"text","image":null,"text":"{...json...}"}]
            }
        ]

    Output:
        { "text": "<|im_start|>user ...", "image_paths": ["path/0.jpg", ...] }
    """
    processor = _get_processor()
    messages  = example["messages"]

    clean_messages  = []
    all_image_paths = []

    for msg in messages:
        clean_content = []
        for c in msg["content"]:
            if c["type"] == "image" and c.get("image") is not None:
                all_image_paths.append(c["image"])
                clean_content.append({"type": "image"})          # marker only
            elif c["type"] == "text" and c.get("text") is not None:
                clean_content.append({"type": "text", "text": c["text"]})

        if clean_content:
            clean_messages.append({"role": msg["role"], "content": clean_content})

    text = processor.apply_chat_template(
        clean_messages,
        tokenize=False,
        add_generation_prompt=False,
    )

    return {
        "text"        : text,
        "image_paths" : all_image_paths,
    }


# ─────────────────────────────────────────────────────────────
# STEP 2 — DataLoader collate_fn
# ─────────────────────────────────────────────────────────────

MAX_SEQ_LEN = 32768

def collate_fn(batch: list[dict]) -> dict:
    """
    Called per batch by DataLoader.
    Loads images from disk fresh, tokenises, returns tensors.
    Images are released from RAM after each batch.
    """
    processor = _get_processor()

    texts       = []
    flat_images = []

    for ex in batch:
        images      = []
        valid_count = 0

        for path in ex["image_paths"]:
            try:
                img = Image.open(path).convert("RGB")
                # no manual resize — processor respects min/max_pixels
                images.append(img)
                valid_count += 1
            except Exception as e:
                print(f"⚠  Could not load {path}: {e}")

        text = ex["text"]

        # if any images failed to load, remove their tokens from text
        expected = text.count(processor.image_token)
        if valid_count < expected:
            for _ in range(expected - valid_count):
                text = text.replace(processor.image_token, "", 1)

        texts.append(text)
        flat_images.extend(images)
        # images go out of scope here → RAM freed

    inputs = processor(
        text     = texts,
        images   = flat_images if flat_images else None,
        padding  = True,
        truncation = True,
        max_length = MAX_SEQ_LEN,
        return_tensors = "pt",
    )

    inputs["labels"] = inputs["input_ids"].clone()

    # mask padding tokens so loss ignores them
    pad_id = processor.tokenizer.pad_token_id
    if pad_id is not None:
        inputs["labels"][inputs["labels"] == pad_id] = -100

    return inputs