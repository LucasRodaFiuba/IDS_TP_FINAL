from flask import Flask
import requests
import logging
from constants import API_BASE_URL
logger = logging.getLogger(__name__) 
def obtener_menu():
    menu= {}

    try:
        response = requests.get(f'{API_BASE_URL}/menu', timeout=10)

        if response.status_code == 200:
            menu = response.json()

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

    except Exception as e:
        logger.error(f"Error al obtener el menu")

    return menu

def crear_plato(nombre: str, precio: float, descripcion: str, restriccion: str, categoria: str, imagen: str):
    try:
        response = requests.post(
                f'{API_BASE_URL}/admin/plato',
                json={'nombre': nombre, 'precio': precio, 'descripcion': descripcion, 'restriccion': restriccion , 'categoria': categoria, 'imagen': imagen },
                timeout=10,
            )
        if response.status_code == 201:
                    return {'ok': True}

    except requests.exceptions.ConnectionError:
            logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

    except Exception as e:
            logger.error(f"Error al obtener el menu")
            return {'errores': ['No se pudo conectar con el servidor. Verifica que la API este corriendo.']}
        
def eliminar_plato(nombre:str):
    try: 
        response = requests.delete(
            f'{API_BASE_URL}/menu/plato/eliminar',  
            json={'nombre': nombre},
            timeout=10,
        )
        return response  

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")
        return None

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None
    
def actualizar_plato(id: int, nombre: str, precio: float, descripcion: str, restriccion: str, categoria: str, imagen: str):
    try:
        response = requests.patch(
                f'{API_BASE_URL}/admin/plato/actualizar',
                json={'id': id,'nombre': nombre, 'precio': precio, 'descripcion': descripcion, 'restriccion': restriccion , 'categoria': categoria, 'imagen': imagen },
                timeout=10,
            )
        return response
    except requests.exceptions.ConnectionError:
            logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

    except Exception as e:
            logger.error(f"Error al obtener el menu")
            return {'errores': ['No se pudo conectar con el servidor. Verifica que la API este corriendo.']}
        