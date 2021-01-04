import random
import string

from django.db import models

# Create your models here.
from django.utils import timezone

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
    imagen              = models.ImageField(upload_to='tours')
    es_internacional    = models.BooleanField(default=False)
    capacidad           = models.IntegerField(default=0)
    precio              = models.FloatField()
    duracion            = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def obtener_info(self):
        incluye = Incluye.objects.filter(tour=self)
        no_incluye = NoIncluye.objects.filter(tour=self)
        importante = Importante.objects.filter(tour=self)
        proximas_salidas = Salida.objects.filter(tour=self).order_by('fecha_salida')
        return {'tour':self, 'incluye':incluye, 'no_incluye':no_incluye, 'importante':importante, 'proximas_salidas':proximas_salidas}

class Itinerario(models.Model):
    descripcion     = models.TextField()
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)
    siguiente       = models.ForeignKey("self", on_delete=models.PROTECT, null=True)
    dia             = models.IntegerField(null=True)

class Incluye(models.Model):
    nombre     = models.CharField(max_length=150)
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)

class NoIncluye(models.Model):
    nombre          = models.CharField(max_length=150)
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)

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

class ItinerarioVuelo(models.Model):
    fecha_ida       = models.DateTimeField()
    fecha_regreso   = models.DateTimeField()

class Reserva(models.Model):
    token           = models.CharField(max_length=10, null=True)
    fecha_creacion  = models.DateTimeField(default=timezone.now)
    salida          = models.ForeignKey(Salida, on_delete=models.PROTECT)
    acomodacion     = models.CharField(max_length=10, null=True)
    correo          = models.CharField(max_length=40)

    pagado          = models.BooleanField(default=False)
    de_baja         = models.BooleanField(default=False)

    @classmethod
    def generar_token(cls):
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
        return x

class ReservaPasajero(models.Model):
    token           = models.CharField(max_length=10, null=True)
    reserva         = models.ForeignKey(Reserva, on_delete=models.PROTECT)
    nombres         = models.CharField(max_length=100, null=True)
    apellidos       = models.CharField(max_length=100, null=True)
    cedula          = models.CharField(max_length=12, null=True)