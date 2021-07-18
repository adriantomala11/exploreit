import base64
import datetime
import json
import os
import sys

import requests
from datetime import timedelta
from http import HTTPStatus

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail, EmailMessage
from django.template.loader import get_template, render_to_string
from rest_framework.decorators import api_view

from exploreit import settings
from exploreit.helpers import send_html_email, Payphone, print_exception
from main_app.models import Salida, Tour, Incluye, NoIncluye, Importante, Reserva, ReservaPasajero, InteresadoTour, \
    Categoria
from django.views.decorators.csrf import csrf_exempt

def index(request):
    tours = Tour.objects.all()
    categorias_nacionales = Categoria.objects.filter(tipo='NAC', activa=True)
    categorias_internacionales = Categoria.objects.filter(tipo='INT', activa=True)
    context = {'tours': tours, 'settings': settings, 'categorias_nacionales':categorias_nacionales, 'categorias_internacionales':categorias_internacionales}
    return render(request, 'index.html', context)

def tour_info(request, token):
    context = {'settings':settings}
    tour = get_object_or_404(Tour, token=token)
    tour_info = tour.obtener_info()
    similares = tour.obtener_similares()
    context['tour_info'] = tour_info
    context['similares'] = similares
    return render(request, 'tour_info.html', context)

def tour_booking(request, token):
    if request.method == 'GET':
        context = {'settings':settings}
        tour = get_object_or_404(Tour, token=token)
        salida = Salida.objects.get(pk=request.GET['sal'], tour=tour)
        context['salida'] = salida
        context['hay_suficientes_cupos'] = salida.obtener_disponibilidad(request.GET['pas'])
        n_pasajeros = request.GET['pas']
        pasajeros = []
        for i in range(int(n_pasajeros)):
            pasajeros.append('')
        context['pasajeros'] = pasajeros

        detalle_orden = {}
        detalle_orden['total'] = round(tour.precio * int(n_pasajeros), 2)
        detalle_orden['subtotal'] = round(detalle_orden['total'] / 1.12, 2) #asumiendo que el iva es 12%
        detalle_orden['impuestos'] = round(detalle_orden['total'] - detalle_orden['subtotal'], 2)

        detalle_payphone = {}
        detalle_payphone['total'] = int(detalle_orden['total'] * 100)
        detalle_payphone['subtotal'] = int(detalle_orden['subtotal'] * 100)
        detalle_payphone['impuestos'] = int(detalle_orden['impuestos'] * 100)
        detalle_payphone['service'] = int(detalle_payphone['total'] - detalle_payphone['subtotal'] - detalle_payphone['impuestos'])

        context['detalle_orden'] = detalle_orden
        context['detalle_payphone'] = detalle_payphone

        return render(request, 'tour_booking.html', context)

    elif request.method == 'POST':
        data = json.loads(request.POST['booking_data'])
        valor = int(data['valor'].replace(',', ''))
        reserva = Reserva(salida_id=data['salida'], nombre=data['contacto']['nombres'], apellido=data['contacto']['apellidos'], correo=data['contacto']['correo'], telefono=data['contacto']['tlf'], token=Reserva.generar_token(), metodo_de_pago=data['metodo_pago'], valor=valor)
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
        """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [reserva.correo,]
        send_mail(subject, message, from_email, recipient_list)

        #RETORNO
        response_url = '/ver-reserva/?tok='+str(reserva.token)
        response = JsonResponse({'status':200, 'url': response_url, 'reserva_token':reserva.token, 'payphone_token': Payphone.TOKEN, 'payphone_prepare_url': Payphone.PREPARE_URL})
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
    tags = {}
    categorias = []
    try:
        # FILTRO POR NACIONAL O INTERNACIONAL
        if params.__contains__('tipo'):
            tipo = params['tipo']
            if tipo=='NAC':
                categorias = Categoria.objects.filter(tipo='NAC')
            elif tipo=='INT':
                categorias = Categoria.objects.filter(tipo='INT')
            salidas = Salida.objects.filter(tour__tipo=tipo, tour__activo=True)
            tags['tipo'] = {'nombre': 'Tipo', 'valor': tipo, 'valor_string': dict(Tour.TIPO_CHOICES).get(tipo)}
        else:
            categorias = Categoria.objects.all()
            salidas = Salida.objects.filter(tour__activo=True)

        #FILTRO POR RANGO DE FECHAS
        if params.__contains__('daterange'):
            fechas = params['daterange'].split(' - ')
            fecha_inicio = fechas[0]
            fecha_inicio = fecha_inicio[6:10] + '-' + fecha_inicio[0:2] + '-' + fecha_inicio[3:5]
            fecha_fin = fechas[1]
            fecha_fin = fecha_fin[6:10] + '-' + fecha_fin[0:2] + '-' + fecha_fin[3:5]
            salidas = salidas.filter(fecha_salida__range=[fecha_inicio, fecha_fin])
            tags['daterange'] = {'nombre': 'Fecha Salida', 'valor': params['daterange'], 'valor_string': params['daterange']}

        #FILTRO POR PRECIO
        elif params.__contains__('precio-min'):
            if params['precio-min'] != '' and params['precio-min'] != '0':
                precio_min = int(params['precio-min'])
                tags['precio-min'] = {'nombre': 'Precio Mínimo', 'valor': params['precio-min'], 'valor_string': '$'+str(precio_min)}

        elif params.__contains__('precio-max') and params['precio-max'] != '' and params['precio-max'] != '0':
            precio_max = int(params['precio-max'])
            tags['precio-max'] = {'nombre': 'Precio Máximo', 'valor': params['precio-max'], 'valor_string': '$'+str(precio_max)}

        if params.__contains__('precio-max') or params.__contains__('precio-min'):
            salidas = salidas.filter(tour__precio__range=[precio_min, precio_max])

        if params.__contains__('categoria'):
            categoria = params['categoria']
            if categoria == 'ALL':
                pass
            else:
                categoria = Categoria.objects.get(codigo=categoria)
                salidas = salidas.filter(tour__categoria=categoria)
                tags['categoria'] = {'nombre': 'Categoria', 'valor': categoria.codigo, 'valor_string': categoria.nombre}

        if params.__contains__('continente'):
            continente = params['continente']

        tours = {}
        for salida in salidas:
            if not tours.__contains__(str(salida.tour.id)):
                tours[str(salida.tour.id)] = salida.tour

        context = {'settings':settings, 'tags': tags, 'tours': tours, 'categorias': categorias}
        return render(request, 'tour_grid.html', context)
        #if params.__contains__('mobile'):
        #    tipo = params['mobile']
        #    if tipo == settings.MOBILE_KEY:
        #        tours = Tour.to_response_dict(tours.values())
        #        return JsonResponse(data={'tags': tags, 'tours': tours})
        #else:
        #    return render(request,'tour_grid.html',context)
    except Exception as e:
        print(e)
        return redirect('/tours/')

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
            context['settings'] = settings
            return render(request, 'tour_booked.html', context)
        else:
            return render(request, 'ver_reserva.html')

def enviar_mail(request):
    # ENVIO DE CORREO CON INSTRUCCIONES DE PAGO
    subject = 'Explore It: Instrucciones de Pago para Reserva'
    context = {subject}
    recipient_list = ['luisadriant11@hotmail.com', ]
    send_html_email(recipient_list, 'Good news', 'email_templates/index.html', context, settings.DEFAULT_FROM_EMAIL)
    return HttpResponse()

def subir_comprobante(request):
    reserva_token = request.POST['reserva']
    reserva = Reserva.objects.get(token=reserva_token)
    imagen = request.POST['imagen']
    filename = request.POST['filename']
    return_value = reserva.upload_to_aws(imagen, filename)
    return JsonResponse({'data':return_value})

def mostrar_interes(request):
    tour_token = request.POST['tour']
    correo_interesado = request.POST['correo']
    new_interesado = InteresadoTour(cliente=correo_interesado, tour=get_object_or_404(Tour, token=tour_token))
    new_interesado.save()
    response = JsonResponse({'status': 200, 'msg': 'Success'})
    return response

@api_view()
def recibir_pagos(request):
    url = 'https://pay.payphonetodoesposible.com/api'
    try:
        id = str(request.GET.get('id'))
        client_tx_id = str(request.GET.get('clientTransactionId'))
        data = {
            "id": id,
            "clientTxId": client_tx_id,
        }
        url = url+'/button/V2/Confirm/'
        auth_token = 'Bearer '+Payphone.TOKEN
        r = requests.post(url, data=data, headers={'Authorization': auth_token})
        response = json.loads(r.text)
        reserva = Reserva.objects.get(token=str(request.GET.get('clientTransactionId')))
        if(response['transactionStatus']=='Approved' and response['amount']==reserva.valor):
            reserva.aprobar()
        response = HttpResponse()
    except Exception as e:
        print_exception()
        response = HttpResponse()
    return response

#from django.http import StreamingHttpResponse
#def validate_certificate(request):
#    content = open('/Users/adriantomala/Desktop/Proyecto Exploreit/exploreit/main_app/6E1AA5227777D3E36CCEF7FB5B85D88A.txt', 'r').read()
#    response = StreamingHttpResponse(content)
#    response['Content-Type'] = 'text/plain; charset=utf8'
#    return response