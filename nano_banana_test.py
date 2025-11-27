from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from PIL import Image


DEFAULT_PROMPT = (
    "Keep the person's clothing identical to the reference photo, but place "
    "them walking through a park at sunset. Preserve their pose, body "
    "proportions, and styling for a realistic scene."
)

COFFEE_PROMPT = (
    "Show the same person relaxing in a stylish coffee shop at golden hour, "
    "sitting with a warm drink while wearing the exact same outfit."
)

METRO_PROMPT = (
    "Depict the person standing on a platform inside the Madrid metro at "
    "sunset, keeping the outfit identical and ensuring realistic lighting."
)

SCENE_VARIATIONS = (
    ("park", None),
    ("coffee", COFFEE_PROMPT),
    ("metro", METRO_PROMPT),
)

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "output"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reimagine a person photo in a new setting while keeping outfits"
    )
    parser.add_argument(
        "--person-image",
        required=True,
        help="Filename of the person's photo located in the ./input directory",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Optional custom text prompt",
    )
    parser.add_argument(
        "--output-prefix",
        default="generated_image",
        help="Prefix for the three generated images (suffixes are added automatically)",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash-image",
        help="Gemini image model to use",
    )
    return parser.parse_args()


def load_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY missing. Set it in .env or env vars.")
    return api_key


def main() -> None:
    args = parse_args()
    api_key = load_api_key()

    client = genai.Client(api_key=api_key)

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Input directory not found: {INPUT_DIR}. Place source images in this folder."
        )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    person_filename = Path(args.person_image).name
    person_path = INPUT_DIR / person_filename

    if not person_path.exists():
        raise FileNotFoundError(f"Person image not found: {person_path}")

    with Image.open(person_path) as person_img:
        base_image = person_img.copy()

    for scene_suffix, scene_prompt in SCENE_VARIATIONS:
        prompt_text = args.prompt if scene_prompt is None else scene_prompt
        response = client.models.generate_content(
            model=args.model,
            contents=[
                prompt_text,
                base_image.copy(),
            ],
        )

        produced_image = None
        for part in response.parts:
            if getattr(part, "text", None):
                print(part.text)
            elif getattr(part, "inline_data", None):
                produced_image = part.as_image()

        if produced_image is None:
            raise RuntimeError(
                f"Gemini response for scene '{scene_suffix}' did not include image data."
            )

        output_path = OUTPUT_DIR / f"{args.output_prefix}_{scene_suffix}.png"
        produced_image.save(output_path)
        print(f"Saved {scene_suffix} image to {output_path.resolve()}")


if __name__ == "__main__":
    main()