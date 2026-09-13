import axios from "axios";
import { authConfig } from "@/auth/api"
import { AuthOptions } from "@/auth/types";

export type UsageResponse = {
    usage: number;
    remaining_time: number;
};

export async function getAnalyzerUsage(options?: AuthOptions): Promise<UsageResponse> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/usage/analyzer`,
        authConfig(options),
    );
    return data as UsageResponse;
}

export async function getJobFinderUsage(options?: AuthOptions): Promise<UsageResponse> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/usage/job-finder`,
        authConfig(options),
    );
    return data as UsageResponse;
}