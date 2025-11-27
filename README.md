# VisualTryOn
Visual Try On - Different Scenarios

## Nano Banana Test

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your Gemini API key to `.env`:
   ```env
   GOOGLE_API_KEY="your-key"
   ```
3. Run the script with your reference image:
   ```bash
   python nano_banana_test.py --image path/to/cat.png --output nano.png
   ```
   Optional flags: `--prompt "custom text"`, `--model gemini-2.5-flash-image`.
