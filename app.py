from flask import Flask, render_template, request, redirect, url_for,flash, session
#from services.reservas import obtener_reservas, enviar_reserva
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
import os
from services.reservas import enviar_reserva
from services.mis_reservas import obtener_reservas,cancelar_reserva_service 
from services.auth import (
    eliminar_usuario_api,
    iniciar_sesion_api,
    obtener_perfil_usuario_api,
    registrar_usuario_api,
    solicitar_recuperacion_password_api,
)

app = Flask(__name__)
# Carpeta donde se guardan las imágenes
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img')

app.secret_key = "dev-secret-key-123"

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/nosotros')
def pagina_nosotros():
    return render_template('nosotros.html')

@app.route('/reservas', methods=['GET', 'POST'])
def pagina_reservas():
    if request.method == 'POST':
        data = request.form.to_dict()
        #Hago posible que servicios extras tenga como valor una lista.
        data['servicios_extras'] = request.form.getlist('servicios_extras')

        resultado = enviar_reserva(data)

        if resultado.get("ok"):
            flash("Reserva creada", "success")
            return redirect(url_for("pagina_reservas"))
        
        #Manejo caso en el que tira 404 (no se puede reservar si el usuario no está)
        errores = resultado.get("errores", [])
        # 5. Busco específicamente el error de usuario no registrado
        # any(...) recorre todos los errores y chequea si alguno contiene ese código
        if any("usuario.no.existe" in str(e) for e in errores):

            # muestro mensaje al usuario en pantalla
            flash("Tenés que iniciar sesión primero", "error")

            # redirijo al login y termino la ejecución
            return redirect(url_for("iniciar_sesion"))

        # 6. Si no era ese error específico, muestro todos los errores generales
        for e in errores:
            flash(e, "error")

        # 7. Vuelvo a la página de reservas con los errores mostrados
        return redirect(url_for("pagina_reservas"))

    # 8. Si es GET, simplemente muestro la página
    return render_template("reservas.html")

@app.route('/clientes')
def pagina_clientes():
    return render_template('clientes.html')


@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        resultado = iniciar_sesion_api(email, password)

        if resultado.get('ok'):
            data = resultado.get('data', {})
            usuario = data.get('usuario', {})
            session['token'] = data.get('token')
            session['usuario'] = usuario
            flash('Inicio de sesion correcto', 'success')
            return redirect(url_for('perfil'))

        for error in resultado.get('errores', []):
            flash(error, 'error')

    return render_template('iniciar_sesion.html')
    
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        resultado = registrar_usuario_api(request.form.to_dict())

        if resultado.get('ok'):
            flash('Cuenta creada correctamente. Ya podes iniciar sesion.', 'success')
            return redirect(url_for('iniciar_sesion'))

        for error in resultado.get('errores', []):
            flash(error, 'error')

    return render_template('registro.html')


@app.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        email = request.form.get('email', '')
        resultado = solicitar_recuperacion_password_api(email)

        if resultado.get('ok'):
            flash('Solicitud de recuperacion enviada.', 'success')
            return redirect(url_for('iniciar_sesion'))

        for error in resultado.get('errores', []):
            flash(error, 'error')

    return render_template('recuperar_contrasena.html')


@app.route('/perfil')
def perfil():
    usuario_sesion = session.get('usuario')
    token = session.get('token')

    if not usuario_sesion or not token:
        flash('Tenes que iniciar sesion primero.', 'error')
        return redirect(url_for('iniciar_sesion'))

    usuario_id = usuario_sesion.get('id')
    resultado = obtener_perfil_usuario_api(usuario_id, token)

    if not resultado.get('ok'):
        for error in resultado.get('errores', []):
            flash(error, 'error')
        return redirect(url_for('iniciar_sesion'))

    data = resultado.get('data', {})
    return render_template(
        'perfil.html',
        usuario=data.get('usuario', usuario_sesion),
        reservas=data.get('reservas', [])
    )


@app.route('/cerrar_sesion', methods=['POST'])
def cerrar_sesion():
    session.clear()
    flash('Sesion cerrada correctamente.', 'success')
    return redirect(url_for('iniciar_sesion'))


@app.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    usuario_sesion = session.get('usuario')
    token = session.get('token')

    if not usuario_sesion or not token:
        flash('Tenes que iniciar sesion primero.', 'error')
        return redirect(url_for('iniciar_sesion'))

    resultado = eliminar_usuario_api(usuario_sesion.get('id'), token)

    if resultado.get('ok'):
        session.clear()
        flash('Cuenta eliminada correctamente.', 'success')
        return redirect(url_for('home'))

    for error in resultado.get('errores', []):
        flash(error, 'error')

    return redirect(url_for('perfil'))

@app.route('/admin')
def pagina_admin():
    return render_template('admin.html')

@app.route('/admin/reservas')
def admin_reservas():
    return render_template('admin_reservas.html')

@app.route('/admin/clientes')
def admin_clientes():
    return render_template('admin_clientes.html')

@app.route('/mis_reservas', methods=['GET'])
def pagina_mis_reservas():
    #Obtengo email logeado
    usuario = session.get("usuario")

    if not usuario:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("iniciar_sesion"))

    email = usuario.get("email")

    if not email:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("iniciar_sesion"))

    #uso services
    resultado = obtener_reservas(email)
    
    if resultado.get("ok"):
        flash("Reservas obtenidas", "success")
        return render_template("mis_reservas.html",reservas=resultado['response'])
        
    errores = resultado.get("errores", [])
    
    for e in errores:
        flash(e, "error")

    return render_template("mis_reservas.html", reservas=None)

#FUNCIONALIDAD botón cancelar de mis_reservas
@app.route('/cancelar_reserva/<int:id_reserva>', methods=['POST'])
def cancelar_reserva(id_reserva):
    cancelar_reserva_service(id_reserva)
    return redirect(url_for("pagina_mis_reservas"))


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

@app.route('/admin/dashboard')
def pagina_dashboard():
    fecha_inicio = request.args.get('fecha_inicio', '2026-05-01')
    fecha_fin = request.args.get('fecha_fin', '2026-05-31')


    datos_ficticios = {
        "fecha_analisis_inicio": fecha_inicio,
        "fecha_analisis_fin": fecha_fin,
        "resumen_operaciones": {
            "total_reservas_activas": 142,
            "total_cubiertos_proyectados": 418,
            "ingreso_estimado_ars": 11913000.00 
        },
        "rendimiento_carta": {
            "plato_estrella": "Ojo de Bife Madurado",
            "servicio_mas_solicitado": "Maridaje Exclusivo con Sommelier"
        },
        "ultimas_reservas": [
            {
                "id": 1031,
                "nombre_cliente": "Lionel Messi",
                "fecha": "2026-05-05",
                "hora": "21:30",
                "comensales": 5,
                "estado": "confirmada",
                "notas_especiales": "Mesa VIP. Requires máxima discreción y seguridad."
            },
            {
                "id": 1036,
                "nombre_cliente": "Sofía Martínez",
                "fecha": "2026-05-06",
                "hora": "19:30",
                "comensales": 2,
                "estado": "confirmada",
                "notas_especiales": "Un comensal tiene alergia severa a los mariscos."
            },
            {
                "id": 1037,
                "nombre_cliente": "Juan Pérez",
                "fecha": "2026-05-07",
                "hora": "13:00",
                "comensales": 8,
                "estado": "confirmada",
                "notas_especiales": "Almuerzo familiar. Necesitan espacio para un cochecito de bebé."
            },
            {
                "id": 1038,
                "nombre_cliente": "Ricardo Fort",
                "fecha": "2026-05-08",
                "hora": "23:00",
                "comensales": 4,
                "estado": "confirmada",
                "notas_especiales": "Quiere el mejor champagne de la carta listo y frío en la mesa al llegar."
            },
            {
                "id": 1034,
                "nombre_cliente": "Ana Rodríguez",
                "fecha": "2026-05-14",
                "hora": "20:00",
                "comensales": 2,
                "estado": "confirmada",
                "notas_especiales": "Cena romántica de aniversario. ¿Tienen option de flores en la mesa?"
            },
            {
                "id": 1033,
                "nombre_cliente": "Carlos Fernández",
                "fecha": "2026-05-15",
                "hora": "21:00",
                "comensales": 4,
                "estado": "confirmada",
                "notas_especiales": ""
            },
            {
                "id": 1031,
                "nombre_cliente": "Lionel Messi",
                "fecha": "2026-05-18",
                "hora": "21:30",
                "comensales": 5,
                "estado": "cancelada",
                "notas_especiales": "Mesa VIP. Requires máxima discreción y seguridad."
            },
            {
                "id": 1031,
                "nombre_cliente": "Lionel Messi",
                "fecha": "2026-05-20",
                "hora": "21:30",
                "comensales": 5,
                "estado": "cancelada",
                "notas_especiales": "Mesa VIP. Requires máxima discreción y seguridad."
            },
            {
                "id": 1027,
                "nombre_cliente": "Martina Galperin",
                "fecha": "2026-05-22",
                "hora": "21:00",
                "comensales": 6,
                "estado": "confirmada",
                "notas_especiales": "Cena corporativa. Solicita discreción y mesa alejada del centro."
            },
            {
                "id": 1026,
                "nombre_cliente": "Alejandro Bozou",
                "fecha": "2026-05-27",
                "hora": "22:15",
                "comensales": 2,
                "estado": "cancelada",
                "notas_especiales": ""
            },
            {
                "id": 1035,
                "nombre_cliente": "Diego Maradona",
                "fecha": "2026-05-28",
                "hora": "22:00",
                "comensales": 6,
                "estado": "confirmada",
                "notas_especiales": "Reserva cancelada por imprevisto."
            },
            {
                "id": 1030,
                "nombre_cliente": "Miguel Angel",
                "fecha": "2026-05-29",
                "hora": "20:30",
                "comensales": 2,
                "estado": "confirmada",
                "notes_especiales": "Mesa tranquila, prefiere sector del patio."
            },
            {
                "id": 1025,
                "nombre_cliente": "Juan Pérez",
                "fecha": "2026-05-30",
                "hora": "20:00",
                "comensales": 4,
                "estado": "pendiente",
                "notas_especiales": "Un comensal requiere menú estricto sin TACC."
            },
            {
                "id": 1032,
                "nombre_cliente": "María Gómez",
                "fecha": "2026-05-31",
                "hora": "19:00",
                "comensales": 3,
                "estado": "pendiente",
                "notas_especiales": "Festejo de cumpleaños, solicita porción de torta con velita."
            }
    ]
}
    return render_template('dashboard.html', data=datos_ficticios, f_inicio=datos_ficticios["fecha_analisis_inicio"], f_fin=datos_ficticios["fecha_analisis_fin"])

if __name__ == "__main__":
    app.run(debug=True,port = 5001)
