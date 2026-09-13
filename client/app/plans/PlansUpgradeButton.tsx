"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { useAuth } from "@/contexts/AuthContext";
import { createCheckoutSession } from "@/services/paymentService";

type PlansUpgradeButtonProps = {
  className?: string;
  label?: string;
};

export function PlansUpgradeButton({
  className = "mkt-btn mkt-btn-primary plans-cta",
  label = "Go Premium",
}: PlansUpgradeButtonProps) {
  const { status, tier } = useAuth();
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  const isPremium = tier?.toLowerCase() === "premium";

  async function onUpgrade() {
    if (status !== "authenticated") {
      toast.info("Sign in to upgrade to Premium.");
      router.push("/login");
      return;
    }
    if (isPremium) {
      toast.info("You're already on Premium.");
      return;
    }

    setBusy(true);
    try {
      const origin = window.location.origin;
      const url = await createCheckoutSession(
        `${origin}/payment/success`,
        `${origin}/plans`,
      );
      window.location.href = url;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Could not start checkout.";
      toast.error(message);
      setBusy(false);
    }
  }

  if (isPremium) {
    return (
      <span className="plans-cta-current" aria-live="polite">
        Your current plan
      </span>
    );
  }

  return (
    <button
      type="button"
      className={className}
      disabled={busy}
      onClick={() => {
        void onUpgrade();
      }}
    >
      {busy ? "Opening Stripe…" : label}
    </button>
  );
}
