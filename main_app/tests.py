import re
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse
import json 
#import unittest
# Create your tests here.
from main_app.models import Salida, Tour, Incluye, NoIncluye, Importante, Reserva, ReservaPasajero, InteresadoTour, \
    Categoria
from main_app.views import *

class MainTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin222', 'admin@correo.com', 'Exploreit2021!')
        
        Categoria.objects.create(codigo="FUL", nombre="Full Day", tipo='NAC',activa=True)
        Categoria.objects.create(codigo="ANS", nombre="Cat 2", tipo='NAC',activa=True)
        Categoria.objects.create(codigo="FSS", nombre="CAt 3", tipo='NAC',activa=True)
        Categoria.objects.create(codigo="IST", nombre="CAt 5", tipo='INT',activa=True)

        Tour.objects.create(nombre="Volcan Chimborazo",
        descripcion="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor",
        ubicacion="Chimborazo, Ecuador",hora_checkin="03:15",hora_salida="03:30",hora_retorno="21:30",
        lugar_salida="Gasolinera Mobil ubicada en la Av. Francisco",token="ti5RCHZmtRoPDgcfnvojAV7H",imagen="Screen Shot 2021-03-12 at 22.42.25.png",
        tipo="NAC",precio=45.0,duracion=1,categoria=Categoria.objects.get(codigo="FUL"),
        abordaje_dia_anterior=True)

        Salida.objects.create(token="DyeISHV8mO8D7BB4Bnqgfx1j",tour=Tour.objects.get(nombre="Volcan Chimborazo"), fecha_salida="2021-10-21", 
        capacidad=20)

        Reserva.objects.create(token="Mmgv2eKwvKd7V2LBQiv1y3zz",fecha_creacion="2021-04-04 02:05:10",
        salida=Salida.objects.get(token="DyeISHV8mO8D7BB4Bnqgfx1j"),acomodacion="asd",correo="bmsa753@gmail.com",
        nombre="NombreTest",apellido="ApellidoTest",cedula="0000000000",telefono="0000000000",
        comprobante="ASDASDAASDAADASASDADAS",metodo_de_pago="PAP",valor=95.0,estado="PEN",pagado=False,de_baja=False)

        ReservaPasajero.objects.create(token="vDjCla2TcrXFuQaQNUqEkEBN",reserva=Reserva.objects.get(token="Mmgv2eKwvKd7V2LBQiv1y3zz"),
        nombres="NombreTest",apellidos="ApellidosTest",edad=18,cedula="0000000000")

    '''
    Link: ''
    '''
    def testIndex(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        response = self.client.get('')
        self.assertEqual(len(response.context['categorias_nacionales']) , 3)
        self.assertEqual(len(response.context['categorias_internacionales']) , 1)

    '''
    /tour-info/<slug:token>/
    '''
    def testTourInfo(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        token_tour = 'ti5RCHZmtRoPDgcfnvojAV7H'
        response = self.client.get('/tour-info/'+token_tour+'/')
        tour = get_object_or_404(Tour, token=token_tour)
        self.assertEqual(len(response.context['tour_info']) , len(tour.obtener_info()))
        self.assertEqual(len(response.context['similares']) , len(tour.obtener_similares()))
    '''
    /tour-booking/<slug:token>/
    '''
    def testTourBookingGet(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        token_tour = 'ti5RCHZmtRoPDgcfnvojAV7H'
        token_salida = 'DyeISHV8mO8D7BB4Bnqgfx1j'
        tour = get_object_or_404(Tour, token=token_tour)
        salida = Salida.objects.get(token=token_salida)
        response = self.client.get('/tour-booking/'+token_tour+'/',{'sal':salida.id,'pas':5})

        detalle_orden = {}
        detalle_orden['total'] = round(tour.precio * int(5), 2)
        detalle_orden['subtotal'] = round(detalle_orden['total'] / 1.12, 2) #asumiendo que el iva es 12%
        detalle_orden['impuestos'] = round(detalle_orden['total'] - detalle_orden['subtotal'], 2)

        tour = get_object_or_404(Tour, token=token_tour)
        self.assertTrue(response.context['hay_suficientes_cupos'])
        self.assertEqual(response.context['detalle_orden'] , detalle_orden)

    def testTourBookingPost(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        token_tour = 'ti5RCHZmtRoPDgcfnvojAV7H'
        token_salida = 'DyeISHV8mO8D7BB4Bnqgfx1j'
        reserva_token='Mmgv2eKwvKd7V2LBQiv1y3zz'
        salida = Salida.objects.get(token="DyeISHV8mO8D7BB4Bnqgfx1j")
        reserva = {}
        reserva['salida']=salida.id
        pasajero=[{'nombres':'Bryan','apellidos':'Sanchez','cedula':'0000000000'},{'nombres':'Nomvre2','apellidos':'Apellido2','cedula':'0000000000'}]
        reserva['pasajeros']=pasajero
        contacto={}
        contacto['nombres']='NombreTest'
        contacto['apellidos']='ApellidoTest'
        contacto['correo']='bmsa753@gmail.com'
        contacto['tlf']='0000000000'
        reserva['contacto']=contacto

        reserva['metodo_pago']='PAP'
        reserva['valor']='95,0'

        json_object = json.dumps(reserva, indent = 16) 
        response = self.client.post('/tour-booking/'+token_tour+'/',{'booking_data':json_object})
        self.assertEqual(response.status_code,200)
    '''
    /tour-booked/<slug:token>/
    '''
    def testTourBooked(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        token_tour = 'ti5RCHZmtRoPDgcfnvojAV7H'
        token_salida = 'DyeISHV8mO8D7BB4Bnqgfx1j'
        reserva_token='Mmgv2eKwvKd7V2LBQiv1y3zz'

        reserva = get_object_or_404(Reserva, token=reserva_token)
        pasajeros = ReservaPasajero.objects.filter(reserva=reserva)
        response = self.client.post('/tour-booked/'+reserva_token+'/')
        self.assertEqual(response.context['reserva'],reserva)
        self.assertEqual(len(response.context['pasajeros']),len(pasajeros))
'''
nombre + ' COPIA'
response = self.client.get('/administrador/categorias/', {'categoria': 'FUL','tipo':'NAC'})
def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')

         Itinerario.objects.create(tour=Tour.objects.get(nombre="Volcan Chimborazo"), dia=1, descripcion="NAC")
        Incluye.objects.create(nombre="Guía Nacional",tour=Tour.objects.get(nombre="Volcan Chimborazo"))
        NoIncluye.objects.create(nombre="Guía Nacional",tour=Tour.objects.get(nombre="Volcan Chimborazo"))

'''
    
    
   