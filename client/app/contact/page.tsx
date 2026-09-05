import type { Metadata } from "next";
import "../marketing.css";
import "./contact.css";
import { ContactForm } from "@/app/contact/ContactForm";

export const metadata: Metadata = {
  title: "Contact",
  description: "Reach the JobGenius team with questions, feedback, or support requests.",
};

export default function ContactPage() {
  return (
    <div className="mkt contact">
      <header className="mkt-page-hero">
        <div className="mkt-shell">
          <p className="mkt-kicker mkt-rise">Contact</p>
          <h1 className="mkt-title mkt-rise mkt-rise-delay">
            Tell us what you need.
          </h1>
          <p className="mkt-lead mkt-rise mkt-rise-delay-2">
            Product questions, partnership ideas, or a stuck account — drop a
            note and we will get back to you.
          </p>
        </div>
      </header>

      <section className="mkt-section" aria-labelledby="contact-form-title">
        <div className="mkt-shell contact-layout">
          <div className="contact-aside">
            <h2 id="contact-form-title" className="mkt-title">
              Write to us
            </h2>
            <p className="mkt-lead">
              Prefer email? Reach us at{" "}
              <a className="contact-email" href="mailto:hello@jobgenius.app">
                hello@jobgenius.app
              </a>
            </p>
            <dl className="contact-meta">
              <div>
                <dt>Response time</dt>
                <dd>Usually within 1–2 business days</dd>
              </div>
              <div>
                <dt>Best for</dt>
                <dd>Support, feedback, and press</dd>
              </div>
            </dl>
          </div>

          <ContactForm />
        </div>
      </section>
    </div>
  );
}
