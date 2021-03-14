import datetime
import json
import base64
import os

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from exploreit import settings
from exploreit.helpers import send_html_email, PrintException
from main_app.models import Salida, ReservaPasajero, Tour, Reserva, Incluye, NoIncluye, Itinerario

@login_required(login_url='/login/')
def dashboard(request):
    salidas_proximas = Salida.objects.all()
    context = {'salidas_proximas': salidas_proximas, 'settings': settings}
    return render(request, 'admin_dashboard.html', context)

@login_required(login_url='/login/')
def salidas_programadas(request):
    hoy = datetime.date.today()
    salidas_proximas = Salida.objects.filter(fecha_salida__range=[hoy, '2030-12-31'])
    context = {'salidas_proximas': salidas_proximas, 'settings': settings}
    return render(request, 'salidas_programadas.html', context)

@login_required(login_url='/login/')
def tours_registrados(request):
    tours = Tour.objects.all()
    params = request.GET
    fecha_inicio, fecha_fin, precio_min, precio_max, tipo, categoria, continente = (None, None, 0, 10000, None, None, None)
    tags = {}

    try:
        #FILTRO POR TIPO (NACIONAL, INTERNACIONAL)
        if params.__contains__('tipo'):
            tipo = params['tipo']
            if tipo == 'INT':
                tours = Tour.objects.filter(es_internacional=True)
                tags['tipo'] = {'nombre': 'Tipo', 'valor': params['tipo'], 'valor_string': 'Internacional'}
            elif tipo == 'NAC':
                tours = Tour.objects.filter(es_internacional=False)
                tags['tipo'] = {'nombre': 'Tipo', 'valor': params['tipo'], 'valor_string': 'Nacional'}
            else:
                tours = Tour.objects.all()
        else:
            tours = Tour.objects.all()

        #FILTRO POR NOMBRE
        if params.__contains__('nombre'):
            tours = tours.filter(nombre__icontains=params['nombre'])
            tags['nombre'] = {'nombre': 'Nombre', 'valor': params['nombre'], 'valor_string': 'Nombre'}

        #FILTRO POR PRECIO
        if params.__contains__('precio-min'):
            if params['precio-min'] != '' and params['precio-min'] != '0':
                precio_min = int(params['precio-min'])
                tags['precio-min'] = {'nombre': 'Precio Mínimo', 'valor': params['precio-min'], 'valor_string': '$'+str(precio_min)}
        if params.__contains__('precio-max'):
            if params['precio-max'] != '' and params['precio-max'] != '0':
                precio_max = int(params['precio-max'])
                tags['precio-max'] = {'nombre': 'Precio Máximo', 'valor': params['precio-max'], 'valor_string': '$'+str(precio_max)}
        if params.__contains__('precio-max') or params.__contains__('precio-min'):
            tours = tours.filter(precio__range=[precio_min, precio_max])

        tours.order_by('pk')
        context = {'tours': tours, 'tags': tags, 'settings': settings}
        return render(request, 'tours_registrados.html', context)
    except:
        redirect('/tours/')

@login_required(login_url='/login/')
def obtener_listado_pasajeros(request, token):
    salida = get_object_or_404(Salida, token=token)
    pasajeros = ReservaPasajero.objects.filter(reserva__salida=salida, reserva__pagado=True)
    context = {'salida': salida, 'pasajeros': pasajeros}
    return render(request, 'listado_pasajeros.html', context)

@login_required(login_url='/login/')
def obtener_listado_reservas(request, token):
    salida = get_object_or_404(Salida, token=token)
    reservas = Reserva.objects.filter(salida=salida)
    context = {'salida': salida, 'reservas': reservas, 'settings':settings}
    return render(request, 'listado_reservas.html', context)

@login_required(login_url='/login/')
def programar_salida(request):
    if request.method == 'GET':
        tours = Tour.objects.all()
        context = {'tours': tours}
        return render(request, 'programar_salida.html', context)

    elif request.method == 'POST':
        data = json.loads(request.POST['salida_data'])
        tour = get_object_or_404(Tour, pk=data['tour'])
        fecha = data['fecha']
        capacidad = data['capacidad']
        nueva_salida = Salida(tour=tour, fecha_salida=fecha, token=Salida.generar_token(), capacidad=capacidad)
        nueva_salida.save()
        response_url = '/administrador/salidas-programadas/'
        response = JsonResponse({'status':200, 'url': response_url})
        return response

@login_required(login_url='/login/')
def registrar_tour(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'registrar_tour.html', context)

    elif request.method == 'POST':
        transaction.set_autocommit(False)
        try:
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
                              duracion=len(data['itinerario']),
                              precio=float(data['precio']),
                              token=Salida.generar_token())
            nuevo_tour.save()

            for inc in data['incluye']:
                incluye = Incluye(tour=nuevo_tour, nombre=inc['nombre'])
                incluye.save()

            for ninc in data['no_incluye']:
                no_incluye = NoIncluye(tour=nuevo_tour, nombre=ninc['nombre'])
                no_incluye.save()
            counter = 0
            for dia in data['itinerario']:
                counter += 1
                for iti in dia:
                    itinerario = Itinerario(tour=nuevo_tour, descripcion=iti['descripcion'], dia=counter)
                    itinerario.save()
            imagen = data['imagen']['data']
            imgdata = base64.b64decode(imagen.split(',')[1])
            filename = data['imagen']['nombre']
            nuevo_tour.imagen = filename
            ruta = os.path.join(settings.BASE_DIR, 'media', 'tours', str(nuevo_tour.id))

            if not (os.path.exists(ruta)):
                os.makedirs(ruta)
            ruta = os.path.join(ruta, filename)
            with open(ruta, 'wb+') as f:
                f.write(imgdata)
            nuevo_tour.save()
            response_url = '/administrador/tours-registrados/'
            response = JsonResponse({'status': 200, 'url': response_url})
            transaction.commit()
            return response
        except Exception as e:
            transaction.rollback()
            msg = str(e)
            response = JsonResponse({'status': 500, 'msg': msg})
            return response

@login_required(login_url='/login/')
def editar_tour(request, slug):
    if request.method == 'GET':
        try:
            tour = Tour.objects.get(token=slug)

            incluye = Incluye.objects.filter(tour=tour)
            incluye = Incluye.queryset_to_list(incluye)

            no_incluye = NoIncluye.objects.filter(tour=tour)
            no_incluye = NoIncluye.queryset_to_list(no_incluye)

            itinerario = Itinerario.objects.filter(tour=tour).order_by('dia')
            print(itinerario)
            itinerario_ls = [[]]
            for iti in itinerario:
                if iti.dia == len(itinerario_ls):
                    itinerario_ls[iti.dia-1].append({'id': iti.id, 'descripcion':iti.descripcion})
                else:
                    itinerario_ls.append([])
                    print()
                    itinerario_ls[iti.dia-1].append({'id': iti.id, 'descripcion':iti.descripcion})
            print(itinerario_ls)
            context = {'incluye':incluye, 'no_incluye':no_incluye, 'itinerario':itinerario_ls, 'tour': tour}
            return render(request, 'registrar_tour.html', context)
        except:
            PrintException()
            redirect('/administrador/registrar-tour/')

    elif request.method == 'POST':
        transaction.set_autocommit(False)
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
            tour.precio=float(data['precio'])
            tour.duracion=len(data['itinerario'])

            tour.eliminar_incluyes()
            tour.eliminar_no_incluyes()
            tour.eliminar_itinerarios()

            for inc in data['incluye']:
                incluye = Incluye(tour=tour, nombre=inc['nombre'])
                incluye.save()

            for ninc in data['no_incluye']:
                no_incluye = NoIncluye(tour=tour, nombre=ninc['nombre'])
                no_incluye.save()

            counter = 0
            for dia in data['itinerario']:
                counter += 1
                for iti in dia:
                    itinerario = Itinerario(tour=tour, descripcion=iti['descripcion'], dia=counter)
                    itinerario.save()

            try:
                imagen = data['imagen']['data']
                imgdata = base64.b64decode(imagen.split(',')[1])
                filename = data['imagen']['nombre']
                tour.imagen = filename
                ruta = os.path.join(settings.BASE_DIR, 'media', 'tours', str(tour.id))

                if not (os.path.exists(ruta)):
                    os.makedirs(ruta)
                ruta = os.path.join(ruta, filename)
                with open(ruta, 'wb+') as f:
                    f.write(imgdata)
                tour.save()
            except Exception as e:
                print(e)
            response_url = '/administrador/tours-registrados/'
            response = JsonResponse({'status':200, 'url': response_url})
            transaction.commit()
            return response

        except Exception as e:
            transaction.rollback()
            msg = str(e)
            response = JsonResponse({'status': 500, 'msg': msg})
            return response

@login_required(login_url='/login/')
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
        response = JsonResponse({'status': 200, 'msg': 'Success'})
    except Exception as e:
        print('Exception: ', e)
        transaction.rollback()
        response = JsonResponse({'status': 200, 'msg': 'Error'})
    return response

@login_required(login_url='/login/')
def copiar_tour(request):
    tour_token = request.POST['tour_token']
    new_tour = get_object_or_404(Tour, token=tour_token)
    nombre = new_tour.nombre
    incluyes = Incluye.objects.filter(tour=new_tour)
    no_incluyes = NoIncluye.objects.filter(tour=new_tour)
    itinerarios = Itinerario.objects.filter(tour=new_tour)
    new_tour.pk = None
    new_tour.token = Salida.generar_token()
    new_tour.nombre = nombre + ' COPIA'
    new_tour.save()
    for item in incluyes:
        item.pk = None
        item.tour = new_tour
        item.save()
    for item in no_incluyes:
        item.pk = None
        item.tour = new_tour
        item.save()
    for item in itinerarios:
        item.pk = None
        item.tour = new_tour
        item.save()
    response = JsonResponse({'status': 200, 'msg': 'Success'})
    return response


@login_required(login_url='/login/')
def reserva_dar_de_baja(request):
    transaction.set_autocommit(False)
    try:
        reserva_token = request.POST['reserva_token']
        reserva = get_object_or_404(Reserva, token=reserva_token)
        reserva.de_baja = True
        reserva.save()
        transaction.commit()
        response = JsonResponse({'status': 200, 'msg': 'Success'})
    except Exception as e:
        print('Exception: ', e)
        transaction.rollback()
        response = JsonResponse({'status': 200, 'msg': 'Error'})
    return response

@login_required(login_url='/login/')
def historial_salidas(request):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    salidas = Salida.objects.filter(fecha_salida__range=['2021-01-01', yesterday])
    context = {'salidas': salidas}
    return render(request, 'historial_salidas.html', context)

@login_required(login_url='/login/')
def aumentar_capacidad(request):
    salida_token = request.POST['salida']
    salida = get_object_or_404(Salida, token=salida_token)
    salida.capacidad = salida.capacidad + int(request.POST['aumento'])
    salida.save()
    response = JsonResponse({'status': 200, 'msg': 'Success'})
    return response
