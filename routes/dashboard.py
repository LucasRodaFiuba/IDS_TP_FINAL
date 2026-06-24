from flask import Flask, Blueprint,redirect,url_for,request,render_template, flash
from services.dashboard import obtener_estadisticas

dashboard_bp= Blueprint('dashboard',__name__)

@dashboard_bp.route('/admin/dashboard')
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