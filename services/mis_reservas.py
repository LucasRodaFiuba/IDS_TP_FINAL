from flask import Flask
import requests
import logging
from constants import API_BASE_URL

logger = logging.getLogger(__name__)

def obtener_reservas(email):
    try:
        response = requests.get(f'{API_BASE_URL}/reservas/usuario/{email}',timeout=10,)

        if response.status_code == 200:
            return {'ok': True,'response':response.json()}
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

def cancelar_reserva_service(id_reserva):
    try:
        response = requests.post(f'{API_BASE_URL}/reservas/{id_reserva}',timeout=10)
        if response.status_code == 204:
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