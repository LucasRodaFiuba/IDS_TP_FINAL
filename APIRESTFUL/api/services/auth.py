from datetime import datetime, timedelta, timezone
from functools import wraps
import os
import secrets

import bcrypt
import jwt
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from api import db_funciones
from api.services.usuarios import construir_usuario_dto
from api.utils import construir_error_api
from api.validators.auth import (
    validar_body_login,
    validar_body_olvido_password,
    validar_body_registro,
)


JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-cambiar-en-produccion')
JWT_ALGORITHM = 'HS256'
JWT_EXP_HORAS = int(os.environ.get('JWT_EXP_HORAS', '8'))


def hashear_password(password):
    hash_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hash_bytes.decode('utf-8')


def verificar_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except (ValueError, TypeError):
        return False


def generar_token(usuario):
    ahora = datetime.now(timezone.utc)
    payload = {
        'sub': str(usuario['id_usuario']),
        'email': usuario['email'],
        'rol': usuario['rol'],
        'iat': ahora,
        'exp': ahora + timedelta(hours=JWT_EXP_HORAS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError(construir_error_api(
            code='auth.token.expired',
            message='Token expirado',
            description='El token de autenticacion expiro. Vuelva a iniciar sesion.'
        ), 401)
    except jwt.InvalidTokenError:
        raise ValueError(construir_error_api(
            code='auth.token.invalid',
            message='Token invalido',
            description='El token de autenticacion no es valido.'
        ), 401)


def extraer_token_del_header():
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        raise ValueError(construir_error_api(
            code='auth.token.missing',
            message='Token de autenticacion faltante',
            description='Debe enviarse el header Authorization con el formato Bearer <token>'
        ), 401)
    return header[len('Bearer '):].strip()


def requiere_auth():
    def decorador(funcion):
        @wraps(funcion)
        def wrapper(*args, **kwargs):
            try:
                token = extraer_token_del_header()
                request.usuario_actual = decodificar_token(token)
            except ValueError as e:
                status = e.args[1] if len(e.args) > 1 else 401
                return jsonify(e.args[0]), status

            return funcion(*args, **kwargs)
        return wrapper
    return decorador


def registrar_usuario(body):
    datos = validar_body_registro(body)

    rol = db_funciones.obtener_rol_por_nombre(datos['rol'])
    if not rol:
        raise ValueError(construir_error_api(
            code='invalid.rol',
            message='Rol invalido',
            description=f"El rol '{datos['rol']}' no existe en la base de datos"
        ), 400)

    try:
        id_usuario = db_funciones.insertar_usuario_auth(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email'],
            password_hash=hashear_password(datos['password']),
            telefono=datos['telefono'],
            id_rol=rol['id_rol'],
        )
    except IntegrityError:
        raise ValueError(construir_error_api(
            code='email.already.registered',
            message='Email ya registrado',
            description=f"Ya existe un usuario con email '{datos['email']}'"
        ), 409)

    usuario = db_funciones.obtener_usuario_publico_por_id(id_usuario)
    return {
        'token': generar_token(usuario),
        'tipo': 'Bearer',
        'usuario': construir_usuario_dto(usuario),
    }


def autenticar_usuario(body):
    datos = validar_body_login(body)
    usuario = db_funciones.obtener_usuario_auth_por_email(datos['email'])

    if not usuario or not verificar_password(datos['password'], usuario['password']):
        raise ValueError(construir_error_api(
            code='invalid.credentials',
            message='Credenciales invalidas',
            description='El email o password son incorrectos'
        ), 401)

    return {
        'token': generar_token(usuario),
        'tipo': 'Bearer',
        'usuario': construir_usuario_dto(usuario),
    }


def solicitar_recuperacion_password(body):
    datos = validar_body_olvido_password(body)
    usuario = db_funciones.obtener_usuario_publico_por_email(datos['email'])

    mensaje = 'Si el email existe, se enviaran instrucciones de recuperacion'
    if not usuario:
        return {'mensaje': mensaje}

    token_recuperacion = secrets.token_urlsafe(32)
    db_funciones.registrar_log_usuario(
        usuario['id_usuario'],
        f'Solicitud de recuperacion de password. Token: {token_recuperacion}'
    )

    return {
        'mensaje': mensaje,
        'token_dev': token_recuperacion,
    }
