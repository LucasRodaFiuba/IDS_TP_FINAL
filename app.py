from flask import Flask, render_template, request, redirect, url_for,flash, session
import requests
from services.resenas import obtener_resenas, enviar_resena, eliminar_resena
#from services.reservas import obtener_reservas, enviar_reserva
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
import os
from services.menu import obtener_menu,crear_plato,eliminar_plato,actualizar_plato
from services.reservas import crear_reserva_admin, enviar_reserva, eliminar_reserva, obtener_disponibilidad
from services.mis_reservas import obtener_reservas,cancelar_reserva_service
from services.auth import (
    eliminar_usuario_api,
    iniciar_sesion_api,
    obtener_perfil_usuario_api,
    registrar_usuario_api,
    solicitar_recuperacion_password_api,
)
from routes.servicios_extra import servicios_extra_bp
from services.servicios_extra import obtener_servicios_extra
from services.dashboard import obtener_estadisticas
from services.usuarios import obtener_usuarios,actualizar_rol_usuario, crear_usuario, actualizar_usuario
from datetime import datetime
from constants import MESES

app = Flask(__name__)
# Carpeta donde se guardan las imágenes
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img')

app.secret_key = "dev-secret-key-123"

app.register_blueprint(servicios_extra_bp)

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/admin/usuarios')
def pagina_usuarios():
    data = obtener_usuarios()
    usuarios = data.get('usuarios', [])
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/admin/agregar_usuario', methods=['POST'])
def agregar_usuario():
    nombre = request.form.get('usuario')
    apellido = request.form.get('apellido')
    email = request.form.get('correo')
    password = request.form.get('password_hash')
    telefono = request.form.get('telefono')
    rol = request.form.get('id_rol')
    crear_usuario(nombre, apellido, email, password, telefono, rol)
    if not nombre or not email or not password or not rol:
        flash('Todos los campos son obligatorios.', 'error')
    else:
        flash('Usuario agregado correctamente.', 'success')
    return redirect(url_for('pagina_usuarios'))

@app.route('/admin/usuarios/modificar', methods=['POST'])
def modificar_usuario():
    id_usuario = request.form.get('id')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    email = request.form.get('email')
    telefono = request.form.get('telefono')

    resultado = actualizar_usuario(
        int(id_usuario),
        nombre,
        apellido,
        email,
        telefono
    )

    if resultado:
        flash('Usuario actualizado correctamente', 'success')
    else:
        flash('No se pudo actualizar el usuario', 'error')

    return redirect(url_for('pagina_usuarios'))

@app.route('/admin/usuarios/eliminar/<int:id_usuario>', methods=['POST'])
def eliminar_usuario(id_usuario):
    usuario = session.get('usuario')
    token = session.get('token')

    if not usuario or usuario.get('rol') != 'admin':
        flash('No tenés permisos para esto.', 'error')
        return redirect(url_for('pagina_usuarios'))

    resultado = eliminar_usuario_api(id_usuario, token)

    if resultado.get('ok'):
        flash('Usuario eliminado.', 'success')
    else:
        for e in resultado.get('errores', []):
            flash(e, 'error')
    usuario = session.get('usuario')
    token = session.get('token')
    return redirect(url_for('pagina_usuarios'))


@app.route('/nosotros')
def pagina_nosotros():
    return render_template('nosotros.html')

@app.route('/reservas', methods=['GET', 'POST'])
def pagina_reservas():

    usuario = session.get("usuario")

    if not usuario:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("iniciar_sesion"))

    email = usuario.get("email")

    if not email:
        flash("Tenés que iniciar sesión primero", "error")
        return redirect(url_for("iniciar_sesion"))

    if request.method == 'POST':
        data = request.form.to_dict()
        data['servicios_extras'] = request.form.getlist('servicios_extras')
        resultado = enviar_reserva(data)

        if resultado.get('ok'):
            flash("¡Tu reserva en Le Maison Gourmet ha sido registrada con éxito!", "success")
            return redirect(url_for('pagina_mis_reservas'))
        else:
            errores = resultado.get('errores', ['Error desconocido al procesar la reserva.'])
            for e in errores:
                flash(f"Hubo un problema: {e}", "error")
            return redirect(url_for('pagina_reservas'))
    

    fecha_seleccionada = request.args.get('fecha')
    comensales = request.args.get('comensales')
    
    horarios_disponibles = []
    
    if fecha_seleccionada:
        resultado = obtener_disponibilidad(fecha=fecha_seleccionada, comensales=comensales)
        
        if resultado.get('ok'):
            horarios_disponibles = resultado['data'].get('turnos_disponibles', [])
        else:
            for e in resultado.get('errores', []):
                flash(f"No se pudieron cargar los horarios: {e}", "error")

    servicios_extra = obtener_servicios_extra()

    return render_template("reservas.html", horarios=horarios_disponibles, comensales_seleccionados=comensales, fecha_seleccionada=fecha_seleccionada, servicios_extra=servicios_extra)

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
        flash('Tenes que iniciar sesion primero.', 'login_error')
        return redirect(url_for('iniciar_sesion'))

    usuario_id = usuario_sesion.get('id')
    resultado = obtener_perfil_usuario_api(usuario_id, token)

    if not resultado.get('ok'):
        for error in resultado.get('errores', []):
            flash(error, 'login_error')
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
        flash('Tenes que iniciar sesion primero.', 'login_error')
        return redirect(url_for('iniciar_sesion'))

    resultado = eliminar_usuario_api(usuario_sesion.get('id'), token)

    if resultado.get('ok'):
        session.clear()
        flash('Cuenta eliminada correctamente.', 'success')
        return redirect(url_for('home'))

    for error in resultado.get('errores', []):
        flash(error, 'login_error')

    return redirect(url_for('perfil'))

@app.route('/admin')
def pagina_admin():
    servicios_extra = obtener_servicios_extra()
    return render_template('admin.html', servicios_extra=servicios_extra)

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
        reservas = resultado['response']

        for reserva in reservas:
            fecha = datetime.strptime(reserva['fecha_reserva'], "%Y-%m-%d")
            reserva['mes_abreviado'] = MESES[fecha.month - 1]
            reserva['dia'] = fecha.day

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


@app.route('/admin/menu', methods=['POST'])
def agregar_objeto():
    nombre = request.form.get('nombre', '').strip()
    precio = request.form.get('precio', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    restriccion = request.form.get('restriccion', 'ninguno').strip()
    categoria = request.form.get('categoria', '').strip()
    imagen = request.form.get('imagen', '').strip()

    imagen = None
    archivo = request.files.get('imagen')
    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagen = f"/static/img/{filename}"
    else:
        imagen = request.form.get('imagen', '').strip()   
    
    resultado = crear_plato(nombre, precio, descripcion, restriccion, categoria, imagen) 
    if not resultado['ok']:
        errores = resultado['error'].get('errors', [])
        mensaje_error = errores[0].get('description', 'No se pudo crear el plato') if errores else 'No se pudo actualizar el plato'
        flash(mensaje_error, 'error')  
        return redirect(url_for('pagina_admin')) 

 
    flash('Plato creado exitosamente', 'success')
    return redirect(url_for('pagina_menu'))


@app.route('/menu')
def pagina_menu():
    data = obtener_menu()
    platos = data.get('platos', [])
    return render_template('menu.html', platos=platos)

    
@app.route('/admin/menu/modificar', methods=['POST'])
def modificar_objeto():
    id =request.form.get('id')
    nombre = request.form.get('nombre')
    precio = request.form.get('precio') or None
    descripcion = request.form.get('descripcion')
    restriccion = request.form.get('restriccion')
    categoria = request.form.get('categoria')
    archivo = request.files.get('imagen')
   
    imagen_url = None
    if archivo and archivo.filename != '':
        nombre_archivo = archivo.filename
        archivo.save(f'static/img/{nombre_archivo}')
        imagen_url = f'/static/img/{nombre_archivo}'

    resultado = actualizar_plato(id, nombre, precio, descripcion, restriccion, categoria, imagen_url)
    if not resultado['ok']:
        errores = resultado['error'].get('errors', [])
        mensaje_error = errores[0].get('description', 'No se pudo actualizar el plato') if errores else 'No se pudo actualizar el plato'
        flash(mensaje_error, 'error')  
        return redirect(url_for('pagina_admin')) 

    flash('Plato actualizado exitosamente', 'success')
    return redirect(url_for('pagina_menu'))


@app.route('/admin/menu/eliminar', methods=['POST'])
def eliminar_objeto():
    nombre = request.form.get('nombre')
    resultado = eliminar_plato(nombre)  
    if not resultado['ok']:
        errores = resultado['error'].get('errors', [])
        mensaje = errores[0].get('description', 'No se pudo eliminar el plato') if errores else 'No se pudo eliminar el plato'
        flash(mensaje, 'error')
        return redirect(url_for('pagina_admin'))

    flash('Plato eliminado exitosamente', 'success')
    return redirect(url_for('pagina_menu'))

@app.route('/admin/reservas/agregar', methods=['POST'])
def agregar_reserva():

    if request.method == 'POST':
        data = request.form.to_dict()
        #Hago posible que servicios extras tenga como valor una lista.
        data['servicios_extras'] = request.form.getlist('servicios_extras')

        response = enviar_reserva(data)

        if response.get("ok"):
            flash("¡Reserva confirmada! Nos vemos pronto en Le Maison Gourmet.", "success")
            return redirect(url_for("pagina_admin"))



    if response is None:
        return redirect(url_for('pagina_admin'))  
    
    if response.status_code == 204:
        return redirect(url_for('pagina_admin'))  
    
    elif response.status_code == 404:
        return redirect(url_for('pagina_admin'))


@app.route('/admin/dashboard')
def pagina_dashboard():
    fecha_inicio = request.args.get('fecha_inicio', '2026-05-01')
    fecha_fin = request.args.get('fecha_fin', '2026-05-31')
    page = request.args.get('page', 1, type=int)  

    filtros = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "page": page, "per_page": 10}

    resultado = obtener_estadisticas(filtros)

    if resultado.get("ok"):
        datos_reales = resultado.get("data", {})
        
        total_paginas = datos_reales.get("total_paginas", 1)
        
        return render_template('dashboard.html', data=datos_reales, f_inicio=fecha_inicio, f_fin=fecha_fin,page=page, total_paginas=total_paginas)
    
    for error in resultado.get("errores", []):
        flash(error, "error")

    return render_template('dashboard.html', data=None, f_inicio=fecha_inicio, f_fin=fecha_fin, page=1, total_paginas=1)

@app.route('/resenas', methods=['GET', 'POST'])
def pagina_resenas():
    origen = request.form.get('origen', url_for('pagina_resenas'))
    if request.method == 'POST':
        usuario = session.get('usuario')
        token = session.get('token')

        if not usuario or not token:
            flash('Tenés que iniciar sesión para dejar una reseña.', 'error')
            return redirect(url_for('iniciar_sesion'))

        resultado = enviar_resena(
            id_usuario=usuario['id'],
            id_reserva=None,
            id_plato=request.form.get('id_plato'), 
            puntuacion=int(request.form.get('puntuacion')),
            comentario=request.form.get('comentario'),
            token=token
        )

        if resultado.get('ok'):
            flash('¡Reseña enviada!', 'success')
        else:
            for e in resultado.get('errores', []):
                flash(e, 'error')

        return redirect(origen)

    # GET
    resultado = obtener_resenas()
    if resultado.get('ok'):
        return render_template('reseñas.html', resenas=resultado['response'])
    for e in resultado.get('errores', []):
        flash(e, 'error')
    return render_template('reseñas.html', resenas=[])

@app.route('/resenas/eliminar/<int:id_resena>', methods=['POST'])
def eliminar_resena_view(id_resena):
    origen = request.form.get('origen', url_for('pagina_resenas'))
    usuario = session.get('usuario')
    token = session.get('token')

    if not usuario or usuario.get('rol') != 'admin':
        flash('No tenés permisos para esto.', 'error')
        return redirect(url_for('pagina_resenas'))

    resultado = eliminar_resena(id_resena, token)

    if resultado.get('ok'):
        flash('Reseña eliminada.', 'success')
    else:
        for e in resultado.get('errores', []):
            flash(e, 'error')

    return redirect(origen)


@app.route('/admin/reservas/eliminar', methods=['POST'])
def eliminar_reserva_admin():
    if request.method == 'POST':
        data = request.form.to_dict()

        response = eliminar_reserva(data)

        if response.get("ok"):
            flash("Reserva eliminada con éxito.", "success")
        else:
            errores = response.get("errores", ["Error desconocido al eliminar."])
            for error in errores:
                flash(error, "error")

        return redirect(url_for('pagina_admin'))
    
@app.route('/admin/usuarios/actualizar_rol', methods=['POST'])
def actualizar_rol():
    id_usuario = request.form.get('id_usuario')

    resultado = actualizar_rol_usuario(int(id_usuario))

    if resultado:
        flash('Rol actualizado correctamente', 'success')
    else:
        flash('No se pudo actualizar el rol', 'error')

    return redirect(url_for('pagina_usuarios'))
    
if __name__ == "__main__":
       app.run(debug=True,port = 5001)
