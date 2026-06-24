from flask import Flask
import requests
import logging
from constants import API_BASE_URL

logger = logging.getLogger(__name__)

def enviar_reserva(datos):
    nombre = datos.get('nombre_cliente')
    email = datos.get('correo_electronico')
    telefono = datos.get('telefono-cliente')
    fecha = datos.get('fecha_reserva')
    hora = datos.get('horario_reserva')
    comensales = datos.get('cantidad_personas')
    servicios_extras_id = datos.get('servicios_extras')

    #convierto a entero
    servicios_extras_id_enteros = []

    for servicio in servicios_extras_id:
        conversion = int(servicio)
        servicios_extras_id_enteros.append(conversion)

    try:
        response = requests.post(f'{API_BASE_URL}/reservas',json={'nombre_cliente': nombre,'email': email,'telefono':telefono, 'fecha': fecha, 'hora': hora,'comensales' : int(comensales),"servicios_extras_id":servicios_extras_id_enteros},timeout=10,)

        if response.status_code == 201:
            return {'ok': True}
        else:
            return {
                'ok': False,
                'errores': [
                f"Error API {response.status_code}: {response.text}"
            ]
        }
        
    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return {'errores': ['No se pudo conectar con el servidor. Verifica que la API esté corriendo.']}

    except Exception as e:
        print(e)
        print(response.status_code)
        print(response.text)
        return {'errores': [str(e)]}

    

def eliminar_reserva(datos):
    email = datos.get('email') 
    fecha_reserva = datos.get('fecha_reserva')
    hora_reserva = datos.get('hora_reserva') 

    try:
        response = requests.delete(
            f'{API_BASE_URL}/admin/reservas', 
            json={'email': email, 'fecha_reserva': fecha_reserva, 'hora_reserva': hora_reserva}, timeout=10)

        if response.status_code == 204:
            return {'ok': True}
        else:
            return {
                'ok': False,
                'errores': [f"Error API {response.status_code}: {response.text}"]
            }

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return {'errores': ['No se pudo conectar con el servidor.']}
    except Exception as e:
        return {'errores': [str(e)]}
    
def obtener_disponibilidad(fecha, comensales):
    try:
        response = requests.get(f'{API_BASE_URL}/reservas/disponibilidad', params={'fecha': fecha, 'comensales': comensales}, timeout=10)

        if response.status_code == 200:
            return {'ok': True, 'data': response.json()}
        else:
            return {
                'ok': False,
                'errores': [f"Error API {response.status_code}: {response.text}"]
            }
    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return {'ok': False, 'errores': ['No se pudo conectar con el servidor de la API.']}
    except Exception as e:
        return {'ok': False, 'errores': [str(e)]}