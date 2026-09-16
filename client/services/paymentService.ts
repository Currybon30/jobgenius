import axios, { AxiosError } from "axios";
import { authConfig } from "../auth/api";
import { toast } from "react-toastify";

export async function createCheckoutSession(
  successUrl: string,
  cancelUrl: string,
): Promise<string> {
  try {
    const { data } = await axios.post<{ checkoutUrl: string }>(
      `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/payments/create-checkout-session`,
      { successUrl, cancelUrl },
      authConfig({ timeout: 15_000 }),
    );
    return data.checkoutUrl;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to create checkout session. Please try again later.");
    }
    throw error;
  }
}


export async function cancelSubscription(): Promise<string> {
  try {
    const { data } = await axios.post<{ message: string }>(
      `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/payments/cancel-subscription`,
      authConfig({ timeout: 15_000 }),
    );
    return data.message;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to cancel subscription. Please try again later.");
    }
    throw error;
  }
}