import Link from "next/link";
import "./error.css";

type ErrorContentProps = {
  heading?: string;
};

export function ErrorContent({
  heading = "Oops! Something went wrong!",
}: ErrorContentProps) {
  return (
    <div className="error-container">
      <div className="face">
        <div className="band">
          <div className="red" />
          <div className="white" />
          <div className="blue" />
        </div>
        <div className="eyes" />
        <div className="dimples" />
        <div className="mouth" />
      </div>

      <h1>{heading}</h1>
      {heading !== "404 — Page not found" ? (
        <Link href="/" className="not-found-home-link">
          Back to JobGenius
        </Link>
      ) : null}
    </div>
  );
}
