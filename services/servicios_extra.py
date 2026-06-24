from flask import Flask
import requests
import logging
from constants import API_BASE_URL

logger = logging.getLogger(__name__)

def obtener_servicios_extra() -> dict:
    try:
        servicios=[]

        response= requests.get(f'{API_BASE_URL}/servicios_extra',timeout=10)

        if response.status_code == 200:
            servicios= response.json()


    except requests.exceptions.Timeout:
        logger.error("Timeout al conectar con la API")

    except requests.exceptions.ConnectionError:
        logger.error(f'No se puedo conectar con la api en {API_BASE_URL}')
        return{'ok':False, 'error':'server_down'}

    except Exception as e:
        logger.error(f'Error al obtener los servicios extra:{e}')

    return servicios

def agregar_servicio_extra(nombre, descripcion)-> dict:
    try:
        response = requests.post(
            f'{API_BASE_URL}/servicios_extra',
            json={
                'nombre': nombre,
                'descripcion': descripcion
            },
            timeout=10
        )

        if response.status_code == 201:
            return {'ok': True}

    except requests.exceptions.ConnectionError:
        logger.error(f'No se puedo conectar con la api en {API_BASE_URL}')
        return {'ok':False,'error':'server_down'}

    except requests.exceptions.Timeout:
        logger.error("Timeout al enviar servicio")

    except Exception as e:
        logger.error(f'Error al agregar servicio extra:{e}')

def actualizar_servicio_extra(id_servicio,nombre,descripcion):
    try:
        response= requests.patch(f'{API_BASE_URL}/servicios_extra/{id_servicio}',
            json={'id_servicio':id_servicio,
                  'nombre':nombre,
                  'descripcion':descripcion},
            timeout=10
            )
        
        if response.status_code ==  200:
            return {'ok':True}
        if response.status_code == 404:
            return {'ok':False,'error':'not_found'}

    except requests.exceptions.Timeout:
        logger.error("Timeout al enviar servicio")

        
    except requests.exceptions.ConnectionError:
        logger.error(f'No se puedo conectar con la api en {API_BASE_URL}')
        return {'ok':False,'error':'server_down'}

    except Exception as e:
        logger.error(f'Error al eliminar el servicio extra:{e}')



def eliminar_servicio_extra(id_servicio)-> dict:
    try:
        response= requests.delete(
            f'{API_BASE_URL}/servicios_extra/{id_servicio}',
            json={'id_servicio':id_servicio},
            timeout=10
            )

        
        if response.status_code ==  200:
            return {'ok':True}
        if response.status_code == 404:
            return {'ok':False,'error':'not_found'}
        
    
    except requests.exceptions.Timeout:
        logger.error("Timeout al enviar servicio")

        
    except requests.exceptions.ConnectionError:
        logger.error(f'No se puedo conectar con la api en {API_BASE_URL}')
        return {'ok':False,'error':'server_down'}

    except Exception as e:
        logger.error(f'Error al eliminar el servicio extra:{e}')


