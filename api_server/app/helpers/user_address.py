import requests

def get_user_city_and_country(ip_address = None):
    if ip_address is None:
        ip_address = requests.get('https://api.ipify.org').text
        
    response = requests.get(f'https://ip-api.com/json/{ip_address}').json()
    
    if response['status'] == 'success':
        return response['city'], response['country']
    
    return None, None