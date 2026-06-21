import requests
import logging
from front_app.constants import API_BASE_URL

logger = logging.getLogger(__name__)

def obtener_resenas():
    try:
        response = requests.get(f'{API_BASE_URL}/resenas', timeout=10)

        if response.status_code == 200:
            return {'ok': True, 'response': response.json()}
        else:
            return {'ok': False, 'errores': [f"Error API {response.status_code}"]}

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return {'errores': ['No se pudo conectar con el servidor.']}

    except Exception as e:
        logger.error(e)
        return {'errores': [str(e)]}


def enviar_resena(id_usuario, id_reserva, puntuacion, comentario, token):
    try:
        response = requests.post(
            f'{API_BASE_URL}/resenas',
            json={
                'id_usuario': id_usuario,
                'id_reserva': id_reserva,
                'puntuacion': puntuacion,
                'comentario': comentario
            },
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        if response.status_code == 201:
            return {'ok': True}
        return {'ok': False, 'errores': [f'Error {response.status_code}']}

    except Exception as e:
        return {'ok': False, 'errores': [str(e)]}