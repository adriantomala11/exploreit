import json
import base64
import os

from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from exploreit import settings
from exploreit.helpers import send_html_email
from main_app.models import Salida, ReservaPasajero, Tour, Reserva, Incluye, NoIncluye, Itinerario


def dashboard(request):
    salidas_proximas = Salida.objects.all()
    context = {'salidas_proximas': salidas_proximas, 'settings': settings}
    return render(request, 'admin_dashboard.html', context)

def salidas_programadas(request):
    salidas_proximas = Salida.objects.all()
    context = {'salidas_proximas': salidas_proximas, 'settings': settings}
    return render(request, 'salidas_programadas.html', context)

def tours_registrados(request):
    tours = Tour.objects.all()
    context = {'tours': tours, 'settings': settings}
    return render(request, 'tours_registrados.html', context)

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

def registrar_tour(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'registrar_tour.html', context)

    elif request.method == 'POST':
        data = json.loads(request.POST['tour_data'])
        nuevo_tour = Tour(nombre=data['nombre'],
                          descripcion=data['descripcion'],
                          ubicacion=data['ubicacion'],
                          tipo=data['tipo'],
                          hora_checkin=data['hora_checkin'],
                          hora_salida=data['hora_salida'],
                          hora_retorno=data['hora_retorno'],
                          lugar_salida=data['lugar_salida'],
                          es_internacional=True if data['es_internacional']=='INT' else False,
                          capacidad=int(data['capacidad']),
                          precio=float(data['precio']),
                          duracion=int(data['duracion']),
                          token=Salida.generar_token())
        nuevo_tour.save()
        for inc in data['incluye']:
            incluye = Incluye(tour=nuevo_tour, nombre=inc['nombre'])
            incluye.save()

        for ninc in data['no_incluye']:
            no_incluye = NoIncluye(tour=nuevo_tour, nombre=ninc['nombre'])
            no_incluye.save()

        for iti in data['itinerario']:
            itinerario = Itinerario(tour=nuevo_tour, descripcion=iti['descripcion'])
            itinerario.save()

        response_url = '/administrador/tours-registrados/'
        response = JsonResponse({'status':200, 'url': response_url})
        return response

def editar_tour(request, slug):
    if request.method == 'GET':
        try:
            tour = Tour.objects.get(token=slug)

            incluye = Incluye.objects.filter(tour=tour)
            incluye = Incluye.queryset_to_list(incluye)

            no_incluye = NoIncluye.objects.filter(tour=tour)
            no_incluye = NoIncluye.queryset_to_list(no_incluye)

            itinerario = Itinerario.objects.filter(tour=tour)
            itinerario = Itinerario.queryset_to_list(itinerario)

            context = {'incluye':incluye, 'no_incluye':no_incluye, 'itinerario':itinerario, 'tour': tour}

            return render(request, 'editar_tour.html', context)
        except Exception as e:
            print(e)
            redirect('/administrador/registrar-tour/')

    elif request.method == 'POST':
        try:
            tour = Tour.objects.get(token=slug)
            data = json.loads(request.POST['tour_data'])
            tour.nombre=data['nombre']
            tour.descripcion=data['descripcion']
            tour.ubicacion=data['ubicacion']
            tour.tipo=data['tipo']
            tour.hora_checkin=data['hora_checkin']
            tour.hora_salida=data['hora_salida']
            tour.hora_retorno=data['hora_retorno']
            tour.lugar_salida=data['lugar_salida']
            tour.es_internacional=True if data['es_internacional']=='INT' else False
            tour.capacidad=int(data['capacidad'])
            tour.precio=float(data['precio'])
            tour.duracion=int(data['duracion'])


            tour.eliminar_incluyes()
            tour.eliminar_no_incluyes()
            tour.eliminar_itinerarios()

            for inc in data['incluye']:
                incluye = Incluye(tour=tour, nombre=inc['nombre'])
                incluye.save()

            for ninc in data['no_incluye']:
                no_incluye = NoIncluye(tour=tour, nombre=ninc['nombre'])
                no_incluye.save()

            for iti in data['itinerario']:
                itinerario = Itinerario(tour=tour, descripcion=iti['descripcion'])
                itinerario.save()

            imagen = data['imagen']['data']
            imgdata = base64.b64decode(imagen.split(',')[1])
            filename = data['imagen']['nombre']
            tour.imagen = filename
            ruta= os.path.join(settings.BASE_DIR,'media','tours',str(tour.id))
            if not (os.path.exists(ruta)):
                os.mkdir(ruta)
            ruta = os.path.join(ruta, filename)
            with open(ruta, 'wb+') as f:
                f.write(imgdata)
            tour.save()
            response_url = '/administrador/tours-registrados/'
            response = JsonResponse({'status':200, 'url': response_url})
            return response

        except Exception as e:
            print(e)
            response = JsonResponse({'status': 200, 'url': '/administrador/editar-tour/'+slug+'/'})
            return response

def reserva_aprobar(request):
    transaction.set_autocommit(False)
    try:
        reserva_token = request.POST['reserva_token']
        reserva = get_object_or_404(Reserva, token=reserva_token)
        pasajeros = ReservaPasajero.objects.filter(reserva=reserva)
        for pasajero in pasajeros:
            pasajero.token = pasajero.generar_token()
            pasajero.save()
        reserva.pagado = True
        reserva.save()
        recipient_list = [reserva.correo,]
        context = {'url': settings.URL,'link': settings.URL+'/ver-reserva/?tok='+reserva.token, 'reserva':reserva}
        send_html_email(recipient_list, 'Su reserva ha sido aceptada', 'email_templates/index.html', context, settings.DEFAULT_FROM_EMAIL)
        transaction.commit()
        response = JsonResponse({'status': 200, 'msg': 'Todo Bien'})
    except Exception as e:
        print('Exception: ', e)
        transaction.rollback()
        response = JsonResponse({'status': 200, 'msg': 'Error'})
    return response

def reserva_dar_de_baja(request):
    response = JsonResponse({'status': 200})
    return response