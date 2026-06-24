import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = '/'
DB_URL = os.getenv("DATABASE_URL")

# Formato de fecha esperado por la API
FORMATO_FECHA = '%Y-%m-%d'

# Formato de horario esperado por la API
FORMATO_HORARIO = '%H:%M'

#valores minimos y máximos de comensales
MIN_COMENSALES = 1
MAX_COMENSALES = 10

#valores minimos y máximos de ids para servicios extras
MIN_ID = 1
MAX_ID = 7

#Horarios fijos en que se pueden hacer la reserva (18-23hs)
HORARIOS_PARA_RESERVAR = ["18:00","19:00","20:00","21:00","22:00","23:00"]

#Errores tipo code
ERROR_CODE_INVALID_MIN_VALUE   = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE   = 'invalid.max.value'

#Para validar las restricciones y categorias
RESTRICCIONES_VALIDAS = {'ninguno','sin lactosa', 'vegetariano', 'vegano', 'sin tacc'}
CATEGORIAS_VALIDAS    = {'bebida', 'entrada', 'postre', 'plato_principal'}
 
