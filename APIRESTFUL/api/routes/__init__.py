from api.routes.dashboard import dashboard_bp

def registrar_rutas(app):
    """Registra todos los Blueprints de la API en la instancia de Flask."""
    app.register_blueprint(dashboard_bp)
    
    # Registrar el resto de endpoints en este archivo