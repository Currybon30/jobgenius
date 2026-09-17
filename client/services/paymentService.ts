import axios, { AxiosError } from "axios";
import { authConfig } from "../auth/api";
import { toast } from "react-toastify";
import { AuthOptions } from "@/auth/types";
import { axiosErrorMessage } from "@/utils/errorHelpers";

export async function createCheckoutSession(
  successUrl: string,
  cancelUrl: string,
  options?: AuthOptions,
): Promise<string | null> {
  try {
    const { data } = await axios.post<{ checkoutUrl: string }>(
      `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/payments/create-checkout-session`,
      { successUrl, cancelUrl },
      authConfig(options),
    );
    return data.checkoutUrl;
  } catch (error: unknown) {
    const errorMessage = axiosErrorMessage(error, "Failed to create checkout session. Please try again later.");
    toast.error(errorMessage);
    console.error(errorMessage);
    return null;
  }
}


export async function cancelSubscription(): Promise<string | null> {
  try {
    const { data } = await axios.post<{ message: string }>(
      `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/payments/cancel-subscription`,
      authConfig({ timeout: 15_000 }),
    );
    return data.message;
  } catch (error: unknown) {
    const errorMessage = axiosErrorMessage(error, "Failed to cancel subscription. Please try again later.");
    toast.error(errorMessage);
    console.error(errorMessage);
    return null;
  }
}