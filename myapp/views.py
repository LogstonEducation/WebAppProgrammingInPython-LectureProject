import datetime

from django.shortcuts import render


def home(request):
    data = {'date': datetime.date.today()}
    return render(request, 'myapp/home.html', context=data)
