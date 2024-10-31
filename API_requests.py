import requests

from errors import BadRequest, APIKeyError
from initialize import BASEURL, API_KEY, SEARCH_BY_GEOLOCATION, FORECAST_5_DAYS_BY_GEOLOCATION


def result_to_geokey(response) -> str:
    data = response.json()
    geokey = data['Key']

    return geokey

def geokey_request(lat: str, lon: str) -> str:  # Запрос к API для получения геокода для дальнейших запросов
    location = f'{lat},{lon}'
    query = {'apikey': API_KEY, 'q' :location}

    get_location_key_request = requests.get(url=BASEURL+SEARCH_BY_GEOLOCATION,
                                    params=query)

    if get_location_key_request.status_code == 400 or get_location_key_request.json() is None:
        raise BadRequest

    if get_location_key_request.status_code == 401 or get_location_key_request.status_code == 503:
        raise APIKeyError


    geokey = result_to_geokey(get_location_key_request)
    return geokey


def result_to_conditions(response) -> dict:  # Парсит необходимые данные прогноза от API
    data = response.json()
    conditions = {}
    for i in range(5):
        date = data['DailyForecasts'][i]['Date']
        min_temperature = data['DailyForecasts'][i]['Temperature']['Minimum']['Value']
        max_temperature = data['DailyForecasts'][i]['Temperature']['Maximum']['Value']
        humidity = data['DailyForecasts'][i]['Day']['RelativeHumidity']['Average'] #  Влажность в процентах
        wind_speed = data['DailyForecasts'][i]['Day']['Wind']['Speed']['Value'] # Скорость ветра в км/ч
        precipitation_probability = data['DailyForecasts'][i]['Day']['PrecipitationProbability'] #  вероятность осадков в %
        conditions[i] =  {
            'Date': date,
            'Minimal Temperature': min_temperature,
            'Maximal Temperature': max_temperature,
            "Humidity": humidity,
            'Wind Speed': wind_speed,
            'Precipitation Probability': precipitation_probability
                  }
    return conditions


def weather_by_key_request(geokey: str) -> dict:
    query = {'apikey': API_KEY,
             'language': 'ru-ru',
             'details': True,
             'metric': True}
    get_weather_by_key = requests.get(url=BASEURL+FORECAST_5_DAYS_BY_GEOLOCATION+geokey,
                                      params=query)

    if get_weather_by_key.status_code == 400:
        raise BadRequest
    if get_weather_by_key.status_code == 401:
        raise APIKeyError

    conditions = result_to_conditions(get_weather_by_key)

    return conditions


def get_weather_conditions(lat: str, lon: str) -> dict:
    try:
        geokey = geokey_request(lat, lon)
        conditions = weather_by_key_request(geokey)
        return conditions

    except BadRequest:
        raise BadRequest("По этим координатам нельзя получить погоду..")
    except APIKeyError:
        raise APIKeyError("Проблема с API-ключом!")



if __name__ == "__main__":
    lat = '55.764108'
    lon = '37.592446'
    print(get_weather_conditions(lat, lon))
