from flask import Flask, render_template, request, redirect, url_for
from services.reservas import obtener_reservas, enviar_reserva
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
# Carpeta donde se guardan las imágenes
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img')


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/nosotros')
def pagina_nosotros():
    return render_template('nosotros.html')

@app.route('/reservas', methods=['GET', 'POST'])
def pagina_reservas():
    if request.method == 'POST':
        fecha = request.form.get('fecha_reserva')
        hora = request.form.get('horario_reserva')
        personas = request.form.get('cantidad_personas')
        nombre = request.form.get('nombre_cliente')

        resultado = enviar_reserva(fecha, hora, personas, nombre)

        if 'ok' in resultado:
            return redirect(url_for('reservas.pagina_reservas', exito=True))
        else:
            return render_template('reservas.html', reservas=obtener_reservas(), errores_api=resultado['errores'])

    lista_reservas = obtener_reservas()

    return render_template('reservas.html', reservas=lista_reservas, exito=request.args.get('exito'))

@app.route('/clientes')
def pagina_clientes():
    return render_template('clientes.html')


@app.route('/iniciar_sesion')
def iniciar_sesion():
    return render_template('iniciar_sesion.html')

@app.route('/admin')
def pagina_admin():
    return render_template('admin.html')

@app.route('/admin/reservas')
def admin_reservas():
    return render_template('admin_reservas.html')

@app.route('/admin/clientes')
def admin_clientes():
    return render_template('admin_clientes.html')

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='restaurante_db',
            user='nacho',
            password='1234'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

@app.route('/admin/menu', methods=['POST'])
def agregar_objeto():
    conn = get_db_connection()
    cursor = conn.cursor()

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    vegetariano = request.form.get('vegetariano', False)
    vegano = request.form.get('vegano', False)
    sin_tacc = request.form.get('sin_tacc', False)
    sin_lactosa = request.form.get('sin_lactosa', False)
    categoria = request.form['categoria']
    # Procesar imagen
    imagen_url = None

    # Si subieron archivo
    imagen = request.files.get('imagen')
    if imagen and imagen.filename != '':
        filename = secure_filename(imagen.filename)
        imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagen_url = f"/static/img/{filename}"

    # Si pegaron URL
    if not imagen_url:  # solo si no se subió archivo
        imagen_url = request.form.get('imagen_url')
    cursor.execute("""
        INSERT INTO menu (nombre, descripcion, precio, vegetariano, vegano, sin_tacc, sin_lactosa, categoria, imagen_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (nombre, descripcion, precio, vegetariano, vegano, sin_tacc, sin_lactosa, categoria, imagen_url))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('pagina_menu'))

@app.route('/menu')
def pagina_menu():
    conn = get_db_connection()
    if conn is None:
        return "Error: no se pudo conectar a la base de datos", 500

    cursor = conn.cursor(dictionary=True)  # mysql.connector soporta dictionary=True

    cursor.execute("SELECT * FROM menu")
    platos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("menu.html", platos=platos)

@app.route('/admin/menu/entradas', methods=['POST'])
def agregar_entrada():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/plato', methods=['POST'])
def agregar_plato():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/postre', methods=['POST'])
def agregar_postre():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/bebida', methods=['POST'])
def agregar_bebida():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']
    
@app.route('/admin/menu/modificar', methods=['UPDATE'])
def modificar_objeto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    ingredientes = request.form['ingredientes']

@app.route('/admin/menu/eliminar', methods=['DELETE'])
def eliminar_objeto():
    nombre = request.form['nombre']

@app.route('/admin/reservas/agregar', methods=['POST'])
def agregar_reserva():
    nombre_cliente = request.form['nombre_cliente']
    fecha_hora = request.form['fecha_hora']
    cantidad_personas = request.form['cantidad_personas']

@app.route('/admin/reservas/modificar', methods=['UPDATE'])
def modificar_reserva():
    nombre_cliente = request.form['nombre_cliente']
    fecha_hora_reserva = request.form['fecha_hora_reserva']
    nueva_fecha_hora = request.form['nueva_fecha_hora']

@app.route('/admin/reservas/eliminar', methods=['DELETE'])
def eliminar_reserva():
    nombre_cliente = request.form['nombre_cliente']
    fecha_hora = request.form['fecha_hora']

@app.route('/admin/usuarios/agregar', methods=['POST'])
def agregar_usuario():
    nombre_usuario = request.form['nombre_usuario']
    correo_electronico = request.form['correo_electronico']
    contrase単a = request.form['contrase単a']

@app.route('/admin/usuarios/modificar', methods=['UPDATE'])
def modificar_usuario():
    nombre_usuario = request.form['nombre_usuario']
    nuevo_nombre_usuario = request.form['nuevo_nombre_usuario']
    nuevo_correo_electronico = request.form['nuevo_correo_electronico']
    nueva_contrase単a = request.form['nueva_contrase単a']

@app.route('/admin/usuarios/eliminar', methods=['DELETE'])
def eliminar_usuario():
    nombre_usuario = request.form['nombre_usuario']

if __name__ == "__main__":
    app.run(debug=True)
