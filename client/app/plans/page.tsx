import type { Metadata } from "next";
import Link from "next/link";
import "../marketing.css";
import "./plans.css";
import { PlansUpgradeButton } from "./PlansUpgradeButton";

export const metadata: Metadata = {
  title: "Plans",
  description:
    "Choose Basic free or Premium at CAD $20/month — clearer resumes, sharper matches, deeper coaching.",
};

const BASIC_FEATURES = [
  {
    title: "Resume read that cuts the fog",
    body: "Intent, structure, skills, and ATS scores — plus general feedback you can act on tonight.",
  },
  {
    title: "Fit against a job post",
    body: "Paste a description and see missing skills and match scores without selling your soul for a login wall.",
  },
  {
    title: "Local job pulse",
    body: "Recommendations shaped by where you are (and your industry when signed in) — calm, not a firehose.",
  },
  {
    title: "Prompt job search, sparingly",
    body: "One guided search every 15 days when you’re logged in — enough to scout, not spam.",
  },
] as const;

const PREMIUM_FEATURES = [
  {
    title: "The full coaching stack",
    body: "Everything in Basic, then certifications, languages, links, volunteer signals, and richer ATS bonuses.",
  },
  {
    title: "Rewritten, not just reviewed",
    body: "The optimizer returns a stronger draft with keyword notes and what actually changed.",
  },
  {
    title: "Recruiter-grade feedback",
    body: "Strengths, growth edges, JD fit, interview talking points, and a priority action plan — not five vague bullets.",
  },
  {
    title: "Job finder on demand",
    body: "Toggle roles into your analysis, or run prompt search every 3 days — fresher than Basic’s cadence.",
  },
  {
    title: "Saved analyses & smarter matches",
    body: "Premium runs land in your history; recommendations lean on your resume via vector search, refreshed every few days.",
  },
  {
    title: "Room to iterate",
    body: "Up to three premium analyses per day — ship, tweak, re-run before the interview.",
  },
] as const;

export default function PlansPage() {
  return (
    <div className="mkt plans">
      <header className="plans-hero">
        <div className="plans-hero-atmosphere" aria-hidden="true" />
        <div className="mkt-shell plans-hero-inner">
          <p className="plans-brand mkt-rise">JobGenius</p>
          <h1 className="plans-headline mkt-rise mkt-rise-delay">
            Pick the altitude for your search.
          </h1>
          <p className="plans-support mkt-rise mkt-rise-delay-2">
            Basic keeps the runway clear. Premium puts a sharper mentor in the cockpit —
            rewrite, coach, and chase roles that actually fit.
          </p>
        </div>
      </header>

      <section className="plans-stage" aria-label="Plan comparison">
        <div className="mkt-shell plans-grid">
          <article className="plans-tier plans-tier-basic mkt-rise">
            <p className="plans-tier-kicker">Starter</p>
            <h2 className="plans-tier-name">Basic</h2>
            <p className="plans-tier-price">
              <span className="plans-tier-amount">Free</span>
              <span className="plans-tier-period">forever</span>
            </p>
            <p className="plans-tier-lead">
              Honest signals for your resume and a quieter way to scout roles — no card, no
              guilt trip.
            </p>
            <ul className="plans-feature-list">
              {BASIC_FEATURES.map((feature) => (
                <li key={feature.title}>
                  <strong>{feature.title}</strong>
                  <span>{feature.body}</span>
                </li>
              ))}
            </ul>
            <Link href="/analyzer" className="mkt-btn mkt-btn-ghost plans-cta">
              Try the analyzer
            </Link>
          </article>

          <article className="plans-tier plans-tier-premium mkt-rise mkt-rise-delay">
            <p className="plans-tier-badge">Most chosen</p>
            <p className="plans-tier-kicker">Full stack</p>
            <h2 className="plans-tier-name">Premium</h2>
            <p className="plans-tier-price">
              <span className="plans-tier-amount">CAD&nbsp;$20</span>
              <span className="plans-tier-period">/ month</span>
            </p>
            <p className="plans-tier-lead">
              For the stretch interview — deeper reads, an optimized draft, and matches that
              remember your resume.
            </p>
            <ul className="plans-feature-list">
              {PREMIUM_FEATURES.map((feature) => (
                <li key={feature.title}>
                  <strong>{feature.title}</strong>
                  <span>{feature.body}</span>
                </li>
              ))}
            </ul>
            <PlansUpgradeButton />
            <p className="plans-tier-footnote">
              14-day trial on checkout · cancel anytime before the next bill
            </p>
          </article>
        </div>
      </section>

      <section className="plans-footnote-section" aria-labelledby="plans-compare">
        <div className="mkt-shell plans-footnote-inner">
          <h2 id="plans-compare" className="plans-footnote-title">
            Same compass. Different altitude.
          </h2>
          <p className="plans-footnote-copy">
            Both plans use the same JobGenius brain — Premium just turns on the deeper agents,
            saves your analyses, and refreshes job matches more often. Start free; climb when
            the stakes get real.
          </p>
          <div className="mkt-cta-row">
            <Link href="/faqs" className="mkt-btn mkt-btn-ghost">
              Read FAQs
            </Link>
            <Link href="/contact" className="mkt-btn mkt-btn-ghost">
              Ask a question
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
