import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='restaurante_db',
            user='nacho',            # PONGAN SU USUARIO DE SQL ACA (puede estar predeterminado como "root")
            password='1234'    # PONGAN SU CONTRASEÑA DE SQL ACA
        )
        return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise e