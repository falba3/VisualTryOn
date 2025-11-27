
"""
Generate multiple Gemini Nano Banana variations from a reference portrait.

Example:
    python sergiio.py --image reference.jpg --output-dir outputs
"""

import argparse
import mimetypes
import os
from pathlib import Path
from typing import List, Tuple

import google.generativeai as gen

DEFAULT_PROMPTS: List[Tuple[str, str]] = [
    (
        "urban_walk",
        "Young adult with round glasses, long dark hair, wearing a teal/blue-green hoodie with a small light logo on the chest, black headphones resting around his neck. He walks on a modern urban street with mid-rise buildings and shopfronts, late-afternoon light, slight breeze showing the drape and fit of the hoodie, natural candid look, full-body, realistic photography.",
    ),
    (
        "cafe_coffee",
        "Same young man, same outfit and headphones around neck, sitting by a window in a bright cafe with natural light. He holds and sips a to-go coffee cup, relaxed posture that shows how the hoodie sits when seated, soft shadows, warm tones, realistic lifestyle photo.",
    ),
    (
        "railing_pose",
        "Same young man, teal hoodie with small logo, black headphones at neck. Leaning back against a railing or low wall, hands in hoodie pocket, looking forward confidently. Urban backdrop with subtle depth of field, morning light, hoodie fit visible around torso, realistic street-style photo.",
    ),
    (
        "phone_check",
        "Same character and outfit, checking his smartphone while standing on a city sidewalk, crosswalk and traffic blur in background, natural posture highlighting hoodie fit, golden-hour light, realistic photo.",
    ),
    (
        "backpack_move",
        "Same character and outfit, adjusting or carrying a backpack on one shoulder in a plaza or subway entrance, dynamic mid-step pose showing hoodie drape, cool daylight, realistic lifestyle photo.",
    ),
]


def load_env_api_key() -> str:
    """Lightweight .env loader to avoid extra dependencies."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            if key and key not in os.environ:
                os.environ[key] = value.strip().strip('"').strip("'")
    return os.getenv("GOOGLE_API_KEY", "")


def load_image_part(image_path: Path) -> dict:
    if not image_path.exists():
        raise FileNotFoundError(f"Reference image not found: {image_path}")
    mime_type = mimetypes.guess_type(str(image_path))[0] or "image/png"
    return {"mime_type": mime_type, "data": image_path.read_bytes()}


def extract_image_bytes(response) -> bytes:
    for candidate in getattr(response, "candidates", []) or []:
        for part in getattr(candidate, "content", None).parts or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                return inline.data
    raise RuntimeError("Model response did not include image data.")


def build_prompts(args) -> List[Tuple[str, str]]:
    if args.prompt:
        return [("custom", args.prompt)]
    selected = set(args.only) if args.only else None
    return [(name, prompt) for name, prompt in DEFAULT_PROMPTS if selected is None or name in selected]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Gemini Nano Banana variations from a reference portrait.")
    parser.add_argument("--image", required=True, help="Path to the reference portrait.")
    parser.add_argument("--output-dir", default="outputs", help="Directory to save generated images.")
    parser.add_argument("--model", default="models/gemini-2.0-nano-banana", help="Gemini model name to use.")
    parser.add_argument("--prompt", help="Custom prompt to generate a single image (skips preset scenarios).")
    parser.add_argument(
        "--only",
        nargs="+",
        choices=[name for name, _ in DEFAULT_PROMPTS],
        help="Run only specific preset scenarios (by key).",
    )
    parser.add_argument("--api-key", help="Override GOOGLE_API_KEY environment variable.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_key = args.api_key or load_env_api_key()
    if not api_key:
        raise SystemExit("Missing GOOGLE_API_KEY. Set it in .env or pass --api-key.")

    gen.configure(api_key=api_key)
    model = gen.GenerativeModel(args.model)

    prompts = build_prompts(args)
    if not prompts:
        raise SystemExit("No prompts to run. Use preset scenarios or --prompt.")

    image_part = load_image_part(Path(args.image))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, prompt in prompts:
        print(f"[+] Generating {name} ...")
        response = model.generate_content(
            [image_part, prompt],
            generation_config={"response_mime_type": "image/png"},
        )
        png_bytes = extract_image_bytes(response)
        out_path = output_dir / f"{name}.png"
        out_path.write_bytes(png_bytes)
        print(f"    saved -> {out_path}")


if __name__ == "__main__":
    main()

