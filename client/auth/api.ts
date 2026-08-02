import axios from "axios";
import { AuthOptions, LoginRequest, RegisterRequest } from "./types";

const authConfig = (options?: AuthOptions) => ({
    signal: options?.signal,
    withCredentials: options?.withCredentials ?? true,
});

export async function handleAnonymousReady(): Promise<void> {
    try {
        await axios.get(
            `${process.env.NEXT_PUBLIC_SPRING_API_URL}/auth/anonymous_ready`,
            { withCredentials: true },
        );
    }
    catch (error: unknown) {
        if (axios.isAxiosError(error) && error.response?.status === 429) {
            throw new Error("Too many requests. Please try again later.");
        }
        else if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.message || error.message);
        }
        else if (error instanceof Error) {
            throw new Error(error.message);
        }
        else {
            throw new Error("An unknown error occurred.");
        }
    }
}

export async function handleLogin(
    loginRequest: LoginRequest,
    options?: AuthOptions,
): Promise<void> {
    try {
        await axios.post(
            `${process.env.NEXT_PUBLIC_SPRING_API_URL}/auth/login`,
            loginRequest,
            authConfig(options),
        );
    }
    catch (error: unknown) {
        if (axios.isAxiosError(error) && error.response?.status === 429) {
            throw new Error("Too many requests. Please try again later.");
        }
        else if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.message || error.message);
        }
        else if (error instanceof Error) {
            throw new Error(error.message);
        }
        else {
            throw new Error("An unknown error occurred.");
        }
    }
}

export async function handleRegister(
    registerRequest: RegisterRequest,
    options?: AuthOptions,
): Promise<void> {
    try {
        await axios.post(
            `${process.env.NEXT_PUBLIC_SPRING_API_URL}/auth/register`,
            registerRequest,
            authConfig(options),
        );
    }
    catch (error: unknown) {
        if (axios.isAxiosError(error) && error.response?.status === 429) {
            throw new Error("Too many requests. Please try again later.");
        }
        else if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.message || error.message);
        }
        else if (error instanceof Error) {
            throw new Error(error.message);
        }
        else {
            throw new Error("An unknown error occurred.");
        }
    }
}

export async function handleRefreshToken(): Promise<void> {
    try {
        await axios.post(
            `${process.env.NEXT_PUBLIC_SPRING_API_URL}/auth/refresh`,
            {},
            { withCredentials: true },
        )
    }
    catch (error: unknown) {
        if (axios.isAxiosError(error) && error.response?.status === 429) {
            throw new Error("Too many requests. Please try again later.");
        }
        else if (axios.isAxiosError(error)) {
            throw new Error(error.response?.data?.message || error.message);
        }
        else if (error instanceof Error) {
            throw new Error(error.message);
        }
        else {
            throw new Error("An unknown error occurred.");
        }
    }
}
export async function handleLogout(): Promise<void> {
    await axios.post(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL}/auth/logout`,
        {},
        { withCredentials: true },
    );
}