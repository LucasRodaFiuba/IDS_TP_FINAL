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


def ejecutar_mutacion(sql: str, parametros: dict = None) -> int:
    """
    Ejecuta un INSERT, UPDATE o DELETE y hace commit.
    Retorna el id autoincremental generado por el INSERT (0 si no aplica).
    """
    with motor.begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0

#--------------------------------------------------------------------------
#  RESERVAS
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
# Queries para crear reservas
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
    return ejecutar_mutacion(query,{'id_usuario':id_usuario, 'numero_mesa':numero_mesa,'fecha_reserva':fecha,'hora_reserva':hora,'cantidad_personas':comensales})


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