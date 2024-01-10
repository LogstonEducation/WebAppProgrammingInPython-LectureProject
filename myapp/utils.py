import bs4
import requests

from .models import Currency


COUNTRY_CURRENCIES_SYMBOLS_URL = "https://thefactfile.org/countries-currencies-symbols/"


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

        obj = Currency.objects.filter(iso=currency_symbol).first()
        if obj is None:
            Currency(
                iso=currency_symbol,
                long_name=currency_name,
            ).save()
