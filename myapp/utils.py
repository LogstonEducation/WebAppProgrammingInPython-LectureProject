from datetime import datetime, timezone

import bs4
import folium
import requests

from . import models


COUNTRY_CURRENCIES_SYMBOLS_URL = "https://thefactfile.org/countries-currencies-symbols/"
CURRENCY_TABLE_URL_STUB = "https://www.xe.com/currencytables/?from="


def fetch_currencies() -> list:
    response = requests.get(COUNTRY_CURRENCIES_SYMBOLS_URL)
    if not response.status_code == 200:
        return []

    soup = bs4.BeautifulSoup(response.content, 'html.parser')

    currencies = set()
    for line in soup.find_all('tr'):
        try:
            td = line.find_all('td')

            currency = td[2].get_text().strip()
            iso = td[3].get_text().strip()
        except (AttributeError, IndexError):
            continue

        currencies.add((currency, iso))

    return sorted(currencies)


def add_currencies(currencies):
    for currency in currencies:
        currency_name, currency_symbol = currency

        obj = models.Currency.objects.filter(iso=currency_symbol).first()
        if obj is None:
            models.Currency(
                iso=currency_symbol,
                long_name=currency_name,
            ).save()


def get_currency_rates(iso_code):
    url = CURRENCY_TABLE_URL_STUB + iso_code

    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')

    x_rate_list = []
    for line in soup.find('tbody').find_all('tr'):
        symbol = line.find('th').get_text()
        td = line.find_all('td')
        try:
            x_rate = float(td[2].get_text().strip())
        except (TypeError, ValueError):
            continue

        x_rate_list.append((symbol, x_rate))

    return x_rate_list


def update_xrates(currency):
    for symbol, x_rate in get_currency_rates(currency.iso):

        try:
            currency_two = models.Currency.objects.get(iso=symbol)
        except models.Currency.DoesNotExist:
            continue

        try:
            rate_object = models.Rates.objects.get(
                currency_one=currency,
                currency_two=currency_two,
            )

            rate_object.rate = x_rate
            rate_object.last_update_time = datetime.now(timezone.utc)

        except models.Rates.DoesNotExist:
            rate_object = models.Rates(
                currency_one=currency,
                currency_two=currency_two,
                rate=x_rate,
                last_update_time=datetime.now(timezone.utc),
            )

        rate_object.save()


def dms_to_decimal(dms_coordinates):
    degrees = int(dms_coordinates.split('°')[0])
    minutes = int(dms_coordinates.split('°')[1].split("′")[0])

    try:
        seconds = int(dms_coordinates.split('°')[1].split("′")[1][:2])
    except (TypeError, ValueError):
        seconds = 0.0

    decimal = degrees + minutes / 60 + seconds / 3600

    if dms_coordinates:
        if dms_coordinates[-1] == "S":
            decimal = -decimal

        elif dms_coordinates[-1] == "W":
            decimal = -decimal

    return decimal


def get_lat_lon(city_name):
    city = models.City.objects.filter(name=city_name).first()

    url = ''
    if city:
        lat = city.latitude
        lon = city.longitude
    else:
        url = f"https://en.wikipedia.org/wiki/{city_name.replace(' ', '_')}"
        soup = bs4.BeautifulSoup(requests.get(url).content, 'html.parser')
        try:
            lat = soup.find('span', class_="latitude").get_text()
            lon = soup.find('span', class_="longitude").get_text()
        except AttributeError:
            lat = lon = '0°0′0″N 0°0′0″W'

        lat = dms_to_decimal(lat)
        lon = dms_to_decimal(lon)

    return round(lat, 5), round(lon, 5), url


def get_lat_lon_dicts(visiting_cities):
    details_by_lat_lon = dict()
    for city_name in visiting_cities:
        lat, lon, wiki_link = get_lat_lon(city_name.strip())
        if lat and lon and wiki_link:
            details_by_lat_lon[(lat,  lon)] = (wiki_link, city_name)
    return details_by_lat_lon


def add_markers(m, visiting_cities):
    details_by_lat_lon = get_lat_lon_dicts(visiting_cities)
    for (lat, lon), (wiki_link, city_name) in details_by_lat_lon.items():
        icon = folium.Icon(color="blue", prefix="fa", icon="plane")
        popup = f"<a href={wiki_link}>{city_name}</a>"
        marker = folium.Marker((lat, lon), icon=icon, popup=popup)
        marker.add_to(m)

    # Add line. First rearrange lat longs by longitude
    lat_lon_list = sorted(details_by_lat_lon.keys(), key=lambda x: x[1])
    line_string = [[lat_lon_list[i], lat_lon_list[i+1]] for i in range(len(lat_lon_list)-1)]

    line = folium.PolyLine(line_string, color="red", weight=5)
    line.add_to(m)
    return m
