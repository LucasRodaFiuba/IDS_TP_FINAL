from flask import Flask, Blueprint,redirect,url_for,request,render_template, flash, session
from services.auth import (
    eliminar_usuario_api,
    iniciar_sesion_api,
    obtener_perfil_usuario_api,
    registrar_usuario_api,
    solicitar_recuperacion_password_api,
)


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/iniciar_sesion', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.perfil'))

        for error in resultado.get('errores', []):
            flash(error, 'error')

    return render_template('iniciar_sesion.html')
    
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        resultado = registrar_usuario_api(request.form.to_dict())

        if resultado.get('ok'):
            flash('Cuenta creada correctamente. Ya podes iniciar sesion.', 'success')
            return redirect(url_for('auth.iniciar_sesion'))

        for error in resultado.get('errores', []):
            flash(error, 'error')

    return render_template('registro.html')


@auth_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        email = request.form.get('email', '')
        resultado = solicitar_recuperacion_password_api(email)

        if resultado.get('ok'):
            flash('Solicitud de recuperacion enviada.', 'success')
            return redirect(url_for('auth.iniciar_sesion'))

        for error in resultado.get('errores', []):
            flash(error, 'error')

    return render_template('recuperar_contrasena.html')


@auth_bp.route('/perfil')
def perfil():
    usuario_sesion = session.get('usuario')
    token = session.get('token')

    if not usuario_sesion or not token:
        flash('Tenes que iniciar sesion primero.', 'login_error')
        return redirect(url_for('auth.iniciar_sesion'))

    usuario_id = usuario_sesion.get('id')
    resultado = obtener_perfil_usuario_api(usuario_id, token)

    if not resultado.get('ok'):
        for error in resultado.get('errores', []):
            flash(error, 'login_error')
        return redirect(url_for('auth.iniciar_sesion'))

    data = resultado.get('data', {})
    return render_template(
        'perfil.html',
        usuario=data.get('usuario', usuario_sesion),
        reservas=data.get('reservas', [])
    )

@auth_bp.route('/cerrar_sesion', methods=['POST'])
def cerrar_sesion():
    session.clear()
    flash('Sesion cerrada correctamente.', 'success')
    return redirect(url_for('auth.iniciar_sesion'))


@auth_bp.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    usuario_sesion = session.get('usuario')
    token = session.get('token')

    if not usuario_sesion or not token:
        flash('Tenes que iniciar sesion primero.', 'login_error')
        return redirect(url_for('auth.iniciar_sesion'))

    resultado = eliminar_usuario_api(usuario_sesion.get('id'), token)

    if resultado.get('ok'):
        session.clear()
        flash('Cuenta eliminada correctamente.', 'success')
        return redirect(url_for('home'))

    for error in resultado.get('errores', []):
        flash(error, 'login_error')

    return redirect(url_for('auth.perfil'))
