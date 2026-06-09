from ..constantes import FORMATO_FECHA, FORMATO_HORARIO, MIN_COMENSALES, MAX_COMENSALES, MIN_ID, MAX_ID
from ..utils import (
    construir_error_api,
    validar_formato_fecha_o_horario,
    validar_entero,
    validar_telefono,
    validar_email,
    validar_string_no_vacio,
    validar_maximo,
    validar_minimo,
    validar_que_sea_lista
)
from datetime import datetime, date

def validar_id(id) -> int:
    """Valida que el id recibido sea un entero positivo."""
    id = validar_entero(id, 'padron')

    return validar_minimo(id, 1, 'padron')


def validar_parametros(fecha,comensales):
    """
    Valida los parámetros de  GET /reservas/disponibilidad.
    Dos casos:
    1.Los datos son válidos entonces devuelve los parámetros en forma de diccionario
    2.Hay algún error de validación y devuelve error.
    """

    if fecha is None or comensales is None:
        raise ValueError(construir_error_api(
            code='invalid.params',
            message='Parámetros inválidos',
            description='Faltan fecha o comensales en la query'
        ))

    errores = []

    fecha_valida = None
    comensales_valido = None

    try:
        fecha_str = validar_string_no_vacio(fecha, 'fecha')
        validar_formato_fecha_o_horario(fecha_str, FORMATO_FECHA, 'fecha')
        fecha_valida = fecha_str
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        comensales_val = validar_entero(comensales, 'comensales')
        comensales_val = validar_minimo(comensales_val, MIN_COMENSALES, 'comensales')
        comensales_val = validar_maximo(comensales_val, MAX_COMENSALES, 'comensales')
        comensales_valido = comensales_val
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError(construir_error_api(
            code='validation.error',
            message='Error de validación',
            description='Los parámetros no son válidos'
        ))
    print(fecha_valida)
    print(comensales_valido)

    return {
        'fecha': fecha_valida,
        'comensales': comensales_valido
    }


def validar_body_nueva_reserva(body: dict) -> dict:
    """
    Valida el body del POST /reservas.
    Dos casos:
    1.Los datos son válidos entonces devuelve el body en forma de diccionario
    2.Hay algún error de validación y devuelve error.
    """
    if body is None:
        raise ValueError(construir_error_api(
            code='invalid.body',
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON valido con Content-Type application/json'
        ))

    errores = []

    #inicializo campos en None, en caso de que tenga algún error
    nombre_del_cliente = None
    email = None
    telefono = None
    fecha = None
    hora = None
    comensales = None
    servicios_extras_id = None
    notas_especiales = None

    #Valido nombre del cliente
    try:
        nombre_del_cliente = validar_string_no_vacio(body.get('nombre_cliente'), 'nombre_cliente')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    #valido email
    try:
        email = validar_string_no_vacio(body.get('email'),'email')
        email = validar_email(email, 'email')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    #valido telefono
    try:
        telefono = validar_string_no_vacio(body.get('telefono'),'telefono')
        telefono = validar_telefono(telefono,'telefono')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    #valido fecha (aseguro que no sea una fecha del pasado)
    try:
        fecha_str = validar_string_no_vacio(body.get('fecha'), 'fecha')
        fecha_dt = validar_formato_fecha_o_horario(fecha_str, FORMATO_FECHA, 'fecha')
        if fecha_dt.date() < date.today():
            errores.append({
                "code": "fecha.invalida",
                "message": "Fecha inválida",
                "description": "No podés reservar en una fecha pasada",
                "field": "fecha"
            })
        fecha = fecha_str
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    #valido hora
    try:
        hora_str = validar_string_no_vacio(body.get('hora'), 'hora')
        hora = validar_formato_fecha_o_horario(hora_str, FORMATO_HORARIO, 'hora')
        hora = hora.strftime("%H:%M:%S")
    except ValueError as e:
        errores.extend(e.args[0]['errors'])
    
    #valido cantidad de comensales
    try:
        comensales = validar_entero(body.get('comensales'), 'comensales')
        #valido rango permitido de comensales
        comensales = validar_minimo(comensales, MIN_COMENSALES, 'comensales')
        comensales = validar_maximo(comensales, MAX_COMENSALES, 'comensales')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    #valido servicios_extras_id
    try:
        servicios_extras_id = body.get('servicios_extras_id')

        servicios_validos = []

        if servicios_extras_id is not None:

            validar_que_sea_lista(servicios_extras_id, 'servicios_extras_id')

            for servicio in servicios_extras_id:

                servicio = validar_entero(servicio, 'servicios_extras')

                validar_minimo(servicio, MIN_ID, 'servicios_extras')
                validar_maximo(servicio, MAX_ID, 'servicios_extras')

                servicios_validos.append(servicio)

            servicios_extras_id = servicios_validos

        else:
            servicios_extras_id = None

    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    #Valido notas_especiales
    try:
        notas_especiales = body.get("notas_especiales")
        #notas_especiales = validar_string_no_vacio(body.get('notas_especiales'), 'Notas_especiales')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    #Si tengo algún error, se levanta uun error.
    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre_cliente': nombre_del_cliente,
        'email':   email,
        'telefono':  telefono,
        'fecha' : fecha,
        'hora' : hora,
        'comensales' : comensales,
        'servicios_extras_id' : servicios_extras_id,
        'notas_especiales' : notas_especiales
    }
