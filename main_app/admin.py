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

# Register your models here.
