import datetime

from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import folium

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

    if request.user.is_authenticated:
        account_holder = models.AccountHolder.objects.get(user=request.user)
        account_holder.currencies_visited.add(data['currency1'])
        account_holder.currencies_visited.add(data['currency2'])
        data['currencies_visited'] = account_holder.currencies_visited.all()

    return render(request, "myapp/exchange_detail.html", data)


def register_new_user(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        new_user = form.save()
        models.AccountHolder(
            user=new_user,
            date_of_birth=request.POST["dob"],
        ).save()
        return HttpResponseRedirect(reverse('home'))

    return render(request, "registration/register.html", {'form': form})


def map(request):
    number_of_cities = int(request.GET["number_of_cities"]) if 'number_of_cities' in request.GET else 0

    form_names = ["city" + str(i) for i in range(number_of_cities)]
    visiting_cities = list(filter(lambda n: n != '', (request.GET.get(name) or '' for name in form_names)))

    m = folium.Map()
    data = {
        'm': m._repr_html_,
        'number_of_cities': number_of_cities,
        'names': form_names,
        'visiting_cities': visiting_cities,
    }
    return render(request, 'myapp/map.html', context=data)
