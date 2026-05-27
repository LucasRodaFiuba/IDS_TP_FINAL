from flask import Flask
import requests
import logging
from constants import API_BASE_URL

logger = logging.getLogger(__name__)

def obtener_reservas():
    reservas = []

    try:
        response = requests.get(f'{API_BASE_URL}/reservas', timeout=10)

        if response.status_code == 200:
            reservas = response.json()

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return {'errores': ['No se pudo conectar con el servidor. Verifica que la API esté corriendo.']}

    except Exception:
        return {'errores': ['Ocurrió un error inesperado.']}
    return reservas

def enviar_reserva(fecha: str, hora: str, personas: int, nombre: str, telefono: str):

    try:
        response = requests.post(f'{API_BASE_URL}/reservas',json={'fecha': fecha,'hora': hora,'personas': personas, 'nombre': nombre, 'telefono': telefono},timeout=10,)

        if response.status_code == 201:
            return {'ok': True}
        else:
            return {'errores': ['El servidor no pudo registrar la reserva.']}
        
    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return {'errores': ['No se pudo conectar con el servidor. Verifica que la API esté corriendo.']}

    except Exception:
        return {'errores': ['Ocurrió un error inesperado.']}