import requests
import logging

logger = logging.getLogger(__name__)

def get_user_city_and_country(ip_address=None):
    """
    Resolve location for a client IP.
    Returns (city, country_name, country_code).
    """
    try:
        if ip_address:
            response = requests.get(
                f"https://ipwho.is/{ip_address}", timeout=5
            ).json()
        else:
            # Let provider infer request origin IP when one is not supplied.
            response = requests.get("https://ipwho.is/", timeout=5).json()
    except Exception as exc:
        logger.error(f"Failed to query geo provider: {exc}")
        return None, None, None

    if response.get("success") is True:
        return response.get("city"), response.get("country"), response.get("country_code")

    logger.error(f"Failed to get location info for IP: {ip_address}")
    return None, None, None


if __name__ == "__main__":
    city, country, country_code = get_user_city_and_country()
    logger.info(f"User's City: {city}, Country: {country}, Country Code: {country_code}")