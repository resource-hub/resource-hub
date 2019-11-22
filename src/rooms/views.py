from django.shortcuts import render
from django.views import View


def index(request):
    return render(request, 'rooms/index.html')


class Manage(View):
    def get(request):
        return


class Create(View):
    def get(request):
        return
