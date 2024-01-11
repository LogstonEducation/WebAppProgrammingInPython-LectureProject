import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import models, utils


def home(request):
    data = {'date': datetime.date.today()}
    return render(request, 'myapp/home.html', context=data)


def maintenance(request):
    if request.method == 'POST':
        if request.POST['op'] == 'currencies':
            utils.add_currencies(utils.fetch_currencies())
            return HttpResponseRedirect(reverse('currencies'))

    return render(request, 'myapp/maintenance.html')


def view_currencies(request):
    data = {'currencies': models.Currency.objects.all()}
    return render(request,'myapp/currencies.html', context=data)


def currency_selection(request):
    data = {'currencies': models.Currency.objects.all()}
    return render(request,'myapp/currency_selector.html', context=data)


def exch_rate(request):
    if not ('currency_from' in request.GET and 'currency_to' in request.GET):
        return HttpResponseRedirect(reverse('currency_selector'))

    data = {
        'currency1': models.Currency.objects.filter(iso=request.GET['currency_from']).first(),
        'currency2': models.Currency.objects.filter(iso=request.GET['currency_to']).first(),
    }

    utils.update_xrates(data['currency1'])

    rate_obj = data['currency1'].currency_one_rate_set.filter(currency_two=data['currency2']).first()
    data['rate'] = rate_obj.rate if rate_obj else 'Not Available'

    return render(request, "myapp/exchange_detail.html", data)
