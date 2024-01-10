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
