from flask import Flask
import requests
import logging
from constants import API_BASE_URL 
logger = logging.getLogger(__name__)
 
 
def obtener_menu(limit=20, offset=0):
    try:
        response = requests.get(
            f'{API_BASE_URL}/menu',
            params={'_limit': limit, '_offset': offset},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return {}
 
    except Exception as e:
        logger.error(f"Error al obtener el menu: {e}")
        return {}
 
 
def crear_plato(nombre: str, precio: float, descripcion: str, restriccion: str, categoria: str, imagen: str):
    try:
        response = requests.post(
            f'{API_BASE_URL}/admin/plato',
            json={'nombre': nombre, 'precio': precio, 'descripcion': descripcion,
                  'restriccion': restriccion, 'categoria': categoria, 'imagen': imagen},
            timeout=10,
        )
        if response.status_code == 201:
            return {'ok': True}
 
        return {'ok': False, 'error': response.json()}
 
    except Exception as e:
        logger.error(f"Error inesperado al crear el plato: {e}")
        return {'ok': False}
 
 
def eliminar_plato(nombre: str):
    try:
        response = requests.delete(
            f'{API_BASE_URL}/menu/plato/eliminar',
            json={'nombre': nombre},
            timeout=10,
        )
        if response.status_code == 204:
            return {'ok': True}
 
        return {'ok': False, 'error': response.json()}
 
    except Exception as e:
        logger.error(f"Error inesperado al eliminar el plato: {e}")
        return {'ok': False}
 
 
def actualizar_plato(id: int, nombre: str, precio: float, descripcion: str, restriccion: str, categoria: str, imagen: str):
    try:
        response = requests.patch(
            f'{API_BASE_URL}/admin/plato/actualizar',
            json={'id': id, 'nombre': nombre, 'precio': precio, 'descripcion': descripcion,
                  'restriccion': restriccion, 'categoria': categoria, 'imagen': imagen},
            timeout=10,
        )
        if response.status_code == 204:
            return {'ok': True}
 
        return {'ok': False, 'error': response.json()}
 
    except Exception as e:
        logger.error(f"Error inesperado al actualizar el plato: {e}")
        return {'ok': False}