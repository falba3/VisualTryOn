import base64
import mimetypes
import os
import argparse
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types



def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")


def _part_from_image_path(path):
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        mime_type = "image/png"
    with open(path, "rb") as f:
        data = f.read()
    return types.Part.from_bytes(mime_type=mime_type, data=data)


# ----------------------------------------------------------
# NEW FUNCTION: returns all THREE prompts you provided
# ----------------------------------------------------------
def get_all_prompts():
    """Returns a list of (name, text) prompt pairs."""
    
    prompt_subway = (
        "Generate a photorealistic image of the person. "
        "Maintain the person's identity, facial features, body proportions, and lighting. "
        "Same young man, same outfit, running towards the subway. He holds a white bag in his right hand, "
        "with a worrying posture that shows how the hoodie fits when in motion, soft shadows, warm tones, "
        "realistic lifestyle photo."
    )

    prompt_cafe = (
        "Generate a photorealistic image of the person. "
        "Maintain the person's identity, facial features, body proportions, and lighting. "
        "Same young man, same outfit, sitting in a cafeteria, sipping coffee. He has a relaxed posture, "
        "showing comfort, showing how the hoodie fits when seated, soft shadows, warm tones, "
        "realistic lifestyle photo."
    )

    prompt_gym = (
        "Generate a photorealistic image of the person. "
        "Maintain the person's identity, facial features, body proportions, and lighting. "
        "Same young man, same outfit, laying down in the gym, lifting weights. He has an athletic posture, "
        "showing effort, showing how the hoodie fits when laying on the floor, soft shadows, warm tones, "
        "realistic lifestyle photo."
    )

    return [
        ("subway", prompt_subway),
        ("cafe", prompt_cafe),
        ("gym", prompt_gym),
    ]


def generate_tryon(face_image_path, out_base=None):
    # Load .env from current directory or parents
    load_dotenv(override=True)

    # Support both variable names
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)
    model = "gemini-2.5-flash-image"

    face_part = _part_from_image_path(face_image_path)

    # Output base name
    if out_base:
        base_name, _ = os.path.splitext(out_base)
    else:
        base_name = "tryon_output"

    prompts = get_all_prompts()

    # ----------------------------------------------------------
    # Loop over the 3 prompts and generate 3 different images
    # ----------------------------------------------------------
    for suffix, prompt_text in prompts:
        print(f"\n[+] Generating variation: {suffix}")

        contents = [
            types.Content(
                role="user",
                parts=[
                    face_part,
                    types.Part.from_text(text=prompt_text),
                ],
            )
        ]

        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

        saved = False

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
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

                output_name = f"{base_name}_{suffix}{file_extension}"
                save_binary_file(output_name, data_buffer)
                saved = True
                break

            elif getattr(chunk, "text", None):
                print(chunk.text)

        if not saved:
            raise RuntimeError(f"No image was returned for prompt '{suffix}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate three try-on scenes using a single input portrait."
    )
    parser.add_argument("--face", required=True, help="Path to the person's image")
    parser.add_argument("--out", default="", help="Optional base output filename")
    args = parser.parse_args()

    out_base = args.out if args.out else None
    generate_tryon(args.face, out_base)


if __name__ == "__main__":
    main()
