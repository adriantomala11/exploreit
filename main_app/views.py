from django.shortcuts import render, get_object_or_404

from exploreit import settings
from main_app.models import Salida, Tour, Incluye, NoIncluye, Importante


def index(request):
    salidas_proximas = Salida.objects.all()
    context = {'salidas_proximas': salidas_proximas, 'settings': settings}
    return render(request, 'index.html', context)

def tour_info(request, token):
    context = {'settings':settings}
    tour = get_object_or_404(Tour, token=token)
    tour_info = tour.obtener_info()
    context['tour_info'] = tour_info
    return render(request, 'tour_info.html', context)

