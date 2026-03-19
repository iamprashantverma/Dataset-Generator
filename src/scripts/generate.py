"""
scripts/generate.py
───────────────────
Main entry point — run this to generate the dataset.

Examples
────────
# generate 1000 invoices (default settings)
python scripts/generate.py

# generate 500 with 5 preview PDFs
python scripts/generate.py --n 500 --previews 5

# custom output directory
python scripts/generate.py --n 1000 --output /content/drive/MyDrive/dataset

# higher DPI (better quality, larger files)
python scripts/generate.py --n 1000 --dpi 250
"""

import sys
import argparse
from pathlib import Path

# allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.dataset_builder import generate_dataset


def parse_args():
    p = argparse.ArgumentParser(description="Generate synthetic law firm invoice dataset")
    p.add_argument("--n",        type=int,   default=10,    help="Number of invoices to generate")
    p.add_argument("--output",   type=str,   default="output", help="Root output directory")
    p.add_argument("--val",      type=float, default=0.1,     help="Validation split fraction (default 0.1)")
    p.add_argument("--dpi",      type=int,   default=300,     help="Image render DPI (default 200)")
    p.add_argument("--previews", type=int,   default=0,       help="How many PDFs to save for inspection")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print(f"{'='*50}")
    print(f"  Invoice Dataset Generator")
    print(f"{'='*50}")
    print(f"  Invoices : {args.n}")
    print(f"  Output   : {args.output}")
    print(f"  Val split: {args.val:.0%}")
    print(f"  DPI      : {args.dpi}")
    print(f"  Previews : {args.previews}")
    print(f"{'='*50}\n")

    generate_dataset(
        n          = args.n,
        output_dir = args.output,
        val_split  = args.val,
        dpi        = args.dpi,
        previews   = args.previews,
    )