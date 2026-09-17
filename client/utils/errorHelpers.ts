import axios, { AxiosError } from "axios";

export function axiosErrorMessage(error: unknown, defaultMessage: string = "An unknown error occurred. Please try again later."): string {
    if (!axios.isAxiosError(error)) {
      return error instanceof Error ? error.message : "Request failed.";
    }
    if (error instanceof AxiosError && error.response?.status === 400) {
        return error.response.data.detail;
    }
    if (error instanceof AxiosError && error.response?.status === 401) {
        return "Unauthorized. Please login again.";
    }
    if (error instanceof AxiosError && error.response?.status === 403) {
        return "Forbidden. You are not authorized to access this resource.";
    }
    if (error instanceof AxiosError && error.response?.status === 404) {
        return "Not Found. The requested resource was not found.";
    }
    if (error instanceof AxiosError && error.response?.status === 429) {
        return "Too Many Requests. Please try again later.";
    }
    if (error instanceof AxiosError && error.response?.status === 500) {
        return "Internal Server Error. Please try again later.";
    }
    return error.message || defaultMessage;
}