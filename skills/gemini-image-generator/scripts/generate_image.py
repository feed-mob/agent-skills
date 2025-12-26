#!/usr/bin/env python3
import argparse
import base64
import os
import sys
from datetime import datetime

from google import genai
from google.genai import types

ASPECT_RATIOS = {
    "1:1",
    "2:3",
    "3:2",
    "3:4",
    "4:3",
    "4:5",
    "5:4",
    "9:16",
    "16:9",
    "21:9",
}

IMAGE_SIZES = {"1K", "2K", "4K"}

MODEL_MAP = {
    "flash": "gemini-2.5-flash-image",
    "pro": "gemini-3-pro-image-preview",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate images with Gemini Nano Banana.")
    parser.add_argument("--prompt", required=True, help="Text prompt for image generation.")
    parser.add_argument("--aspect", default="9:16", help="Aspect ratio (e.g., 9:16, 16:9).")
    parser.add_argument("--count", type=int, default=1, help="Number of images to generate (max 3).")
    parser.add_argument("--model", choices=MODEL_MAP.keys(), default="flash", help="Model: flash or pro.")
    parser.add_argument("--size", choices=sorted(IMAGE_SIZES), help="Image size (Pro only): 1K, 2K, 4K.")
    parser.add_argument("--out-dir", default="outputs", help="Output directory for images.")
    return parser.parse_args()


def get_parts(response):
    if getattr(response, "parts", None):
        return response.parts
    candidates = getattr(response, "candidates", None)
    if not candidates:
        return []
    content = getattr(candidates[0], "content", None)
    return getattr(content, "parts", []) if content else []


def inline_data_bytes(part):
    inline = getattr(part, "inline_data", None) or getattr(part, "inlineData", None)
    if inline is None:
        return None
    data = getattr(inline, "data", None)
    if data is None and isinstance(inline, dict):
        data = inline.get("data")
    if data is None:
        return None
    if isinstance(data, str):
        return base64.b64decode(data)
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, bytes):
        return data
    return None


def main() -> int:
    args = parse_args()

    if args.aspect not in ASPECT_RATIOS:
        print(f"Unsupported aspect ratio: {args.aspect}", file=sys.stderr)
        return 2

    if args.count < 1 or args.count > 3:
        print("--count must be between 1 and 3", file=sys.stderr)
        return 2

    model = args.model
    size = args.size
    if size and model == "flash":
        model = "pro"
        print("Switching to Pro because --size was provided.", file=sys.stderr)

    if model == "pro" and not size:
        size = "1K"

    image_config = types.ImageConfig(aspect_ratio=args.aspect)
    if model == "pro" and size:
        image_config.image_size = size

    config = types.GenerateContentConfig(
        response_modalities=["Image"],
        image_config=image_config,
    )

    client = genai.Client()
    os.makedirs(args.out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    saved_paths = []
    image_index = 1

    for _ in range(args.count):
        response = client.models.generate_content(
            model=MODEL_MAP[model],
            contents=args.prompt,
            config=config,
        )

        parts = get_parts(response)
        if not parts:
            continue

        for part in parts:
            data = inline_data_bytes(part)
            if not data:
                continue
            filename = f"{timestamp}_{image_index:02d}.png"
            path = os.path.join(args.out_dir, filename)
            with open(path, "wb") as f:
                f.write(data)
            saved_paths.append(path)
            image_index += 1

    if not saved_paths:
        print("No image data returned by the API.", file=sys.stderr)
        return 1

    for path in saved_paths:
        print(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
