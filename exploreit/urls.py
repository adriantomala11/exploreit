"""exploreit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from exploreit import settings
from main_app import views as main_views
from admin_app import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index, name='index'),
    path('tour-info/<slug:token>/', main_views.tour_info, name='tour_info'),
    path('tour-booking/<slug:token>/', main_views.tour_booking, name='tour_booking'),
    path('tour-booked/<slug:token>/', main_views.tour_booked, name='tour_booked'),
    path('administrador/', admin_views.dashboard, name='admin_dashboard'),
    path('administrador/salidas-programadas/', admin_views.salidas_programadas, name='salidas_programadas'),
    path('administrador/salidas-programadas/<slug:token>/listado-pasajeros/', admin_views.obtener_listado_pasajeros, name='listado_pasajeros'),
    path('administrador/salidas-programadas/<slug:token>/listado-reservas/', admin_views.obtener_listado_reservas,name='listado_reservas'),
    path('administrador/programar-salida/', admin_views.programar_salida, name='programar_salida'),
    path('administrador/registrar_tour/', admin_views.registrar_tour, name='registrar_tour'),
    path('administrador/tours-registrados/', admin_views.tours_registrados, name='tours_registrados'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
