from django.contrib import admin
from main_app.models import *

admin.site.register(Tour)
admin.site.register(Salida)
admin.site.register(Reserva)
admin.site.register(ReservaPasajero)
admin.site.register(Itinerario)
admin.site.register(ItinerarioVuelo)
admin.site.register(Incluye)
admin.site.register(NoIncluye)
admin.site.register(Importante)
admin.site.register(InteresadoTour)
admin.site.register(Categoria)
admin.site.register(Agencia)
admin.site.register(AgenciaUsuario)

# Register your models here.
