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

def actualizar_usuario(id_usuario: int , nombre: str, apellido: str, email: str, telefono: str):

    try:
        response = requests.put(f'{API_BASE_URL}/admin/usuarios/actualizar/{id_usuario}',
                                json={ "nombre": nombre,"apellido": apellido, "email": email, "telefono": telefono},
                                timeout=10)

        if response.status_code == 200:
            usuarios = response.json()

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

    except Exception as e:
        logger.error(f"Error al obtener los usuarios")

def crear_usuario(nombre: str, apellido: str, email: str, password: str, telefono: str, rol: str):
    try:
        response = requests.post(f'{API_BASE_URL}/usuarios', json={
            'nombre': nombre,
            'apellido': apellido,
            'email': email,
            'password': password,
            'telefono': telefono,
            'rol': rol
        }, timeout=10)

        if response.status_code == 201:
            usuarios = response.json()

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

    except Exception as e:
        logger.error(f"Error al obtener los usuarios")