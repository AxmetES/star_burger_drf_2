from datetime import timedelta

import requests
from django.utils import timezone

from foodcartapp.models import GeoPosition
from star_burger.settings import YANDEX_API_KEY


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lon), float(lat)


def save_geo_position(address):
    lon, lat = fetch_coordinates(YANDEX_API_KEY, address)
    geo_position = GeoPosition(lon=lon,
                               lat=lat,
                               address=address)
    geo_position.save()
    return lon, lat


def get_or_create_lon_lat(address):
    geo_position = GeoPosition.objects.filter(address=address).first()
    if not geo_position:
        return save_geo_position(address)
    else:
        if (timezone.now() - geo_position.updated_at) > timedelta(hours=24):
            return save_geo_position(address)
        else:
            return geo_position.lon, geo_position.lat
