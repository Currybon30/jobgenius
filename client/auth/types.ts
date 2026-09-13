export type LoginRequest = {
    email: string;
    password: string;
};

export type RegisterRequest = {
    name: string;
    email: string;
    password: string;
};

export type AuthOptions = {
    signal?: AbortSignal;
    withCredentials?: boolean;
    timeout?: number;
    headers?: Record<string, string>;
};