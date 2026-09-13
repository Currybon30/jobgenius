"use client";

type JobBriefPanelProps = {
  jobDescription: string;
  requirements: string;
  includesJobFinder: boolean;
  onJobDescriptionChange: (value: string) => void;
  onRequirementsChange: (value: string) => void;
  onIncludesJobFinderChange: (value: boolean) => void;
  isPremium: boolean;
};

export function JobBriefPanel({
  jobDescription,
  requirements,
  includesJobFinder,
  onJobDescriptionChange,
  onRequirementsChange,
  onIncludesJobFinderChange,
  isPremium,
}: JobBriefPanelProps) {
  const jdCount = jobDescription.trim().length;
  const reqCount = requirements.trim().length;

  return (
    <div className="analyzer-brief">
      <label className="analyzer-brief-field" htmlFor="analyzer-job-description">
        <span className="analyzer-brief-label-row">
          <span className="analyzer-brief-label">Job description</span>
          <span className="analyzer-brief-count" aria-live="polite">
            {jdCount > 0 ? `${jdCount.toLocaleString()} chars` : "Text only"}
          </span>
        </span>
        <textarea
          id="analyzer-job-description"
          className="analyzer-brief-input"
          rows={9}
          value={jobDescription}
          onChange={(event) => onJobDescriptionChange(event.target.value)}
          placeholder="Paste the full job posting here — responsibilities, stack, team, and tone."
          spellCheck
        />
      </label>

      <label className="analyzer-brief-field" htmlFor="analyzer-requirements">
        <span className="analyzer-brief-label-row">
          <span className="analyzer-brief-label">Your requirements</span>
          <span className="analyzer-brief-count" aria-live="polite">
            {reqCount > 0 ? `${reqCount.toLocaleString()} chars` : "Must-haves"}
          </span>
        </span>
        <textarea
          id="analyzer-requirements"
          className="analyzer-brief-input analyzer-brief-input-sm"
          rows={6}
          value={requirements}
          onChange={(event) => onRequirementsChange(event.target.value)}
          placeholder="What must this role include? e.g. remote, seniority, salary floor, visa, stack you refuse to leave…"
          spellCheck
        />
      </label>

      {isPremium ? (
        <div className="analyzer-toggle-row">
          <div className="analyzer-toggle-copy">
            <p className="analyzer-toggle-title">Include job finder</p>
            <p className="analyzer-toggle-lead">
              Match roles to your resume after analysis — Premium only.
            </p>
          </div>
          <button
            type="button"
            id="analyzer-job-finder"
            className={`analyzer-switch${includesJobFinder ? " is-on" : ""}`}
            role="switch"
            aria-checked={includesJobFinder}
            aria-label="Include job finder"
            onClick={() => onIncludesJobFinderChange(!includesJobFinder)}
          >
            <span className="analyzer-switch-track" aria-hidden="true">
              <span className="analyzer-switch-thumb" />
            </span>
            <span className="analyzer-switch-state">
              {includesJobFinder ? "On" : "Off"}
            </span>
          </button>
        </div>
      ) : null}
    </div>
  );
}
