from typing import List
from behave import *

import json
from main_app.models import Salida, Tour, Incluye, NoIncluye, Importante, Reserva, ReservaPasajero, InteresadoTour, \
    Categoria
#Condiciones antes de empezar cualquier STEP
def before_scenario(context, scenario):
	context = {}
	print(context)

@given("a set of tours")
def step_impl(context):
	list = []

	for row in context.table:
		tour = Tour(row['NOMBRE'], row['DESCRIPCION'], row['UBICACION'], row['HORA_CHECKIN'], row['HORA_SALIDA'], row['HORA_RETORNO'], row['LUGAR_SALIDA'], row['TOKEN'], row['TIPO'], row['PRECIO'], row['DURACION'], row['CATEGORIA'], row['ABORDAJE_DIA_ANTERIOR'])
		list.append(tour)

	context.list = list

@given('the user enters the type: {name}')
def step_impl(context, name):
	context.name = name



@when("the user search tours by {criteria}")
def step_impl(context, criteria):
	if(criteria == 'name'):
		result, message = tours_registrados(context.list, context.name)
		print(result)
		context.result = result
		context.message = message



@then("{total} tours will match")
def step_impl(context, total):
	assert len(context.result) == int(total)


@then("the tours are")
def step_impl(context):
	expected = True
	result = []
	for row in context.table:
		result.append(row['NAME'])
	for x in context.result:
		if x.name not in result:
			print("No tours " + x.name)
			expected = False
	assert expected is True

@then("the following message is displayed: {message}")
def step_impl(context, message):
	print(message)
	print(context.message)
	assert context.message == message