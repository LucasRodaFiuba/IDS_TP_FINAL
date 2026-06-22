import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='restaurante_db',
            user='root',            # PONGAN SU USUARIO DE SQL ACA (puede estar predeterminado como "root")
            password=''    # PONGAN SU CONTRASEÑA DE SQL ACA
        )
        return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise e