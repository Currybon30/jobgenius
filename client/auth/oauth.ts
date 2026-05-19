export function handleGoogleLogin(): void {
    globalThis.location.href = `${process.env.NEXT_PUBLIC_SPRING_API_URL}/oauth2/authorization/google`;
}