from flask import Flask, Blueprint, render_template, request, redirect, url_for,flash, session
from services.usuarios import obtener_usuarios,actualizar_rol_usuario, crear_usuario, actualizar_usuario
from services.auth import eliminar_usuario_api

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/admin/usuarios')
def pagina_usuarios():
    data = obtener_usuarios()
    usuarios = data.get('usuarios', [])
    return render_template('usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/admin/agregar_usuario', methods=['POST'])
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
    return redirect(url_for('usuarios.pagina_usuarios'))

@usuarios_bp.route('/admin/usuarios/modificar', methods=['POST'])
def modificar_usuario():
    id_usuario = request.form.get('id')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    email = request.form.get('email')
    telefono = request.form.get('telefono')

    resultado = actualizar_usuario(int(id_usuario), nombre, apellido, email, telefono)

    if resultado:
        flash('Usuario actualizado correctamente', 'success')
    else:
        flash('No se pudo actualizar el usuario', 'error')

    return redirect(url_for('usuarios.pagina_usuarios'))

@usuarios_bp.route('/admin/usuarios/eliminar/<int:id_usuario>', methods=['POST'])
def eliminar_usuario(id_usuario):
    usuario = session.get('usuario')
    token = session.get('token')

    if not usuario or usuario.get('rol') != 'admin':
        flash('No tenés permisos para esto.', 'error')
        return redirect(url_for('usuarios.pagina_usuarios'))

    resultado = eliminar_usuario_api(id_usuario, token)

    if resultado.get('ok'):
        flash('Usuario eliminado.', 'success')
    else:
        for e in resultado.get('errores', []):
            flash(e, 'error')
    usuario = session.get('usuario')
    token = session.get('token')
    return redirect(url_for('usuarios.pagina_usuarios'))

@usuarios_bp.route('/admin/usuarios/actualizar_rol', methods=['POST'])
def actualizar_rol():
    id_usuario = request.form.get('id_usuario')

    resultado = actualizar_rol_usuario(int(id_usuario))

    if resultado:
        flash('No se pudo actualizar el rol', 'error')
    else:
        flash('Rol actualizado correctamente', 'success')

    return redirect(url_for('usuarios.pagina_usuarios'))