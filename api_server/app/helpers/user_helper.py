import logging

from fastapi import Request
import niquests
from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_user_city_and_country(ip_address: str | None = None):
    """
    Resolve location for a client IP.
    Returns (city, country_name, country_code).
    """
    try:
        if ip_address:
            response = await niquests.aget(
                f"https://ipwho.is/{ip_address}", timeout=5
            )
            response = response.json()
        else:
            # Let provider infer request origin IP when one is not supplied.
            response = await niquests.aget("https://ipwho.is/", timeout=5)
            response = response.json()
    except Exception as exc:
        logger.error(f"Failed to query geo provider: {exc}")
        return None, None, None

    if response.get("success") is True:
        return response.get("city"), response.get("country"), response.get("country_code")

    logger.error(f"Failed to get location info for IP: {ip_address}")
    return None, None, None


def get_user_ip_address(request: Request):
    if settings.DEBUG:
        client_ip = request.headers.get("client-ip-address")
        if client_ip:
            return client_ip.strip()

    # Cloudflare header: CF-Connecting-IP
    cf_connecting_ip = request.headers.get("CF-Connecting-IP")
    if cf_connecting_ip:
        return cf_connecting_ip.strip()

    # Reverse proxy / Load balancer
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Nginx / other reverse proxy
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()
    return request.client.host if request.client else None


if __name__ == "__main__":
    city, country, country_code = get_user_city_and_country()
    logger.info(
        f"User's City: {city}, Country: {country}, Country Code: {country_code}")
