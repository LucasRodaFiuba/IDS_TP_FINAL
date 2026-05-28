import sys
import os
from flask import Flask
from .constantes import BASE_URL
#agregar importaciones para los blueprints u otras cosas importantes
from .routes.reservas import reservas_bp
from .routes.servicios import servicios_extra_bp
from .routes.auth import auth_bp
from .routes.usuarios import usuarios_bp
from .routes.menu import menu_bp



# Buscar módulos en la carpeta donde esté app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import registrar_rutas

app = Flask(__name__)
app.json.sort_keys = False  #no ordena alfabaticamente 

# Registrar los endpoints distribuidos en la carpeta routes
registrar_rutas(app)
#agregar blueprints
app.register_blueprint(reservas_bp, url_prefix=BASE_URL)
app.register_blueprint(servicios_extra_bp)
app.register_blueprint(auth_bp, url_prefix=BASE_URL)
app.register_blueprint(usuarios_bp, url_prefix=BASE_URL)
app.register_blueprint(menu_bp, url_prefix=BASE_URL)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
