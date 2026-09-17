import axios, { AxiosError } from "axios";
import { toast } from "react-toastify";
import { axiosErrorMessage } from "../utils/errorHelpers";
import { AuthOptions } from "@/auth/types";
import { authConfig } from "@/auth/api";

export type FreeAnalyzeResult = {
  intent: Record<string, unknown>;
  analyzer: Record<string, unknown>;
  ats: Record<string, unknown>;
  feedback: Record<string, unknown> | string;
};

export async function freeAnalyzeResume(
  resumePdf: File,
  jdText: string = "",
  userGoal: string = "",
  options?: AuthOptions,
): Promise<FreeAnalyzeResult | null> {
  try {
    const formData = new FormData();
    formData.append("resume_pdf", resumePdf);
    formData.append("jd_text", jdText);
    formData.append("user_goal", userGoal);

    const { data } = await axios.post<FreeAnalyzeResult>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/resume/analyze`,
      formData,
      authConfig(options),
    );
    return data;
  } catch (error: unknown) {
    console.error(error);
    const errorMessage = axiosErrorMessage(error, "Failed to analyze resume. Please try again later.");
    toast.error(errorMessage);
    console.error(errorMessage);
    return null;
  }
}

export type PremiumAnalyzeResult = {
  intent: Record<string, unknown>;
  analyzer: Record<string, unknown>;
  ats: Record<string, unknown>;
  optimizer: Record<string, unknown>;
  feedback: Record<string, unknown> | string;
  job_finder: Record<string, unknown> | unknown | null;
};

export async function premiumAnalyzeResume(
  resumePdf: File,
  jdText: string = "",
  userGoal: string = "",
  includesJobFinder: boolean = false,
  options?: AuthOptions,
): Promise<PremiumAnalyzeResult | null> {
  try {
    const formData = new FormData();
    formData.append("resume_pdf", resumePdf);
    formData.append("jd_text", jdText);
    formData.append("user_goal", userGoal);
    formData.append("includes_job_finder", includesJobFinder.toString());

    const { data } = await axios.post<PremiumAnalyzeResult>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/resume/analyze/premium`,
      formData,
      authConfig(options),
    );
    return data;
  } catch (error: unknown) {
    console.error(error);
    const errorMessage = axiosErrorMessage(error, "Failed to analyze resume. Please try again later.");
    toast.error(errorMessage);
    console.error(errorMessage);
    return null;
  }
}
