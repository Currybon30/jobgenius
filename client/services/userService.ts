import axios from "axios";
import { authConfig } from "../auth/api";

export async function getAllUsers(): Promise<unknown> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/users`,
        authConfig(),
    );
    return data;
}

export async function getCurrentUser(): Promise<unknown> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL}/api/users/me`,
        authConfig(),
    );
    return data;
}

export async function getUserPlan(): Promise<string> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_FASTAPI_API_URL}/api/users/me`,
        authConfig(),
    );
    return data.plan as string;
}