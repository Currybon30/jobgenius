export function AdjustUserFullName(
    firstName: string,
    lastName: string,
    country: string
): string {
    if (country === "Vietnam") {
        return `${lastName} ${firstName}`;
    } else {
        return `${firstName} ${lastName}`;
    }
}