from api.db import get_db_connection

def obtener_platos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_plato AS id, nombre, precio, descripcion, categoria, restriccion, imagen FROM menu",
    )
    platos = cursor.fetchall()
    cursor.close()
    connection.close()
    return platos
def obtener_plato_por_nombre (nombre):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_plato FROM menu WHERE nombre = %s", (nombre,))
    plato = cursor.fetchone()
    cursor.close()
    connection.close()
    return plato
def obtener_plato_por_id (id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu WHERE id_plato = %s", (id,))
    plato = cursor.fetchone()
    cursor.close()
    connection.close()
    return plato

def insertar_plato(nombre, descripcion, precio, restriccion, categoria, imagen):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO menu (nombre, descripcion, precio, restriccion, categoria, imagen) VALUES (%s, %s, %s, %s, %s, %s)",
        (nombre, descripcion, precio, restriccion, categoria, imagen)
    )
    connection.commit()
    cursor.close()
    connection.close()
 
 
def actualizar_plato(id, nombre, descripcion, precio, restriccion, categoria, imagen):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE menu SET nombre=%s, descripcion=%s, precio=%s, restriccion=%s, categoria=%s, imagen=%s WHERE id_plato=%s",
        (nombre, descripcion, precio, restriccion, categoria, imagen, id)
    )
    connection.commit()
    cursor.close()
    connection.close()
 
 
def eliminar_plato_por_nombre(nombre):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM menu WHERE nombre = %s", (nombre,))
    connection.commit()
    cursor.close()
    connection.close()
