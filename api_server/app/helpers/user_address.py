import requests

def get_user_city_and_country(ip_address = None):
    if ip_address is None:
        ip_address = requests.get('https://api.ipify.org').text
        
    response = requests.get(f'http://ip-api.com/json/{ip_address}').json()
    
    if response['status'] == 'success':
        return response['city'], response['country'], response['countryCode']
    
    return None, None, None


if __name__ == "__main__":
    city, country, country_code = get_user_city_and_country()
    print(f"User's City: {city}, Country: {country}, Country Code: {country_code}")