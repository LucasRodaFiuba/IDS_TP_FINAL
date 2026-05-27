from api.utils import (
    construir_error_api,
    validar_email,
    validar_string_no_vacio,
    validar_telefono,
)


ROLES_VALIDOS = ('cliente', 'admin')
PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 255


def _validar_body_presente(body):
    if not isinstance(body, dict):
        raise ValueError(construir_error_api(
            code='invalid.body',
            message='Cuerpo de la solicitud invalido',
            description='El cuerpo debe ser un JSON valido con Content-Type application/json'
        ))


def _limpiar_string_opcional(valor):
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor if valor else None


def _separar_nombre_apellido(nombre_completo):
    partes = str(nombre_completo).strip().split()
    if len(partes) <= 1:
        return partes[0], ''
    return partes[0], ' '.join(partes[1:])


def validar_body_registro(body):
    _validar_body_presente(body)
    errores = []
    nombre = None
    apellido = None
    email = None
    password = None
    telefono = None
    rol = None

    try:
        nombre_raw = validar_string_no_vacio(body.get('nombre'), 'nombre')
        apellido_raw = _limpiar_string_opcional(body.get('apellido'))
        if apellido_raw is None:
            nombre, apellido = _separar_nombre_apellido(nombre_raw)
        else:
            nombre = nombre_raw
            apellido = apellido_raw
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        email = validar_string_no_vacio(body.get('email'), 'email')
        email = validar_email(email, 'email').lower()
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        password = validar_string_no_vacio(body.get('password'), 'password')
        if len(password) < PASSWORD_MIN_LEN or len(password) > PASSWORD_MAX_LEN:
            raise ValueError(construir_error_api(
                code='invalid.password.length',
                message='Longitud de password invalida',
                description=f'El password debe tener entre {PASSWORD_MIN_LEN} y {PASSWORD_MAX_LEN} caracteres'
            ))
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        rol = _limpiar_string_opcional(body.get('rol')) or 'cliente'
        rol = rol.lower()
        if rol not in ROLES_VALIDOS:
            raise ValueError(construir_error_api(
                code='invalid.rol',
                message='Rol invalido',
                description=f"El rol debe ser uno de: {', '.join(ROLES_VALIDOS)}"
            ))
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        telefono = _limpiar_string_opcional(body.get('telefono'))
        if telefono is not None:
            telefono = validar_telefono(telefono, 'telefono')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'password': password,
        'telefono': telefono,
        'rol': rol,
    }


def validar_body_login(body):
    _validar_body_presente(body)
    errores = []
    email = None
    password = None

    try:
        email = validar_string_no_vacio(body.get('email'), 'email')
        email = validar_email(email, 'email').lower()
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    try:
        password = validar_string_no_vacio(body.get('password'), 'password')
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {'email': email, 'password': password}


def validar_body_olvido_password(body):
    _validar_body_presente(body)
    errores = []
    email = None

    try:
        email = validar_string_no_vacio(body.get('email'), 'email')
        email = validar_email(email, 'email').lower()
    except ValueError as e:
        errores.extend(e.args[0]['errors'])

    if errores:
        raise ValueError({'errors': errores})

    return {'email': email}
