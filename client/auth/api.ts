import axios from "axios";
import { AuthOptions, LoginRequest, RegisterRequest } from "./types";

const authConfig = (options?: AuthOptions) => ({
    signal: options?.signal,
    withCredentials: options?.withCredentials ?? true,
});

export async function handleLogin(
    loginRequest: LoginRequest,
    options?: AuthOptions,
): Promise<void> {
    await axios.post(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL }/auth/login`,
        loginRequest,
        authConfig(options),
    );
}

export async function handleRegister(
    registerRequest: RegisterRequest,
    options?: AuthOptions,
): Promise<void> {
    await axios.post(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL }/auth/register`,
        registerRequest,
        authConfig(options),
    );
}

export async function getCurrentUser(): Promise<unknown> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL }/api/users/me`,
        { withCredentials: true },
    );
    return data;
}

export async function handleLogout(): Promise<void> {
    await axios.post(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL }/auth/logout`,
        {},
        { withCredentials: true },
    );
}