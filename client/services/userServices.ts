import axios from "axios";

export async function getCurrentUser(): Promise<unknown> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_SPRING_API_URL }/api/users/me`,
        { withCredentials: true },
    );
    return data;
}

export async function getUserPlan(): Promise<string> {
    const { data } = await axios.get(
        `${process.env.NEXT_PUBLIC_FASTAPI_API_URL }/api/users/me`,
        { withCredentials: true },
    );
    return data.plan as string;
}