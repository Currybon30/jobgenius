import { ErrorContent } from "./error/ErrorContent"; // This already has the error.css imported

export default function NotFound() {
  return (
    <div className="not-found-wrapper">
      <ErrorContent heading="404 — Page not found" />
      <p className="not-found-message">
        The page you are looking for does not exist or has been moved.
      </p>
    </div>
  );
}
