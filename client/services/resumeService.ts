import axios, { AxiosError } from "axios";
import { toast } from "react-toastify";

export type FreeAnalyzeResult = {
  intent: Record<string, unknown>;
  analyzer: Record<string, unknown>;
  ats: Record<string, unknown>;
  feedback: Record<string, unknown> | string;
};

function axiosErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message : "Request failed.";
  }
  const data = error.response?.data as
    | { detail?: string | { msg?: string }[]; message?: string }
    | undefined;
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  if (typeof data?.message === "string") return data.message;
  return error.message || "Request failed.";
}

export async function freeAnalyzeResume(
  resumePdf: File,
  jdText: string = "",
  userGoal: string = "",
): Promise<FreeAnalyzeResult> {
  try {
    const formData = new FormData();
    formData.append("resume_pdf", resumePdf);
    formData.append("jd_text", jdText);
    formData.append("user_goal", userGoal);

    const { data } = await axios.post<FreeAnalyzeResult>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/resume/analyze`,
      formData,
      {
        withCredentials: true,
        timeout: 180_000,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return data;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to analyze resume. Please try again later.");
    }
    throw error;
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
): Promise<PremiumAnalyzeResult> {
  try {
    const formData = new FormData();
    formData.append("resume_pdf", resumePdf);
    formData.append("jd_text", jdText);
    formData.append("user_goal", userGoal);
    formData.append("includes_job_finder", includesJobFinder.toString());

    const { data } = await axios.post<PremiumAnalyzeResult>(
      `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/resume/analyze/premium`,
      formData,
      {
        withCredentials: true,
        timeout: 270_000,
        headers: {
          "Content-Type": "multipart/form-data",
        },
      },
    );
    return data;
  } catch (error) {
    console.error(error);
    if (error instanceof AxiosError && error.response?.status === 400) {
      toast.error(error.response.data.detail);
    } else {
      toast.error("Failed to analyze resume. Please try again later.");
    }
    throw error;
  }
}
