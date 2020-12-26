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

def tour_booking(request, token):
    context = {'settings':settings}
    tour = get_object_or_404(Tour, token=token)
    salida = Salida.objects.get(pk=request.GET['sal'], tour=tour)
    context['salida'] = salida

    n_pasajeros = request.GET['pas']
    pasajeros = []
    for i in range(int(n_pasajeros)):
        pasajeros.append('')
    context['pasajeros'] = pasajeros

    detalle_orden = {}
    detalle_orden['total'] = tour.precio * int(n_pasajeros)
    detalle_orden['subtotal'] = detalle_orden['total'] / 1.12 #asumiendo que el iva es 12%
    detalle_orden['impuestos'] = detalle_orden['total'] - detalle_orden['subtotal']
    context['detalle_orden'] = detalle_orden

    return render(request, 'tour_booking.html', context)

