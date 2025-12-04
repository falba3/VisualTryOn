"use client";

import { useMemo, useState } from "react";
import styles from "./page.module.css";

type SceneResult = { id: string; title: string; src: string };

const SCENES: SceneResult[] = [
  { id: "subway", title: "Subway sprint", src: "" },
  { id: "cafe", title: "Coffee break", src: "" },
  { id: "gym", title: "Gym floor", src: "" },
];

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SceneResult[]>(() => [...SCENES]);

  const disabled = useMemo(() => isLoading || !file, [file, isLoading]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0];
    setFile(nextFile ?? null);
    setResults([...SCENES]);
    setError(null);

    if (nextFile) {
      setPreview(URL.createObjectURL(nextFile));
    } else {
      setPreview(null);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError("Select a portrait image first.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/tryon", {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(data?.error || "Failed to generate try-on scenes.");
      }

      setResults(
        SCENES.map((scene) => {
          const match = data?.images?.find((img: SceneResult) => img.id === scene.id);
          return match ? { ...scene, ...match } : { ...scene, src: "" };
        })
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <header className={styles.hero}>
          <p className={styles.eyebrow}>Visual Try-On</p>
          <h1>Generate styled scenarios from a single portrait.</h1>
          <p className={styles.lede}>
            Upload one image and we&apos;ll render the same person in three photorealistic scenes—
            perfect for quick lookbooks and social drops.
          </p>
        </header>

        <section className={styles.panel}>
          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.formHeader}>
              <div>
                <p className={styles.label}>Reference portrait</p>
                <p className={styles.hint}>Face-forward photo works best. PNG or JPG.</p>
              </div>
              <button className={styles.action} type="submit" disabled={disabled}>
                {isLoading ? "Generating..." : "Create looks"}
              </button>
            </div>

            <label className={styles.upload}>
              <input type="file" accept="image/*" onChange={handleFileChange} />
              {preview ? (
                <div className={styles.previewRow}>
                  <img src={preview} alt="Preview" className={styles.preview} />
                  <div>
                    <p className={styles.filename}>{file?.name}</p>
                    <p className={styles.hint}>Click to replace the portrait.</p>
                  </div>
                </div>
              ) : (
                <div className={styles.placeholder}>
                  <p>Drop a portrait or click to browse</p>
                  <span>We keep the face and outfit consistent across scenes.</span>
                </div>
              )}
            </label>

            {error && <p className={styles.error}>{error}</p>}
          </form>
        </section>

        <section className={styles.results}>
          <div className={styles.sectionHeader}>
            <div>
              <p className={styles.label}>Scenarios</p>
              <p className={styles.hint}>Subway sprint · Coffee break · Gym floor</p>
            </div>
            <span className={styles.status}>
              {isLoading ? "Working..." : "Ready"}
            </span>
          </div>
          <div className={styles.grid}>
            {results.map((scene) => (
              <article key={scene.id} className={styles.card}>
                <div className={styles.cardHeader}>
                  <p className={styles.cardLabel}>{scene.id}</p>
                  <p className={styles.cardTitle}>{scene.title}</p>
                </div>
                <div className={styles.cardBody}>
                  {scene.src ? (
                    <img src={scene.src} alt={scene.title} className={styles.output} />
                  ) : (
                    <div className={styles.skeleton}>
                      <span>{isLoading ? "Rendering..." : "Awaiting generation"}</span>
                    </div>
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
