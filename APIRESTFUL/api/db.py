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

def añadir_reserva(id_usuario,numero_mesa,fecha,hora,comensales):
    query = """
        INSERT INTO reservas(
          id_usuario, numero_mesa, fecha_reserva, hora_reserva, cantidad_personas 
        ) VALUES (:id_usuario,:numero_mesa,:fecha_reserva,:hora_reserva,:cantidad_personas)
    """
    return ejecutar_insert(query,{'id_usuario':id_usuario, 'numero_mesa':numero_mesa,'fecha_reserva':fecha,'hora_reserva':hora,'cantidad_personas':comensales})


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