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

## Next.js front-end (TypeScript)

1. Install deps:
   ```bash
   cd web
   npm install
   ```
2. Add your Gemini key to `web/.env.local`:
   ```env
   GEMINI_API_KEY=your-key
   # or GOOGLE_API_KEY=your-key
   ```
3. Run the dev server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:3000`, upload a portrait, and generate the three preset scenes (subway, cafe, gym).
