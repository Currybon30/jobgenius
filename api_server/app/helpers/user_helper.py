import requests
import logging

logger = logging.getLogger(__name__)

MONTH_WINDOW = 30 * 24 * 60 * 60  # 30 days in seconds

def get_user_city_and_country(ip_address = None):
    if ip_address is None:
        ip_address = requests.get('https://api.ipify.org').text
        
    response = requests.get(f'http://ip-api.com/json/{ip_address}').json()
    
    if response['status'] == 'success':
        return response['city'], response['country'], response['countryCode']
    
    logger.error(f"Failed to get location info for IP: {ip_address}")
    return None, None, None


if __name__ == "__main__":
    city, country, country_code = get_user_city_and_country()
    logger.info(f"User's City: {city}, Country: {country}, Country Code: {country_code}")