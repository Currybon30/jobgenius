import axios, { AxiosError } from "axios";
import { authConfig } from "../auth/api";
import { toast } from "react-toastify";

export async function getAllUsers(): Promise<unknown> {
    try {
        const { data } = await axios.get(
            `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/users`,
            authConfig(),
        );
        return data;
    } catch (error) {
        console.error(error);
        if (error instanceof AxiosError && error.response?.status === 400) {
            toast.error(error.response.data.detail);
        } else {
            toast.error("Failed to get all users. Please try again later.");
        }
        throw error;
    }
}

export async function getCurrentUser(): Promise<unknown> {
    try {
        const { data } = await axios.get(
            `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/users/me`,
            authConfig(),
        );
        return data;
    } catch (error) {
        console.error(error);
        throw error;
    }
}

export async function getUserPlan(): Promise<string> {
    try {
        const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/users/me`,
        authConfig(),
        );
        return data.plan as string;
    } catch (error) {
        console.error(error);
        throw error;
    }
}