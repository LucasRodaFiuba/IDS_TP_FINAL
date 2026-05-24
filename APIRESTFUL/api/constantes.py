BASE_URL = '/'
DB_URL = "mysql+pymysql://appuser:1234@localhost/restaurante_db"
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

#Errores tipo code
ERROR_CODE_INVALID_MIN_VALUE   = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE   = 'invalid.max.value'