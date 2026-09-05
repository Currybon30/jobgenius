import type { Metadata } from "next";
import Link from "next/link";
import "../marketing.css";
import "./about.css";

export const metadata: Metadata = {
  title: "About",
  description:
    "Learn why JobGenius exists — clearer resumes, smarter matches, calmer job search.",
};

export default function AboutPage() {
  return (
    <div className="mkt about">
      <header className="mkt-page-hero">
        <div className="mkt-shell">
          <p className="mkt-kicker mkt-rise">About</p>
          <h1 className="mkt-title mkt-rise mkt-rise-delay">
            We built JobGenius for people tired of guessing.
          </h1>
          <p className="mkt-lead mkt-rise mkt-rise-delay-2">
            The job market rewards clarity. We help you find yours — in your
            resume, your story, and the roles worth chasing.
          </p>
        </div>
      </header>

      <section className="mkt-section" aria-labelledby="about-why">
        <div className="mkt-shell about-split">
          <h2 id="about-why" className="mkt-title">
            Why we exist
          </h2>
          <div className="about-prose">
            <p>
              Most job tools either dump endless listings on you or rewrite your
              resume into something generic. JobGenius sits in the middle: it
              reads what you already have, tells you what is working, and
              points you toward roles that actually fit.
            </p>
            <p>
              We believe AI should feel like a sharp mentor — direct, useful,
              and respectful of your time — not another dashboard full of noise.
            </p>
          </div>
        </div>
      </section>

      <section className="mkt-section about-values" aria-labelledby="about-values">
        <div className="mkt-shell">
          <p className="mkt-kicker">What we care about</p>
          <h2 id="about-values" className="mkt-title">
            Principles we ship by
          </h2>
          <ul className="about-value-list">
            <li>
              <strong>Honesty over hype</strong>
              <span>Feedback you can act on — not empty praise.</span>
            </li>
            <li>
              <strong>Signal over volume</strong>
              <span>Fewer, better matches beat endless scrolling.</span>
            </li>
            <li>
              <strong>Your story stays yours</strong>
              <span>AI assists; it does not erase your voice.</span>
            </li>
          </ul>
        </div>
      </section>

      <section className="mkt-section" aria-labelledby="about-next">
        <div className="mkt-shell about-next">
          <h2 id="about-next" className="mkt-title">
            Want to talk?
          </h2>
          <p className="mkt-lead">
            Questions, ideas, or feedback — we read every message.
          </p>
          <div className="mkt-cta-row">
            <Link href="/contact" className="mkt-btn mkt-btn-primary">
              Contact us
            </Link>
            <Link href="/faqs" className="mkt-btn mkt-btn-ghost">
              Browse FAQs
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
