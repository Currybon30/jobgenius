"use client";

import { SyntheticEvent, useState } from "react";
import { toast } from "react-toastify";
import "./contact.css";

export function ContactForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [topic, setTopic] = useState("general");
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);

  const onSubmit = (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim() || !email.trim() || !message.trim()) {
      toast.error("Please fill in name, email, and message.");
      return;
    }

    setSending(true);
    window.setTimeout(() => {
      setSending(false);
      setName("");
      setEmail("");
      setTopic("general");
      setMessage("");
      toast.success("Message queued — we will reply soon.");
    }, 600);
  };

  return (
    <form className="contact-form" onSubmit={onSubmit} noValidate>
      <div className="contact-field">
        <label htmlFor="contact-name">Name</label>
        <input
          id="contact-name"
          name="name"
          type="text"
          autoComplete="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>

      <div className="contact-field">
        <label htmlFor="contact-email">Email</label>
        <input
          id="contact-email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="contact-field">
        <label htmlFor="contact-topic">Topic</label>
        <select
          id="contact-topic"
          name="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        >
          <option value="general">General question</option>
          <option value="support">Account support</option>
          <option value="feedback">Product feedback</option>
          <option value="press">Press / partnership</option>
        </select>
      </div>

      <div className="contact-field">
        <label htmlFor="contact-message">Message</label>
        <textarea
          id="contact-message"
          name="message"
          rows={6}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          required
        />
      </div>

      <button className="mkt-btn mkt-btn-primary contact-submit" type="submit" disabled={sending}>
        {sending ? "Sending…" : "Send message"}
      </button>
    </form>
  );
}
