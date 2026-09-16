import axios, { AxiosError } from "axios";
import { authConfig } from "@/auth/api"
import { AuthOptions } from "@/auth/types";
import { toast } from "react-toastify";

export type UsageResponse = {
    usage: number;
    remaining_time: number;
};

export async function getAnalyzerUsage(options?: AuthOptions): Promise<UsageResponse> {
    try {
        const { data } = await axios.get(
            `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/usage/analyzer`,
            authConfig(options),
        );
        return data as UsageResponse;
    } catch (error) {
        console.error(error);
        if (error instanceof AxiosError && error.response?.status === 400) {
            toast.error(error.response.data.detail);
        } else {
            toast.error("Failed to get analyzer usage. Please try again later.");
        }
        throw error;
    }
}

export async function getJobFinderUsage(options?: AuthOptions): Promise<UsageResponse> {
    try {
        const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/usage/job-finder`,
        authConfig(options),
        );
        return data as UsageResponse;
    } catch (error) {
        console.error(error);
        if (error instanceof AxiosError && error.response?.status === 400) {
            toast.error(error.response.data.detail);
        } else {
            toast.error("Failed to get job finder usage. Please try again later.");
        }
        throw error;
    }
}