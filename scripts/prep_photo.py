from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(source_path: str, output_path: str = "source-prepped.png") -> None:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Photo not found: {source}")

    image = Image.open(source).convert("RGBA")
    isolated = remove(image)

    white = Image.new("RGBA", isolated.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, isolated).convert("RGB")

    arr = np.array(composited)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/prep_photo.py <source-photo>")
    prep_photo(sys.argv[1])
