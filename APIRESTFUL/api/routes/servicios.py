from flask import jsonify, request, Blueprint
from api.db import get_connection


servicios_extra_db= Blueprint("servicios_extra",__name__)


@servicios_extra_db.route("/")
def obtener_servicios_extra():
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM servicios_extra")
    servicios= cursor.fetchall()       
    cursor.close()
    conn.close()
    return jsonify(servicios), 200


@servicios_extra_db.route("/", methods= ['POST'])
def agregar_servicio():
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    data= request.json

    nombre= data.get("nombre")
    descripcion= data.get("descripcion")
    disponible= data.get("disponible")

    if not nombre or not descripcion or disponible is None:
     return jsonify({"error": "Todos los campos son obligatorios"}), 400

    
    cursor.execute("""INSERT INTO servicios_extra (nombre,descripcion,disponible)
                   VALUES (%s,%s,%s)
                   """,(nombre,descripcion,disponible))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'mensaje':'Servicio agregado correctamente'}), 201


@servicios_extra_db.route("/<int:id>", methods= ['PATCH'])
def acutualizar_servicio(id):
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    data = request.json
    disponible= data.get("disponible")
    if disponible is None:
        return jsonify({'error':'El campo es obligatorio'}),400

    cursor.execute("""UPDATE servicios_extra
                   SET disponible=%s
                   WHERE id=%s
                   """,(disponible,id))
    conn.commit()

    if cursor.rowcount== 0:
        cursor.close()
        conn.close()
        return jsonify({'error':'Servicio inexistente'}),404
    
    
    cursor.close()
    conn.close()

    return jsonify({'mensaje':'Servicio actualizado correctamente'}), 200

@servicios_extra_db.route("/<int:id>", methods= ['DELETE'])
def eliminar_servicio(id):
    conn= get_connection()
    cursor= conn.cursor(dictionary=True)
    
    cursor.execute("""DELETE FROM servicios_extra
                   WHERE id=%s""",(id,))
    conn.commit()

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()

        return jsonify({
            "error": "No existe un servicio con ese id"
        }), 404
    
    cursor.close()
    conn.close()
    return jsonify({'mensaje':'Eliminado correctamente'}), 200

    
