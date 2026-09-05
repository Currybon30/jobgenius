import type { Metadata } from "next";
import Link from "next/link";
import "../marketing.css";
import "./faqs.css";

export const metadata: Metadata = {
  title: "FAQs",
  description: "Answers to common questions about JobGenius accounts, resumes, and matching.",
};

const FAQS = [
  {
    q: "What is JobGenius?",
    a: "JobGenius is an AI career workspace. It analyzes your resume, highlights what to improve, and helps match you with roles that fit your experience.",
  },
  {
    q: "Is there a free plan?",
    a: "Yes. You can create a free account and explore core features. Premium unlocks deeper analysis and matching when you are ready.",
  },
  {
    q: "Do I need an account to try it?",
    a: "You can browse the product pages freely. Resume analysis and saved progress require signing in so we can keep your work secure.",
  },
  {
    q: "What file types can I upload?",
    a: "PDF resumes work best. Keep your file readable (not a scanned image) so the analyzer can extract skills and experience accurately.",
  },
  {
    q: "How does role matching work?",
    a: "We compare the skills and experience in your profile against open roles, then surface matches with clearer fit — not every job on the internet.",
  },
  {
    q: "Is my resume private?",
    a: "Your documents are used to power your analysis and matches. We do not sell your resume data. You can contact us anytime about account or data questions.",
  },
  {
    q: "I found a bug or the AI got something wrong.",
    a: "It happens. Send details through the Contact page — screenshots and the resume section that looked off help us improve fastest.",
  },
] as const;

export default function FaqsPage() {
  return (
    <div className="mkt faqs">
      <header className="mkt-page-hero">
        <div className="mkt-shell">
          <p className="mkt-kicker mkt-rise">FAQs</p>
          <h1 className="mkt-title mkt-rise mkt-rise-delay">
            Straight answers.
          </h1>
          <p className="mkt-lead mkt-rise mkt-rise-delay-2">
            Quick clarity on accounts, resumes, matching, and privacy. Still
            stuck?{" "}
            <Link href="/contact" className="faqs-inline-link">
              Contact us
            </Link>
            .
          </p>
        </div>
      </header>

      <section className="mkt-section" aria-label="Frequently asked questions">
        <div className="mkt-shell faqs-list">
          {FAQS.map(({ q, a }) => (
            <details key={q} className="faqs-item">
              <summary>{q}</summary>
              <p>{a}</p>
            </details>
          ))}
        </div>
      </section>
    </div>
  );
}
