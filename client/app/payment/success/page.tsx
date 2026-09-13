import type { Metadata } from "next";
import "../../marketing.css";
import "./success.css";
import { PaymentSuccessExperience } from "./PaymentSuccessExperience";

export const metadata: Metadata = {
  title: "Premium activated",
  description: "Your JobGenius Premium subscription is active.",
};

export default function PaymentSuccessPage() {
  return (
    <div className="mkt">
      <PaymentSuccessExperience />
    </div>
  );
}
