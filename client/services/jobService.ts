import axios, { AxiosError } from "axios";
import { authConfig } from "../auth/api";
import { toast } from "react-toastify";

export async function jobSearchWithPrompt(
    resumePdf: File,
    prompt: string
): Promise<unknown> {
  try {
    const formData = new FormData();
    formData.append("resume_pdf", resumePdf);
    formData.append("prompt", prompt);
    const { data } = await axios.post<unknown>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/job/search/with/prompt`,
      formData,
      authConfig({ timeout: 180_000 }),
    );
    return data;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to search for jobs. Please try again later.");
    }
    throw error;
  }
}

const HEADERS = {
  "client-ip-address": process.env.NEXT_PUBLIC_CLIENT_IP_ADDRESS || "",
} as Record<string, string>;

export async function getJobRecommendationsUnloggedInUser(): Promise<unknown> {
  try {
    const { data } = await axios.get<unknown>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/recommendations`,
        authConfig({ timeout: 180_000, headers: HEADERS }),
      );
      return data;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to get job recommendations. Please try again later.");
    }
    throw error;
  }
}

export async function getJobRecommendationsFreeUser(
  target_role: string = "any job",
  seniority_level: string = "",
): Promise<unknown> {
  try {
    const params = new URLSearchParams();
    if (target_role !== "any job" && target_role !== "") params.append("target_role", target_role);
    if (seniority_level !== "") params.append("seniority_level", seniority_level);
    const { data } = await axios.get<unknown>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/recommendations/free?${params.toString()}`,
      authConfig({ timeout: 180_000, headers: HEADERS }),
    );
    return data;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to get job recommendations. Please try again later.");
    }
    throw error;
  }
}

export async function getJobRecommendationsPremiumUser(
  resume_id: string = "",
  target_role: string = "any job",
  seniority_level: string = "",
): Promise<unknown> {
  try {
    const params = new URLSearchParams();
    if (resume_id !== "") params.append("resume_id", resume_id);
    if (target_role !== "any job" && target_role !== "") params.append("target_role", target_role);
    if (seniority_level !== "") params.append("seniority_level", seniority_level);
    const { data } = await axios.get<unknown>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/recommendations/premium?${params.toString()}`,
      authConfig({ timeout: 180_000, headers: HEADERS }),
    );
    return data;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to get job recommendations. Please try again later.");
    }
    throw error;
  }
}