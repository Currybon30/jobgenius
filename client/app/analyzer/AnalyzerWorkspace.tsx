"use client";

import { useState } from "react";
import { toast } from "react-toastify";
import {
  freeAnalyzeResume,
  premiumAnalyzeResume,
  type FreeAnalyzeResult,
  type PremiumAnalyzeResult,
} from "@/services/resumeService";
import { ResumeDropzone } from "./ResumeDropzone";
import { JobBriefPanel } from "./JobBriefPanel";
import { AnalyzerLoading } from "./AnalyzerLoading";
import { AnalyzerResults } from "./AnalyzerResults";
import { useAuth } from "@/contexts/AuthContext";

type Phase = "idle" | "loading" | "done";

export function AnalyzerWorkspace() {
  const { status, tier } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [requirements, setRequirements] = useState("");
  const [includesJobFinder, setIncludesJobFinder] = useState(false);
  const [phase, setPhase] = useState<Phase>("idle");
  const [result, setResult] = useState<FreeAnalyzeResult | PremiumAnalyzeResult | null>(null);

  async function onAnalyze() {
    if (!file) {
      toast.error("Upload a PDF resume first.");
      return;
    }

    setPhase("loading");
    setResult(null);

    try {
      if (tier?.toLowerCase() !== "premium") {
        const data = await freeAnalyzeResume(
          file,
          jobDescription.trim(),
          requirements.trim(),
        );
        setResult(data as FreeAnalyzeResult);
        setPhase("done");
      } else {
        const data = await premiumAnalyzeResume(
          file,
          jobDescription.trim(),
          requirements.trim(),
          includesJobFinder,
        );
        setResult(data as PremiumAnalyzeResult);
        setPhase("done");
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Analysis failed. Please try again.";
      toast.error(message);
      setPhase("idle");
    }
  }

  function onAnalyzeAgain() {
    setPhase("idle");
    setResult(null);
  }

  const canAnalyze = Boolean(file) && phase !== "loading";

  if (phase === "loading") {
    return <AnalyzerLoading fileName={file?.name} />;
  }

  if (phase === "done" && result) {
    return <AnalyzerResults result={result} onAnalyzeAgain={onAnalyzeAgain} />;
  }

  return (
    <div className="analyzer-workspace">
      <div className="analyzer-split" aria-label="Resume and job brief">
        <section className="analyzer-pane analyzer-pane-upload" aria-labelledby="analyzer-upload-title">
          <div className="analyzer-pane-head">
            <p className="analyzer-pane-kicker">01 · Resume</p>
            <h2 id="analyzer-upload-title" className="analyzer-pane-title">
              Your PDF
            </h2>
            <p className="analyzer-pane-lead">
              Drop the resume you want read — structure, skills, and gaps.
            </p>
          </div>
          <ResumeDropzone showActions={false} onFileChange={setFile} />
        </section>

        <div className="analyzer-split-rule" aria-hidden="true">
          <span>meets</span>
        </div>

        <section className="analyzer-pane analyzer-pane-brief" aria-labelledby="analyzer-brief-title">
          <div className="analyzer-pane-head">
            <p className="analyzer-pane-kicker">02 · Role</p>
            <h2 id="analyzer-brief-title" className="analyzer-pane-title">
              Job brief
            </h2>
            <p className="analyzer-pane-lead">
              Paste the posting and must-haves so we can score fit, not just polish.
            </p>
          </div>
          <JobBriefPanel
            jobDescription={jobDescription}
            requirements={requirements}
            includesJobFinder={includesJobFinder}
            onJobDescriptionChange={setJobDescription}
            onRequirementsChange={setRequirements}
            onIncludesJobFinderChange={setIncludesJobFinder}
            isPremium={
              status === "authenticated" && tier?.toLowerCase() === "premium"
            }
          />
        </section>
      </div>

      <div className="analyzer-workspace-footer">
        <p className="analyzer-workspace-note">
          {file
            ? `Ready with “${file.name}”${jobDescription.trim() || requirements.trim() ? " and a role brief" : ""}.`
            : "Upload a resume to unlock analysis. Role fields are optional but recommended."}
        </p>
        <button
          type="button"
          className="mkt-btn mkt-btn-primary analyzer-analyze"
          disabled={!canAnalyze}
          onClick={() => {
            void onAnalyze();
          }}
        >
          Analyze fit
        </button>
      </div>
    </div>
  );
}
