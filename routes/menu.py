from flask import Flask, Blueprint, render_template, request, redirect, url_for,flash, session, current_app
from services.menu import obtener_menu,crear_plato,eliminar_plato,actualizar_plato
from werkzeug.utils import secure_filename
import os

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu')
def pagina_menu():
    data = obtener_menu()
    platos = data.get('platos', [])
    return render_template('menu.html', platos=platos)

@menu_bp.route('/admin/menu', methods=['POST'])
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
        archivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
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
    return redirect(url_for('menu.pagina_menu'))

@menu_bp.route('/admin/menu/modificar', methods=['POST'])
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
    return redirect(url_for('menu.pagina_menu'))


@menu_bp.route('/admin/menu/eliminar', methods=['POST'])
def eliminar_objeto():
    nombre = request.form.get('nombre')
    resultado = eliminar_plato(nombre)  
    if not resultado['ok']:
        errores = resultado['error'].get('errors', [])
        mensaje = errores[0].get('description', 'No se pudo eliminar el plato') if errores else 'No se pudo eliminar el plato'
        flash(mensaje, 'error')
        return redirect(url_for('pagina_admin'))

    flash('Plato eliminado exitosamente', 'success')
    return redirect(url_for('menu.pagina_menu'))