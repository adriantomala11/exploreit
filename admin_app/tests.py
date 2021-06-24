from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.urls import reverse
import json 
#import unittest
# Create your tests here.
from main_app.models import Salida, ReservaPasajero, Tour, Reserva, Incluye, NoIncluye, Itinerario, Categoria
from main_app.views import *

class CategoriaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin222', 'admin@correo.com', 'Exploreit2021!')
        
        Categoria.objects.create(codigo="FUL", nombre="Full Day", tipo="NAC",activa=True)
        Categoria.objects.create(codigo="ANS", nombre="Cat 2", tipo="NAC",activa=True)
        Categoria.objects.create(codigo="FSS", nombre="CAt 3", tipo="NAC",activa=True)

        Tour.objects.create(nombre="Volcan Chimborazo",
        descripcion="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor",
        ubicacion="Chimborazo, Ecuador",hora_checkin="03:15",hora_salida="03:30",hora_retorno="21:30",
        lugar_salida="Gasolinera Mobil ubicada en la Av. Francisco",token="ti5RCHZmtRoPDgcfnvojAV7H",imagen="Screen Shot 2021-03-12 at 22.42.25.png",
        tipo="NAC",precio=45.0,duracion=1,categoria=Categoria.objects.get(codigo="FUL"),
        abordaje_dia_anterior=True)

        Itinerario.objects.create(tour=Tour.objects.get(nombre="Volcan Chimborazo"), dia=1, descripcion="NAC")
        Incluye.objects.create(nombre="Guía Nacional",tour=Tour.objects.get(nombre="Volcan Chimborazo"))
        NoIncluye.objects.create(nombre="Guía Nacional",tour=Tour.objects.get(nombre="Volcan Chimborazo"))

        Salida.objects.create(token="DyeISHV8mO8D7BB4Bnqgfx1j",tour=Tour.objects.get(nombre="Volcan Chimborazo"), fecha_salida="2021-10-21", 
        capacidad=20)

        Reserva.objects.create(token="Mmgv2eKwvKd7V2LBQiv1y3zz",fecha_creacion="2021-04-04 02:05:10",
        salida=Salida.objects.get(token="DyeISHV8mO8D7BB4Bnqgfx1j"),acomodacion="asd",correo="asd@gmail.com",
        nombre="NombreTest",apellido="ApellidoTest",cedula="0000000000",telefono="0000000000",
        comprobante="ASDASDAASDAADASASDADAS",metodo_de_pago="PAP",valor=95.0,estado="PEN",pagado=False,de_baja=False)

        ReservaPasajero.objects.create(token="vDjCla2TcrXFuQaQNUqEkEBN",reserva=Reserva.objects.get(token="Mmgv2eKwvKd7V2LBQiv1y3zz"),
        nombres="NombreTest",apellidos="ApellidosTest",edad=18,cedula="0000000000")

    def testLogin(self):
        login = self.client.login(username='admin222', password='Exploreit2021!')
        self.assertTrue(login) 

    '''
    /administrador/categorias/
    '''
    def testGetCategorias(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        response = self.client.get('/administrador/categorias/')
        self.assertEqual(len(response.context['categorias']) , 3)

    def testPostCategoria(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        response = self.client.post('/administrador/categorias/', {'categoria': 'categoria','tipo':'NAC'})
        self.assertEqual(response.status_code,200)
    
    '''
    administrador/aumentar-capacidad/
    '''
    def testAumentarCapacidad(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        salida_token = "DyeISHV8mO8D7BB4Bnqgfx1j"
        response = self.client.post('/administrador/aumentar-capacidad/', {'salida': salida_token,'aumento':3})
        salida = get_object_or_404(Salida, token=salida_token)
        self.assertEqual(salida.capacidad,23)
    '''
    /administrador/reserva-dar-de-baja/
    En un ambiente de testeo, las views deben usar los metodos save() de los modelos, no los atommicos
    '''
    def testDarDeBaja(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        reserva_token = "Mmgv2eKwvKd7V2LBQiv1y3zz"
        response = self.client.post('/administrador/reserva-dar-de-baja/', {'reserva_token': reserva_token})
        reserva = get_object_or_404(Reserva, token=reserva_token)
        self.assertEqual(reserva.de_baja,True)
    
    '''
    /administrador/copiar-tour/
    '''
    def testCopiarTour(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        tour_token = "ti5RCHZmtRoPDgcfnvojAV7H"
        response = self.client.post('/administrador/copiar-tour/', {'tour_token': tour_token})
        nombreTour ="Volcan Chimborazo"
        tourOriginal = get_object_or_404(Tour, nombre=nombreTour)
        tourCopia = get_object_or_404(Tour, nombre="Volcan Chimborazo COPIA")
        self.assertEqual(tourOriginal.nombre+ ' COPIA',tourCopia.nombre)

    '''
    /administrador/reserva-aprobar/
    En un ambiente de testeo, las views deben usar los metodos save() de los modelos, no los atommicos
    '''
    def testReservaAprobar(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        reserva_token = "Mmgv2eKwvKd7V2LBQiv1y3zz"
        response = self.client.post('/administrador/reserva-aprobar/', {'reserva_token': reserva_token})
        reserva = get_object_or_404(Reserva, token=reserva_token)
        self.assertEqual(reserva.estado,"APR")
    
    '''
    /administrador/editar-tour/<slug:slug>/
    '''
    def testEditarTourGet(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        tour_token = "ti5RCHZmtRoPDgcfnvojAV7H"
        response = self.client.get('/administrador/editar-tour/'+tour_token+'/')
        tour = Tour.objects.get(token=tour_token)
        print(response)
        self.assertEqual(response.context['tour'],tour)
    
    def testEditarTourPost(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        tour_token = "ti5RCHZmtRoPDgcfnvojAV7H"
        tour = Tour.objects.get(token=tour_token)
        tour.nombre = "Nombre Cambiado del Tour"
        print(tour.nombre)
        response = self.client.post('/administrador/editar-tour/'+tour_token+'/',{'tour_data':tour})
        self.assertEqual("Nombre Cambiado del Tour",tour.nombre)
    '''
    /administrador/registrar-tour/
    '''
    def testRegistrarTour(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        tour_token = "ti5RCHZmtRoPDgcfnvojAV7H"
        tour = Tour.objects.get(token=tour_token)
        response = self.client.post('/administrador/registrar-tour/',{'tour_data':tour})
        tour2 = Tour.objects.get(nombre=tour.nombre)
        self.assertEqual(tour,tour2)
    '''
    /administrador/programar-salida/
    '''
    def testProgramarSalida(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        tour_token = "ti5RCHZmtRoPDgcfnvojAV7H"
        tour = Tour.objects.get(token=tour_token)
        salida_data = {}
        salida_data['tour']=tour.id
        salida_data['fecha']='2021-10-21'
        salida_data['capacidad']='20'
        json_object = json.dumps(salida_data, indent = 4) 
        response = self.client.post('/administrador/programar-salida/',{'salida_data':json_object})
        self.assertEqual(response.status_code,200)
    '''
    /administrador/salidas-programadas/<slug:token>/listado-reservas/
    '''
    def testListadoReservas(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        salida_token = "DyeISHV8mO8D7BB4Bnqgfx1j"
        response = self.client.get('/administrador/salidas-programadas/'+salida_token+'/listado-reservas/')
        self.assertNotEqual(response.status_code,404)
    '''
    /administrador/salidas-programadas/<slug:token>/listado-pasajeros/
    '''
    def testListadoPasajeros(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        salida_token = "DyeISHV8mO8D7BB4Bnqgfx1j"
        response = self.client.get('/administrador/salidas-programadas/'+salida_token+'/listado-pasajeros/')
        self.assertNotEqual(response.status_code,404)
    
    '''
    /administrador/tours-registrados/
    '''
    def testToursRegistrados(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        response = self.client.get('/administrador/tours-registrados/')
        self.assertNotEqual(response.status_code,404)

    '''
    /administrador/
    '''
    def testDashboard(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        response = self.client.get('/administrador/')
        self.assertNotEqual(response.status_code,404)

    '''
    /administrador/salidas-programadas/
    '''
    def testSalidasProgramadas(self):
        self.client.login(username='admin222', password='Exploreit2021!')
        response = self.client.get('/administrador/salidas-programadas/')
        self.assertNotEqual(response.status_code,404)

'''
nombre + ' COPIA'
response = self.client.get('/administrador/categorias/', {'categoria': 'FUL','tipo':'NAC'})
def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')
'''
    
    
   