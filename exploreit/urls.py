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
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from exploreit import settings
from main_app import views as main_views
from admin_app import views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index, name='index'),
    path('ver-reserva/', main_views.ver_reserva, name='ver_reserva'),
    path('tour-info/<slug:token>/', main_views.tour_info, name='tour_info'),
    path('tour-booking/<slug:token>/', main_views.tour_booking, name='tour_booking'),
    path('tour-booked/<slug:token>/', main_views.tour_booked, name='tour_booked'),
    path('tours/', main_views.tours, name='tours'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('administrador/', admin_views.dashboard, name='admin_dashboard'),
    path('administrador/salidas-programadas/', admin_views.salidas_programadas, name='salidas_programadas'),
    path('administrador/salidas-programadas/<slug:token>/listado-pasajeros/', admin_views.obtener_listado_pasajeros, name='listado_pasajeros'),
    path('administrador/salidas-programadas/<slug:token>/listado-reservas/', admin_views.obtener_listado_reservas,name='listado_reservas'),
    path('administrador/programar-salida/', admin_views.programar_salida, name='programar_salida'),
    path('administrador/registrar-tour/', admin_views.registrar_tour, name='registrar_tour'),
    path('administrador/editar-tour/<slug:slug>/', admin_views.editar_tour, name='editar_tour'),
    path('administrador/tours-registrados/', admin_views.tours_registrados, name='tours_registrados'),
    path('administrador/historial-salidas/', admin_views.historial_salidas, name='historial_salidas'),
    path('administrador/reserva-aprobar/', admin_views.reserva_aprobar, name='reserva_aprobar'),
    path('administrador/reserva-dar-de-baja/', admin_views.reserva_dar_de_baja, name='reserva_dar_de_baja'),
    path('administrador/login/', admin_views.admin_login, name='admin_login'),

    path('prueba-mail/', main_views.enviar_mail, name='enviar_mail')
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
