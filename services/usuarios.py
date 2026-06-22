from flask import Flask
import requests
import logging
from constants import API_BASE_URL
logger = logging.getLogger(__name__) 


def obtener_usuarios():
    usuarios = {}

    try:
        response = requests.get(f'{API_BASE_URL}/admin/usuarios', timeout=10)

        if response.status_code == 200:
            usuarios = response.json()

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

    except Exception as e:
        logger.error(f"Error al obtener los usuarios")

    return usuarios

def actualizar_rol_usuario(id_usuario: int):
    try:
        response = requests.put(f'{API_BASE_URL}/admin/usuarios/actualizar_rol/{id_usuario}', timeout=10)

        if response.status_code == 200:
            usuarios = response.json()

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

    except Exception as e:
        logger.error(f"Error al obtener los usuarios")