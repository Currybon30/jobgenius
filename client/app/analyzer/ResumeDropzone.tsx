"use client";

import { useId, useRef, useState, type ChangeEvent, type DragEvent } from "react";

const MAX_BYTES = 8 * 1024 * 1024;

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isPdf(file: File) {
  return (
    file.type === "application/pdf" ||
    file.name.toLowerCase().endsWith(".pdf")
  );
}

type ResumeDropzoneProps = {
  showActions?: boolean;
  onFileChange?: (file: File | null) => void;
  onAnalyze?: (file: File) => void;
};

export function ResumeDropzone({
  showActions = true,
  onFileChange,
  onAnalyze,
}: ResumeDropzoneProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function acceptFile(next: File | null) {
    if (!next) {
      setFile(null);
      setError(null);
      onFileChange?.(null);
      return;
    }

    if (!isPdf(next)) {
      setFile(null);
      setError("Please upload a PDF resume.");
      onFileChange?.(null);
      return;
    }

    if (next.size > MAX_BYTES) {
      setFile(null);
      setError("That file is larger than 8 MB. Try a lighter PDF.");
      onFileChange?.(null);
      return;
    }

    setError(null);
    setFile(next);
    onFileChange?.(next);
  }

  function onDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    event.stopPropagation();
    if (!dragging) setDragging(true);
  }

  function onDragLeave(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    event.stopPropagation();
    const next = event.relatedTarget as Node | null;
    if (next && event.currentTarget.contains(next)) return;
    setDragging(false);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    event.stopPropagation();
    setDragging(false);
    const dropped = event.dataTransfer.files?.[0] ?? null;
    acceptFile(dropped);
  }

  function onChange(event: ChangeEvent<HTMLInputElement>) {
    const chosen = event.target.files?.[0] ?? null;
    acceptFile(chosen);
    event.target.value = "";
  }

  function clearFile() {
    acceptFile(null);
    inputRef.current?.focus();
  }

  function handleAnalyze() {
    if (!file) return;
    onAnalyze?.(file);
  }

  const zoneClass = [
    "analyzer-dropzone",
    dragging ? "is-dragging" : "",
    file ? "has-file" : "",
    error ? "has-error" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="analyzer-upload">
      <div
        className={zoneClass}
        role="button"
        tabIndex={0}
        aria-controls={inputId}
        aria-describedby="analyzer-drop-hint"
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            inputRef.current?.click();
          }
        }}
      >
        <div className="analyzer-dropzone-glow" aria-hidden="true" />
        <div className="analyzer-dropzone-orbit" aria-hidden="true" />

        <div className="analyzer-dropzone-icon" aria-hidden="true">
          <svg viewBox="0 0 88 104" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect
              x="8"
              y="4"
              width="72"
              height="96"
              rx="12"
              fill="#ffffff"
              stroke="rgba(37,99,235,0.28)"
              strokeWidth="2"
            />
            <path d="M52 4 V24 H72" stroke="rgba(37,99,235,0.35)" strokeWidth="2" />
            <rect x="22" y="40" width="44" height="8" rx="4" fill="#2563eb" opacity="0.9" />
            <rect x="22" y="56" width="36" height="6" rx="3" fill="#94a3b8" opacity="0.55" />
            <rect x="22" y="68" width="40" height="6" rx="3" fill="#94a3b8" opacity="0.4" />
            <rect x="22" y="80" width="28" height="6" rx="3" fill="#94a3b8" opacity="0.3" />
          </svg>
          <span className="analyzer-dropzone-badge">PDF</span>
        </div>

        <div className="analyzer-dropzone-copy">
          {file ? (
            <>
              <p className="analyzer-dropzone-title">Resume ready</p>
              <p className="analyzer-dropzone-file">
                <span className="analyzer-dropzone-filename">{file.name}</span>
                <span className="analyzer-dropzone-size">{formatBytes(file.size)}</span>
              </p>
            </>
          ) : (
            <>
              <p className="analyzer-dropzone-title">
                {dragging ? "Drop it here" : "Drag & drop your resume"}
              </p>
              <p className="analyzer-dropzone-sub">
                or <span>click to browse</span> — PDF only, up to 8 MB
              </p>
            </>
          )}
        </div>

        <input
          ref={inputRef}
          id={inputId}
          className="analyzer-dropzone-input"
          type="file"
          accept="application/pdf,.pdf"
          onChange={onChange}
          onClick={(event) => event.stopPropagation()}
        />
      </div>

      <p id="analyzer-drop-hint" className="analyzer-hint">
        Keep it text-based (not a scanned image) so skills and experience extract cleanly.
      </p>

      {error ? (
        <p className="analyzer-error" role="alert">
          {error}
        </p>
      ) : null}

      {showActions ? (
        <div className="analyzer-actions">
          {file ? (
            <button
              type="button"
              className="mkt-btn mkt-btn-ghost analyzer-clear"
              onClick={clearFile}
            >
              Choose another
            </button>
          ) : null}
          <button
            type="button"
            className="mkt-btn mkt-btn-primary analyzer-analyze"
            disabled={!file}
            onClick={handleAnalyze}
          >
            Analyze resume
          </button>
        </div>
      ) : file ? (
        <div className="analyzer-actions">
          <button
            type="button"
            className="mkt-btn mkt-btn-ghost analyzer-clear"
            onClick={clearFile}
          >
            Choose another
          </button>
        </div>
      ) : null}
    </div>
  );
}
