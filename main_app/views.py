import json
from http import HTTPStatus

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from exploreit import settings
from main_app.models import Salida, Tour, Incluye, NoIncluye, Importante, Reserva, ReservaPasajero


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
    if request.method == 'GET':
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

    elif request.method == 'POST':
        data = json.loads(request.POST['booking_data'])
        reserva = Reserva(salida_id=data['salida'], correo=data['facturacion']['correo'], token=Reserva.generar_token())
        reserva.save()
        pasajeros = data['pasajeros']
        for pasajero in pasajeros:
            pasajero = ReservaPasajero(reserva=reserva, nombres=pasajero['nombres'], apellidos=pasajero['apellidos'], cedula=pasajero['cedula'])
            pasajero.save()
        response_url = '/tour-booked/'+reserva.token+'/'
        response = JsonResponse({'status':200, 'url': response_url})
        return response

def tour_booked(request, token):
    context = {'settings':settings}
    reserva = get_object_or_404(Reserva, token=token)
    return render(request, 'tour_booked.html', context)