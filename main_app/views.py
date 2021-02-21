import datetime
import json
from datetime import timedelta
from http import HTTPStatus

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail, EmailMessage
from django.template.loader import get_template, render_to_string
from exploreit import settings
from exploreit.helpers import send_html_email
from main_app.models import Salida, Tour, Incluye, NoIncluye, Importante, Reserva, ReservaPasajero
from django.views.decorators.csrf import csrf_exempt

def index(request):
    tours = Tour.objects.all()
    context = {'tours': tours, 'settings': settings}
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
        reserva = Reserva(salida_id=data['salida'], nombre=data['contacto']['nombres'], apellido=data['contacto']['apellidos'], correo=data['contacto']['correo'], telefono=data['contacto']['tlf'], token=Reserva.generar_token())
        reserva.save()
        pasajeros = data['pasajeros']
        for pasajero in pasajeros:
            pasajero = ReservaPasajero(reserva=reserva, nombres=pasajero['nombres'], apellidos=pasajero['apellidos'], cedula=pasajero['cedula'])
            pasajero.save()

        #ENVIO DE CORREO CON INSTRUCCIONES DE PAGO
        subject = 'Explore It: Instrucciones de Pago para Reserva '+ reserva.token
        message = """
            Para confirmar su reserva deberá:\n
            1. Ir al banco\n
            2. Realizar el deposito\n
            3. Responder a este correo con la foto del comprobante\n\n
            Att. Explore It\n
            <script>console.log("Hola Mundo")</script>
        """
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [reserva.correo, ]
        send_mail(subject, message, email_from, recipient_list)

        #RETORNO
        response_url = '/tour-booked/'+reserva.token+'/'
        response = JsonResponse({'status':200, 'url': response_url})
        return response

def tour_booked(request, token):
    context = {'settings':settings}
    reserva = get_object_or_404(Reserva, token=token)
    pasajeros = ReservaPasajero.objects.filter(reserva=reserva)
    context['reserva'] = reserva
    context['pasajeros'] = pasajeros
    context['fecha_pago'] = reserva.fecha_creacion + timedelta(days=1)
    return render(request, 'tour_booked.html', context)

def tours(request):
    params = request.GET
    fecha_inicio, fecha_fin, precio_min, precio_max, tipo, categoria, continente = (None, None, 0, 10000, None, None, None)

    # FILTRO POR NACIONAL O INTERNACIONAL
    if params.__contains__('tipo'):
        tipo = params['tipo']
        if tipo == 'INT':
            salidas = Salida.objects.filter(fecha_salida__range=[datetime.date.today(), '2030-12-31'], tour__es_internacional=True)
        elif tipo == 'NAC':
            salidas = Salida.objects.filter(fecha_salida__range=[datetime.date.today(), '2030-12-31'], tour__es_internacional=False)
        else:
            salidas = Salida.objects.filter(fecha_salida__range=[datetime.date.today(), '2030-12-31'])
    else:
        salidas = Salida.objects.filter(fecha_salida__range=[datetime.date.today(), '2030-12-31'])
    params = request.GET

    #FILTRO POR RANGO DE FECHAS
    if params.__contains__('daterange'):
        fechas = params['daterange'].split(' - ')
        fecha_inicio = fechas[0]
        fecha_inicio = fecha_inicio[6:10] + '-' + fecha_inicio[0:2] + '-' + fecha_inicio[3:5]
        fecha_fin = fechas[1]
        fecha_fin = fecha_fin[6:10] + '-' + fecha_fin[0:2] + '-' + fecha_fin[3:5]
        salidas = salidas.filter(fecha_salida__range=[fecha_inicio, fecha_fin])

    #FILTRO POR PRECIO
    if params.__contains__('precio-min'):
        if params['precio-min'] != '' and params['precio-min'] != '0':
            precio_min = int(params['precio-min'])
    if params.__contains__('precio-max'):
        if params['precio-max'] != '' and params['precio-max'] != '0':
            precio_max = int(params['precio-max'])
    if params.__contains__('precio-max') or params.__contains__('precio-min'):
        salidas = salidas.filter(tour__precio__range=[precio_min, precio_max])

    if params.__contains__('categoria'):
        categoria = params['categoria']

    if params.__contains__('continente'):
        continente = params['continente']

    context = {'salidas':salidas, 'settings':settings}
    return render(request,'tour_grid.html',context)

def ver_reserva(request):
    if request.method == 'GET':
        codigo = request.GET.get('tok')
        if codigo:
            context = {}
            reserva = get_object_or_404(Reserva, token=codigo)
            pasajeros = ReservaPasajero.objects.filter(reserva=reserva)
            context['reserva'] = reserva
            context['pasajeros'] = pasajeros
            context['fecha_pago'] = reserva.fecha_creacion + timedelta(days=1)
            return render(request, 'tour_booked.html', context)
        else:
            return render(request, 'ver_reserva.html')

def enviar_mail(request):
    # ENVIO DE CORREO CON INSTRUCCIONES DE PAGO
    subject = 'Explore It: Instrucciones de Pago para Reserva'
    context = {}
    recipient_list = ['luisadriant11@hotmail.com', ]
    send_html_email(recipient_list, 'Good news', 'email_templates/index.html', context, settings.DEFAULT_FROM_EMAIL)
    return HttpResponse()
