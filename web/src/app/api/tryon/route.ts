import { Buffer } from "node:buffer";
import { NextRequest, NextResponse } from "next/server";
import { GoogleGenerativeAI } from "@google/generative-ai";

const MODEL_NAME = "gemini-2.5-flash-image";
const SCENES = [
  {
    id: "subway",
    title: "Subway sprint",
    text:
      "Generate a photorealistic image of the person. Maintain the person's identity, facial features, body proportions, and lighting. "
      + "Same young man, same outfit, running towards the subway. He holds a white bag in his right hand, with a worrying posture that shows how the hoodie fits when in motion, soft shadows, warm tones, realistic lifestyle photo.",
  },
  {
    id: "cafe",
    title: "Coffee break",
    text:
      "Generate a photorealistic image of the person. Maintain the person's identity, facial features, body proportions, and lighting. "
      + "Same young man, same outfit, sitting in a cafeteria, sipping coffee. He has a relaxed posture, showing comfort, showing how the hoodie fits when seated, soft shadows, warm tones, realistic lifestyle photo.",
  },
  {
    id: "gym",
    title: "Gym floor",
    text:
      "Generate a photorealistic image of the person. Maintain the person's identity, facial features, body proportions, and lighting. "
      + "Same young man, same outfit, laying down in the gym, lifting weights. He has an athletic posture, showing effort, showing how the hoodie fits when laying on the floor, soft shadows, warm tones, realistic lifestyle photo.",
  },
];

export const runtime = "nodejs";
export const maxDuration = 60;

function getApiKey() {
  const key = process.env.GEMINI_API_KEY ?? process.env.GOOGLE_API_KEY;
  if (!key) {
    throw new Error("Set GEMINI_API_KEY or GOOGLE_API_KEY in your environment.");
  }
  return key;
}

async function fileToInlineData(file: File) {
  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  const mimeType = file.type || "image/png";

  return {
    inlineData: {
      data: buffer.toString("base64"),
      mimeType,
    },
  };
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file");

    if (!(file instanceof File)) {
      return NextResponse.json(
        { error: "Image file is required under field name 'file'." },
        { status: 400 }
      );
    }

    const baseImagePart = await fileToInlineData(file);
    const genAI = new GoogleGenerativeAI(getApiKey());
    const model = genAI.getGenerativeModel({ model: MODEL_NAME });

    const images = [];

    for (const scene of SCENES) {
      const result = await model.generateContent({
        contents: [
          {
            role: "user",
            parts: [baseImagePart, { text: scene.text }],
          },
        ],
      });

      const part =
        result.response.candidates?.[0]?.content?.parts?.find(
          (p) => p.inlineData?.data
        ) ?? null;
      const inlineData = part?.inlineData;

      if (!inlineData?.data) {
        throw new Error(`No image returned for scene '${scene.id}'.`);
      }

      images.push({
        id: scene.id,
        title: scene.title,
        src: `data:${inlineData.mimeType ?? "image/png"};base64,${inlineData.data}`,
      });
    }

    return NextResponse.json({ images });
  } catch (error) {
    console.error("[tryon] error", error);
    const message = error instanceof Error ? error.message : "Unexpected error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
