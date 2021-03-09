import os
import random
import string
import datetime

from django.db import models

# Create your models here.
from django.utils import timezone
from rest_framework.decorators import api_view

from exploreit import settings


class Tour(models.Model):
    nombre              = models.CharField(max_length=150)
    descripcion         = models.TextField()
    ubicacion           = models.CharField(max_length=60, null=True)
    tipo                = models.CharField(max_length=10)
    hora_checkin        = models.CharField(max_length=10)
    hora_salida         = models.CharField(max_length=10)
    hora_retorno        = models.CharField(max_length=10)
    lugar_salida        = models.CharField(max_length=150)
    token               = models.CharField(max_length=30, null=True)
    imagen              = models.ImageField(upload_to=os.path.join('tours',str(id)))
    es_internacional    = models.BooleanField(default=False)
    capacidad           = models.IntegerField(default=0)
    precio              = models.FloatField()
    duracion            = models.IntegerField(default=0)

    # def __str__(self):
    #     return self.nombre

    def obtener_info(self):
        incluye = Incluye.objects.filter(tour=self)
        no_incluye = NoIncluye.objects.filter(tour=self)
        importante = Importante.objects.filter(tour=self)
        itinerario = Itinerario.objects.filter(tour=self).order_by('dia')
        itinerario_dict = {}
        for iti in itinerario:
            try:
                itinerario_dict[str(iti.dia)].append(iti.descripcion)
            except:
                itinerario_dict[str(iti.dia)] = []
                itinerario_dict[str(iti.dia)].append(iti.descripcion)
        proximas_salidas = Salida.objects.filter(tour=self, fecha_salida__range=[datetime.date.today(), '2030-12-31']).order_by('fecha_salida')
        return {'tour':self, 'incluye':incluye, 'no_incluye':no_incluye, 'importante':importante, 'proximas_salidas':proximas_salidas, 'itinerario': itinerario_dict}

    def eliminar_incluyes(self):
        items = Incluye.objects.filter(tour=self)
        items.delete()

    def eliminar_no_incluyes(self):
        items = NoIncluye.objects.filter(tour=self)
        items.delete()

    def eliminar_itinerarios(self):
        items = Itinerario.objects.filter(tour=self)
        items.delete()

    def imagen_url(self):
        return os.path.join(settings.MEDIA_URL, 'tours', str(self.id), str(self.imagen))

    @classmethod
    def to_response_dict(cls, tours):
        response_dict = []
        for tour in tours:
            tour_dict = {
                'id': tour.id,
                'nombre': tour.nombre,
                'precio': tour.precio,
                'descripcion': tour.descripcion,
                'imagen': tour.imagen_url(),
                'ubicacion': tour.ubicacion
            }
            response_dict.append(tour_dict)
        return response_dict

class Itinerario(models.Model):
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)
    dia             = models.IntegerField(null=True)
    descripcion     = models.CharField(max_length=300, null=True)

    @classmethod
    def queryset_to_dict(cls, queryset):
        dict = {}
        for item in queryset:
            dict[str(item.id)] = {'descripcion': item.descripcion}
        return dict

    @classmethod
    def queryset_to_list(cls, queryset):
        list = []
        for item in queryset:
            list.append({'id':item.id, 'descripcion': item.descripcion})
        return list


class Incluye(models.Model):
    nombre     = models.CharField(max_length=150)
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)

    @classmethod
    def queryset_to_dict(cls, queryset):
        dict = {}
        for item in queryset:
            dict[str(item.id)] = {'nombre': item.nombre}
        return dict

    @classmethod
    def queryset_to_list(cls, queryset):
        list = []
        for item in queryset:
            list.append({'id':item.id,'nombre': item.nombre})
        return list

class NoIncluye(models.Model):
    nombre          = models.CharField(max_length=150)
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)

    @classmethod
    def queryset_to_dict(cls, queryset):
        dict = {}
        for item in queryset:
            dict[str(item.id)] = {'nombre': item.nombre}
        return dict

    @classmethod
    def queryset_to_list(cls, queryset):
        list = []
        for item in queryset:
            list.append({'id':item.id,'nombre': item.nombre})
        return list

class Importante(models.Model):
    descripcion     = models.CharField(max_length=300)
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)

class Salida(models.Model):
    tour            = models.ForeignKey(Tour, on_delete=models.PROTECT)
    fecha_salida    = models.DateField()
    token           = models.CharField(max_length=30, null=True)

    def __str__(self):
        return str(self.tour.nombre)+' ('+str(self.fecha_salida)+')'

    @classmethod
    def generar_token(cls):
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
        return x

    def get_num_pasajeros(self):
        return ReservaPasajero.objects.filter(reserva__pagado=True, reserva__salida=self).count()

class ItinerarioVuelo(models.Model):
    fecha_ida       = models.DateTimeField()
    fecha_regreso   = models.DateTimeField()

class Reserva(models.Model):
    token           = models.CharField(max_length=10, null=True)
    fecha_creacion  = models.DateTimeField(default=timezone.now)
    salida          = models.ForeignKey(Salida, on_delete=models.PROTECT)
    acomodacion     = models.CharField(max_length=10, null=True)
    correo          = models.CharField(max_length=40)
    nombre          = models.CharField(max_length=40)
    apellido        = models.CharField(max_length=40)
    cedula          = models.CharField(max_length=15)
    telefono        = models.CharField(max_length=20, null=True)

    pagado          = models.BooleanField(default=False)
    de_baja         = models.BooleanField(default=False)

    @classmethod
    def generar_token(cls):
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
        return x

    def get_num_pasajeros(self):
        return ReservaPasajero.objects.filter(reserva=self).count()

class ReservaPasajero(models.Model):
    token           = models.CharField(max_length=10, null=True)
    reserva         = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    nombres         = models.CharField(max_length=100, null=True)
    apellidos       = models.CharField(max_length=100, null=True)
    edad            = models.IntegerField(null=True)
    cedula          = models.CharField(max_length=12, null=True)

    @classmethod
    def generar_token(self):
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
        return str(self.id) + x


class Tipo(models.Model):
    nombre          = models.CharField(max_length=10, null=True)

class Categoria(models.Model):
    nombre          = models.CharField(max_length=10, null=True)

class Continente(models.Model):
    nombre          = models.CharField(max_length=10, null=True)