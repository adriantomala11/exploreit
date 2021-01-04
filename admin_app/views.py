import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

from exploreit import settings
from main_app.models import Salida, ReservaPasajero, Tour, Reserva


def dashboard(request):
    salidas_proximas = Salida.objects.all()
    context = {'salidas_proximas': salidas_proximas, 'settings': settings}
    return render(request, 'admin_dashboard.html', context)

def salidas_programadas(request):
    salidas_proximas = Salida.objects.all()
    context = {'salidas_proximas': salidas_proximas, 'settings': settings}
    return render(request, 'salidas_programadas.html', context)

def obtener_listado_pasajeros(request, token):
    salida = get_object_or_404(Salida, token=token)
    pasajeros = ReservaPasajero.objects.filter(reserva__salida=salida)
    context = {'salida': salida, 'pasajeros': pasajeros}
    return render(request, 'listado_pasajeros.html', context)

def obtener_listado_reservas(request, token):
    salida = get_object_or_404(Salida, token=token)
    reservas = Reserva.objects.filter(salida=salida)
    context = {'salida': salida, 'reservas': reservas}
    return render(request, 'listado_reservas.html', context)

def programar_salida(request):
    if request.method == 'GET':
        tours = Tour.objects.all()
        context = {'tours': tours}
        return render(request, 'programar_salida.html', context)

    elif request.method == 'POST':
        data = json.loads(request.POST['salida_data'])
        tour = get_object_or_404(Tour, pk=data['tour'])
        fecha = data['fecha']
        nueva_salida = Salida(tour=tour, fecha_salida=fecha, token=Salida.generar_token())
        nueva_salida.save()
        response_url = '/administrador/salidas-programadas/'
        response = JsonResponse({'status':200, 'url': response_url})
        return response