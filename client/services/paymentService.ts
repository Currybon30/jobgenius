import axios from "axios";
import { authConfig } from "../auth/api";

export async function createCheckoutSession(
  successUrl: string,
  cancelUrl: string,
): Promise<string> {
  const { data } = await axios.post<{ checkoutUrl: string }>(
    `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/payments/create-checkout-session`,
    { successUrl, cancelUrl },
    authConfig({ timeout: 15_000 }),
  );
  return data.checkoutUrl;
}


export async function cancelSubscription(): Promise<string> {
  const { data } = await axios.post<{ message: string }>(
    `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/payments/cancel-subscription`,
    authConfig({ timeout: 15_000 }),
  );
  return data.message;
}