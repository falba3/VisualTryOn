# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import mimetypes
import os
import argparse
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types

def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def _part_from_image_path(path):
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        mime_type = "image/png"
    with open(path, "rb") as f:
        data = f.read()
    return types.Part.from_bytes(mime_type=mime_type, data=data)


def generate_tryon(face_image_path, prompt, out_path=None):
    # Load variables from .env if present
    dotenv_path = find_dotenv(usecwd=True)
    load_dotenv(dotenv_path=dotenv_path, override=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    # if not api_key:
    #     raise RuntimeError("GEMINI_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)

    model = "gemini-2.5-flash-image"

    face_part = _part_from_image_path(face_image_path)

    user_text = prompt

    contents = [
        types.Content(
            role="user",
            parts=[
                face_part,
                types.Part.from_text(text=user_text),
            ],
        )
    ]

    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

    saved_any_image = False
    image_count = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            not getattr(chunk, "candidates", None)
            or not getattr(chunk.candidates[0], "content", None)
            or not getattr(chunk.candidates[0].content, "parts", None)
        ):
            continue

        part0 = chunk.candidates[0].content.parts[0]
        if getattr(part0, "inline_data", None) and getattr(part0.inline_data, "data", None):
            inline_data = part0.inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"

            if out_path and not saved_any_image:
                target = out_path
            else:
                base = os.path.splitext(out_path)[0] if out_path else "tryon_output"
                target = f"{base}_{image_count}{file_extension}"

            save_binary_file(target, data_buffer)
            saved_any_image = True
            image_count += 1
        elif getattr(chunk, "text", None):
            print(chunk.text)

    if not saved_any_image:
        raise RuntimeError("No image was returned by the model.")


def main():
    parser = argparse.ArgumentParser(description="Single image try-on using Gemini 2.5 image model with a script-defined prompt")
    parser.add_argument("--face", required=True, help="Path to the person/face image")
    # Define a hardcoded prompt for the image generation
    script_defined_prompt = (
        "Generate a photorealistic image of the person. "
        "Maintain the person's identity, facial features, body proportions, and lighting. "
        "Same young man, same outfit and headphones around neck, sitting by a window in a bright cafe with natural light. He holds and sips a to-go coffee cup, relaxed posture that shows how the hoodie sits when seated, soft shadows, warm tones, realistic lifestyle photo." 
    )
    parser.add_argument("--out", default="", help="Optional output file path (first image)")
    args = parser.parse_args()

    out_path = args.out if args.out else None
    generate_tryon(args.face, script_defined_prompt, out_path)

if __name__ == "__main__":
    main()