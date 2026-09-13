import axios from "axios";
import { authConfig } from "../auth/api";

export async function jobSearchWithPrompt(
    resumePdf: File,
    prompt: string
): Promise<unknown> {
  const formData = new FormData();
  formData.append("resume_pdf", resumePdf);
  formData.append("prompt", prompt);
  const { data } = await axios.post<unknown>(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/job/search/with/prompt`,
    formData,
    authConfig({ timeout: 180_000 }),
  );
  return data;
}

const HEADERS = {
  "client-ip-address": process.env.NEXT_PUBLIC_CLIENT_IP_ADDRESS || "",
} as Record<string, string>;

export async function getJobRecommendationsUnloggedInUser(): Promise<unknown> {
  const { data } = await axios.get<unknown>(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/recommendations`,
    authConfig({ timeout: 180_000, headers: HEADERS }),
  );
  return data;
}

export async function getJobRecommendationsFreeUser(
  target_role: string = "any job",
  seniority_level: string = "any level",
): Promise<unknown> {
  const params = new URLSearchParams();
  if (target_role !== "any job") params.append("target_role", target_role);
  if (seniority_level !== "any level") params.append("seniority_level", seniority_level);
  const { data } = await axios.get<unknown>(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/recommendations/free?${params.toString()}`,
    authConfig({ timeout: 180_000, headers: HEADERS }),
  );
  return data;
}

export async function getJobRecommendationsPremiumUser(
  resume_id: string = "",
): Promise<unknown> {
  const params = new URLSearchParams();
  if (resume_id !== "") params.append("resume_id", resume_id);
  const { data } = await axios.get<unknown>(
    `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/recommendations/premium?${params.toString()}`,
    authConfig({ timeout: 180_000, headers: HEADERS }),
  );
  return data;
}