from sqlalchemy import create_engine, text
from .constantes import DB_URL
from datetime import datetime, timedelta

# Motor de conexion compartido por toda la aplicacion.
# El pool de conexiones lo maneja SQLAlchemy automaticamente.
motor = create_engine(DB_URL, pool_pre_ping=True)


# ---------------------------------------------------------------
# Funciones de soporte
# ---------------------------------------------------------------

def fila_a_dict(fila) -> dict:
    """Convierte una fila del resultado de una query en un diccionario."""
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict = None) -> list[dict]:
    """Ejecuta una SELECT y devuelve todas las filas como lista de dicts."""
    with motor.connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_insert(sql: str, parametros: dict = None) -> int:
    """
    Ejecuta un INSERT, UPDATE o DELETE y hace commit.
    Retorna el id autoincremental generado por el INSERT (0 si no aplica).
    """
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0

def ejecutar_mutacion(sql, parametros=None):
    with motor.begin() as conexion:
        result = conexion.execute(text(sql), parametros or {})
        return result.rowcount

#--------------------------------------------------------------------------
#  RESERVAS
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
# Queries para crear reservas (especialmente)
#--------------------------------------------------------------------------
def obtener_mesas_por_capacidad(min_capacidad):
    query = """
        SELECT *
        FROM mesas
        WHERE capacidad >= :capacidad
    """
    return ejecutar_consulta(query, {'capacidad': min_capacidad})


def mesa_ocupada(numero_mesa, fecha, hora):
    query = """
        SELECT *
        FROM reservas
        WHERE numero_mesa = :numero_mesa
            AND fecha_reserva = :fecha_reserva
            AND hora_reserva = :hora_reserva
    """
    reserva = ejecutar_consulta(query, {
        'numero_mesa': numero_mesa,
        'fecha_reserva': fecha,
        'hora_reserva': hora
    })

    if reserva:
        return True
    return False

def añadir_reserva(id_usuario,numero_mesa,fecha,hora,comensales,codigo_qr):
    query = """
        INSERT INTO reservas(
          id_usuario, numero_mesa, fecha_reserva, hora_reserva, cantidad_personas,codigo_qr 
        ) VALUES (:id_usuario,:numero_mesa,:fecha_reserva,:hora_reserva,:cantidad_personas,:codigo_qr)
    """
    return ejecutar_insert(query,{'id_usuario':id_usuario, 'numero_mesa':numero_mesa,'fecha_reserva':fecha,'hora_reserva':hora,'cantidad_personas':comensales,'codigo_qr':codigo_qr})


def obtener_usuario_por_email(email):
    """
    Permite obtener el id_usuario basándose en el email 
    recibido.
    """
    query = """
        SELECT id_usuario
        FROM usuarios
        WHERE email = :email
    """

    resultado = ejecutar_consulta(query, {
        'email': email
    })

    if resultado:
        return resultado[0]['id_usuario']

    return None

#--------------------------------------------------------------------------
# Queries para modificar reservas (especialmente)
#--------------------------------------------------------------------------
def update_reserva(id_reserva, datos):
    query = """
        UPDATE reservas
        SET fecha_reserva = :fecha_reserva,
            hora_reserva = :hora_reserva,
            cantidad_personas = :cantidad_personas
        WHERE id_reserva = :id
    """

    parametros = {
        "id": id_reserva,
        "fecha_reserva": datos["fecha"],
        "hora_reserva": datos["hora"],
        "cantidad_personas": datos["comensales"]
    }

    ejecutar_mutacion(query, parametros)


def obtener_id_usuario(id_reserva):
    query = """
        SELECT id_usuario
        FROM reservas
        WHERE id_reserva = :id
    """

    resultado = ejecutar_consulta(query, {"id": id_reserva})

    if not resultado:
        return None

    return resultado[0]["id_usuario"]

def update_usuario(id_usuario, datos):
    query = """
        UPDATE usuarios
        SET nombre = :nombre,
            email = :email,
            telefono = :telefono
        WHERE id_usuario = :id
    """

    parametros = {
        "id": id_usuario,
        "nombre": datos["nombre_cliente"],
        "email": datos["email"],
        "telefono": datos["telefono"]
    }

    ejecutar_mutacion(query, parametros)

def actualizar_servicios_reserva(id_reserva, servicios_extras):
    
    # Borro los servicios extras actuales de la reserva
    query_delete = """
        DELETE FROM reserva_servicios
        WHERE id_reserva = :id_reserva
    """

    ejecutar_mutacion(
        query_delete,
        {'id_reserva': id_reserva},
    )

    # Inserto los nuevos servicios
    query_insert = """
        INSERT INTO reserva_servicios (
            id_reserva,
            id_servicio
        )
        VALUES (
            :id_reserva,
            :id_servicio
        )
    """

    for id_servicio in servicios_extras:

        ejecutar_insert(
            query_insert,
            {
                'id_reserva': id_reserva,
                'id_servicio': id_servicio
            }
        )

#--------------------------------------------------------------------------
# Queries para modificar reservas (especialmente)
#--------------------------------------------------------------------------
def cancelar_reserva(id_reserva):
    query = """
        UPDATE reservas
        SET estado = 'cancelada'
        WHERE id_reserva = :id_reserva
    """

    resultado = ejecutar_mutacion(query,{'id_reserva':id_reserva})

    if resultado == 0:
        return False
    return True


#--------------------------------------------------------------------------
# Queries relacionadas con tokens y QR
#--------------------------------------------------------------------------

def buscar_reserva_por_token(token):
    query = """
        SELECT estado
        FROM reservas
        WHERE codigo_qr = :codigo_qr
    """

    resultados =  ejecutar_consulta(query,{'codigo_qr':token})

    if resultados:
        return resultados[0]
    return None

def actualizar_estado_reserva(token,nuevo_estado):
    query = """
        UPDATE reservas
        SET estado = :estado
        WHERE codigo_qr = :codigo_qr
    """

    ejecutar_mutacion(query, {
        "estado": nuevo_estado,
        "codigo_qr": token
    })
    
# <=========================> CUENTAS DE USUARIO <============================>

def obtener_rol_por_nombre(nombre_rol):
    query = """
    SELECT id_rol, nombre
    FROM roles
    WHERE nombre = :nombre
    """
    resultado = ejecutar_consulta(query, {'nombre': nombre_rol})
    if resultado:
        return resultado[0]
    return None


def obtener_usuario_publico_por_id(id_usuario):
    query = """
    SELECT
        u.id_usuario,
        u.nombre,
        u.apellido,
        u.email,
        u.telefono,
        u.fecha_registro,
        r.nombre AS rol
    FROM usuarios u
    INNER JOIN roles r ON r.id_rol = u.id_rol
    WHERE u.id_usuario = :id_usuario
    """
    resultado = ejecutar_consulta(query, {'id_usuario': id_usuario})
    if resultado:
        return resultado[0]
    return None


def obtener_usuario_publico_por_email(email):
    query = """
    SELECT
        u.id_usuario,
        u.nombre,
        u.apellido,
        u.email,
        u.telefono,
        u.fecha_registro,
        r.nombre AS rol
    FROM usuarios u
    INNER JOIN roles r ON r.id_rol = u.id_rol
    WHERE u.email = :email
    """
    resultado = ejecutar_consulta(query, {'email': email})
    if resultado:
        return resultado[0]
    return None


def obtener_usuario_auth_por_email(email):
    query = """
    SELECT
        u.id_usuario,
        u.nombre,
        u.apellido,
        u.email,
        u.password,
        r.nombre AS rol
    FROM usuarios u
    INNER JOIN roles r ON r.id_rol = u.id_rol
    WHERE u.email = :email
    """
    resultado = ejecutar_consulta(query, {'email': email})
    if resultado:
        return resultado[0]
    return None


def insertar_usuario_auth(nombre, apellido, email, password_hash, telefono, id_rol):
    query = """
    INSERT INTO usuarios
        (nombre, apellido, email, password, telefono, id_rol)
    VALUES
        (:nombre, :apellido, :email, :password, :telefono, :id_rol)
    """
    return ejecutar_insert(query, {
        'nombre': nombre,
        'apellido': apellido,
        'email': email,
        'password': password_hash,
        'telefono': telefono,
        'id_rol': id_rol,
    })


def obtener_reservas_de_usuario(id_usuario):
    query = """
    SELECT
        id_reserva,
        numero_mesa,
        fecha_reserva,
        hora_reserva,
        cantidad_personas,
        estado,
        codigo_qr,
        fecha_creacion
    FROM reservas
    WHERE id_usuario = :id_usuario
    ORDER BY fecha_reserva DESC, hora_reserva DESC
    """
    return ejecutar_consulta(query, {'id_usuario': id_usuario})


def eliminar_usuario_por_id(id_usuario):
    query = """
    DELETE FROM usuarios
    WHERE id_usuario = :id_usuario
    """
    return ejecutar_mutacion(query, {'id_usuario': id_usuario})


def registrar_log_usuario(id_usuario, accion):
    query = """
    INSERT INTO logs (id_usuario, accion)
    VALUES (:id_usuario, :accion)
    """
    return ejecutar_insert(query, {
        'id_usuario': id_usuario,
        'accion': accion,
    })

def obtener_servicios_extra():
    query= """SELECT * FROM servicios_extra"""

    resultado= ejecutar_consulta(query)

    return resultado



def agregar_servicio_extra(nombre,descripcion):
    query= """INSERT INTO servicios_extra (nombre,descripcion)
              VALUES (:nombre,:descripcion)"""
    
    datos= {
        "nombre": nombre,
        "descripcion":descripcion
    }

    resultado= ejecutar_insert(query,datos)

    return resultado


def obtener_servicio_por_id(id_servicio):
    query= """SELECT * FROM servicios_extra WHERE id_servicio= :id_servicio"""

    datos = {
        "id_servicio": id_servicio
    }

    resultado= ejecutar_consulta(query,datos)


    if not resultado:
        return None

    return resultado[0]



def actualizar_servicio_extra(id_servicio,nombre,descripcion):
    query= """UPDATE servicios_extra
              SET nombre= :nombre, descripcion= :descripcion
              WHERE id_servicio= :id_servicio"""
    
    datos={
        "id_servicio":id_servicio,
        "nombre":nombre,
        "descripcion":descripcion

    }

    resultado= ejecutar_mutacion(query,datos)

    return resultado

  

def eliminar_servicio_extra(id_servicio):
    query= """DELETE FROM servicios_extra WHERE id_servicio = :id_servicio"""

    datos={
        "id_servicio": id_servicio
    }

    resultado= ejecutar_mutacion(query,datos)
    
    return resultado
