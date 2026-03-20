"""
src/dataset_builder.py
──────────────────────
Orchestrates the full pipeline:

  generate_invoice_data()   →  dict
  generate_invoice_html()   →  HTML string
  html_to_images()          →  [image paths], page_count
  build_entry()             →  dataset dict (Qwen2-VL format)
  write to .jsonl

Produces:
  output/jsonl/train.jsonl
  output/jsonl/val.jsonl
  output/previews/preview_XXXX.pdf   (optional)
"""

import os
import json
import random
import jsonlines
from pathlib import Path
from tqdm import tqdm

from src.data_generator  import generate_invoice_data
from src.renderer        import html_to_images, html_to_pdf


# ─────────────────────────────────────────────────────────────
# BUILD A SINGLE DATASET ENTRY
# ─────────────────────────────────────────────────────────────

def build_entry(image_paths: list[str], data: dict) -> dict:
    """
    Returns one entry in the exact Qwen2-VL fine-tuning format:

    {
      "messages": [
        { "role": "user",
          "content": [
            {"type": "image", "image": "images/invoice_0001_0.jpg"},
            {"type": "image", "image": "images/invoice_0001_1.jpg"},
            {"type": "text", "text": "Extract the invoice..."}
          ]
        },
        { "role": "assistant",
          "content": [
            {"type": "text", "text": "{...json...}"}
          ]
        }
      ]
    }
    """
    import os
    
    user_content = []
    
    # Add images with relative paths starting from "images/"
    for p in image_paths:
        # Extract just the filename from the full path
        filename = os.path.basename(p)
        # Create relative path starting with "images/"
        relative_path = f"images/{filename}"
        
        user_content.append({
            "type": "image",
            "image": relative_path
        })
    
    # Add text prompt
    user_content.append({
        "type": "text",
        "text": "Extract the invoice information as JSON",
    })

    return {
        "messages": [
            {
                "role": "user",
                "content": user_content,
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(data, indent=2)
                    }
                ],
            },
        ]
    }


# ─────────────────────────────────────────────────────────────
# MAIN GENERATION LOOP
# ─────────────────────────────────────────────────────────────

def generate_dataset(
    n          : int,
    output_dir : str,
    val_split  : float = 0.1,
    dpi        : int   = 200,
    previews   : int   = 0,
    layout     : str   = "layout1",  # New parameter for layout selection
) -> None:
    """
    Generate n invoices and write train.jsonl + val.jsonl.

    Parameters
    ----------
    n          : total number of invoices to generate
    output_dir : root output folder  (images/, jsonl/, previews/ created inside)
    val_split  : fraction of data to put in val.jsonl  (default 10%)
    dpi        : image render resolution
    previews   : how many PDFs to save to output/previews/ for inspection
    layout     : layout name (e.g., "layout1", "layout2", "mixed" for random)
    """
    image_dir   = str(Path(output_dir) / "images")
    jsonl_dir   = str(Path(output_dir) / "jsonl")
    preview_dir = str(Path(output_dir) / "previews")

    Path(image_dir).mkdir(parents=True, exist_ok=True)
    Path(jsonl_dir).mkdir(parents=True, exist_ok=True)
    if previews > 0:
        Path(preview_dir).mkdir(parents=True, exist_ok=True)

    # split indices
    all_indices = list(range(n))
    random.shuffle(all_indices)
    val_size    = max(1, int(n * val_split))
    val_indices = set(all_indices[:val_size])

    train_path  = str(Path(jsonl_dir) / "train.jsonl")
    val_path    = str(Path(jsonl_dir) / "val.jsonl")

    page_dist   = {}
    failed      = []

    with jsonlines.open(train_path, mode="w") as train_w, \
         jsonlines.open(val_path,   mode="w") as val_w:

        for i in tqdm(range(n), desc="Generating invoices"):
            # Select layout (if "mixed", randomly choose)
            if layout == "mixed":
                current_layout = random.choice(["layout1", "layout2"])  # Add more as needed
            else:
                current_layout = layout
            
            invoice_id = f"{current_layout}_invoice_{i:04d}"
            try:
                # 1. generate randomised data
                data = generate_invoice_data()
                data["metadata"]["layout"] = current_layout

                # 2. render data → page images (using ReportLab)
                image_paths, actual_pages = html_to_images(
                    None, image_dir, invoice_id, dpi=dpi, data=data
                )

                # 3. update metadata with real page count
                data["metadata"]["total_pages"] = actual_pages
                page_dist[actual_pages] = page_dist.get(actual_pages, 0) + 1

                # 4. build entry
                entry = build_entry(image_paths, data)

                # 5. write to train or val
                if i in val_indices:
                    val_w.write(entry)
                else:
                    train_w.write(entry)

                # 6. optionally save preview PDF
                if i < previews:
                    preview_path = str(Path(preview_dir) / f"preview_{i:04d}.pdf")
                    html_to_pdf(None, preview_path, data=data)

            except Exception as exc:
                print(f"\n⚠  Failed {invoice_id}: {exc}")
                failed.append({"id": invoice_id, "error": str(exc)})

    # ── summary ──────────────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"  Dataset complete")
    print(f"    Train : {train_path}")
    print(f"    Val   : {val_path}")
    print(f"    Images: {image_dir}")
    print(f"\n📄  Page distribution : {dict(sorted(page_dist.items()))}")
    total_images = sum(k * v for k, v in page_dist.items())
    print(f"🖼   Total images      : {total_images}")
    print(f"  Failed            : {len(failed)}/{n}")

    if failed:
        fail_path = str(Path(output_dir) / "failed.json")
        with open(fail_path, "w") as f:
            json.dump(failed, f, indent=2)
        print(f"    Failed list saved: {fail_path}")