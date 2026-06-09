import requests
from constants import API_BASE_URL


def _extraer_errores(respuesta):
    try:
        data = respuesta.json()
    except ValueError:
        return ["Error inesperado al comunicarse con el servidor."]

    errores = data.get("errors") if isinstance(data, dict) else None
    if not errores:
        if isinstance(data, dict) and data.get("message"):
            return [data.get("message")]
        return ["Ocurrió un error inesperado."]

    mensajes = []
    for error in errores:
        if isinstance(error, dict):
            mensajes.append(error.get("description") or error.get("message") or str(error))
        else:
            mensajes.append(str(error))
    return mensajes


def iniciar_sesion_api(email, password):
    try:
        respuesta = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
    except requests.RequestException:
        return {"ok": False, "errores": ["No se pudo conectar con el backend."]}

    if respuesta.ok:
        return {"ok": True, "data": respuesta.json()}

    return {"ok": False, "errores": _extraer_errores(respuesta)}


def registrar_usuario_api(data):
    payload = {
        "nombre": data.get("nombre", ""),
        "apellido": data.get("apellido", ""),
        "email": data.get("email", ""),
        "password": data.get("password", ""),
        "rol": "cliente",
        "telefono": data.get("telefono", ""),
    }

    try:
        respuesta = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=payload,
            timeout=10,
        )
    except requests.RequestException:
        return {"ok": False, "errores": ["No se pudo conectar con el backend."]}

    if respuesta.ok:
        return {"ok": True, "data": respuesta.json()}

    return {"ok": False, "errores": _extraer_errores(respuesta)}


def solicitar_recuperacion_password_api(email):
    try:
        respuesta = requests.post(
            f"{API_BASE_URL}/auth/forgot-password",
            json={"email": email},
            timeout=10,
        )
    except requests.RequestException:
        return {"ok": False, "errores": ["No se pudo conectar con el backend."]}

    if respuesta.ok:
        return {"ok": True, "data": respuesta.json()}

    return {"ok": False, "errores": _extraer_errores(respuesta)}


def obtener_perfil_usuario_api(usuario_id, token):
    try:
        respuesta = requests.get(
            f"{API_BASE_URL}/usuarios/{usuario_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except requests.RequestException:
        return {"ok": False, "errores": ["No se pudo conectar con el backend."]}

    if respuesta.ok:
        return {"ok": True, "data": respuesta.json()}

    return {"ok": False, "errores": _extraer_errores(respuesta)}


def eliminar_usuario_api(usuario_id, token):
    try:
        respuesta = requests.delete(
            f"{API_BASE_URL}/usuarios/{usuario_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except requests.RequestException:
        return {"ok": False, "errores": ["No se pudo conectar con el backend."]}

    if respuesta.status_code == 204:
        return {"ok": True}

    if respuesta.ok:
        return {"ok": True, "data": respuesta.json() if respuesta.content else {}}

    return {"ok": False, "errores": _extraer_errores(respuesta)}
