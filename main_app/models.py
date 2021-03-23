import os
import random
import string
import datetime
from enum import Enum

from django.db import models

# Create your models here.
from django.utils import timezone
from rest_framework.decorators import api_view

from exploreit import settings
import boto3
from botocore.exceptions import NoCredentialsError

from exploreit.helpers import decode_base64_file

class Categoria(models.Model):
    codigo          = models.CharField(max_length=6, unique=True, null=True)
    nombre          = models.CharField(max_length=10, null=True)

class Tour(models.Model):
    TIPO_CHOICES = (
        ('NAC', 'Nacional'),
        ('INT', 'Internacional'),
    )

    nombre                  = models.CharField(max_length=150)
    descripcion             = models.TextField()
    ubicacion               = models.CharField(max_length=60, null=True)
    hora_checkin            = models.CharField(max_length=10)
    hora_salida             = models.CharField(max_length=10)
    hora_retorno            = models.CharField(max_length=10)
    lugar_salida            = models.CharField(max_length=150)
    token                   = models.CharField(max_length=30, null=True)
    imagen                  = models.ImageField(upload_to=os.path.join('tours',str(id)))
    tipo                    = models.CharField(max_length=3, default='NAC', choices=TIPO_CHOICES)
    precio                  = models.FloatField()
    duracion                = models.IntegerField(default=0)
    categoria               = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True)
    abordaje_dia_anterior   = models.BooleanField(default=True)

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

    def get_interesados(self):
        return InteresadoTour.objects.filter(tour=self).count()

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

    def obtener_similares(self):
        return Tour.objects.filter(tipo=self.tipo).exclude(pk=self.pk).order_by('?')[:3]

    def obtener_duracion(self):
        itinerario = Itinerario.objects.filter(tour=self).order_by('-dia')
        if len(itinerario) > 0:
            return (Itinerario.objects.filter(tour=self).order_by('-dia')[0]).dia
        else:
            return 0

    def esta_disponible(self):
        proximas_salidas = Salida.objects.filter(tour=self, fecha_salida__range=[datetime.date.today(), '2030-12-31']).count()
        return proximas_salidas > 0

    def obtener_tipo_str(self):
        return dict(Tour.TIPO_CHOICES).get(self.tipo)


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
    capacidad       = models.IntegerField(default=0)

    def __str__(self):
        return str(self.tour.nombre)+' ('+str(self.fecha_salida)+')'

    @classmethod
    def generar_token(cls):
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
        return x

    def get_num_pasajeros(self):
        return ReservaPasajero.objects.filter(reserva__pagado=True, reserva__salida=self).count()

    def obtener_cupos_disponibles(self):
        pasajeros_confirmados = ReservaPasajero.objects.filter(reserva__salida=self, reserva__pagado=True, reserva__de_baja=False).count()
        return int(self.capacidad) - int(pasajeros_confirmados)

    def obtener_disponibilidad(self, cupos_solicitados):
        return self.obtener_cupos_disponibles() >= int(cupos_solicitados)

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
    comprobante     = models.CharField(max_length=100, null=True)

    pagado          = models.BooleanField(default=False)
    de_baja         = models.BooleanField(default=False)

    @classmethod
    def generar_token(cls):
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))
        return x

    def get_num_pasajeros(self):
        return ReservaPasajero.objects.filter(reserva=self).count()


    def upload_to_aws(self, base64_file, filename):
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        try:
            extension = filename.split('.')[1]
            file, file_name = decode_base64_file(base64_file)
            s3_filename = 'comprobante_' + str(self.token) + '.' + str(extension)
            self.comprobante = s3_filename
            s3.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                s3_filename,
                ExtraArgs={'ACL': 'public-read'}
            )
            self.save()
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def comprobante_es_imagen(self):
        try:
            tipo = self.comprobante.split('.')[1]
            return  tipo == 'jpg' or tipo == 'png' or tipo == 'jpeg'
        except:
            return False

    def comprobante_es_documento(self):
        try:
            tipo = self.comprobante.split('.')[1]
            return  tipo != 'jpg' or tipo != 'png' or tipo != 'jpeg'
        except:
            return False

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

class InteresadoTour(models.Model):
    cliente         = models.CharField(max_length=50)
    tour            = models.ForeignKey(Tour, on_delete=models.CASCADE)