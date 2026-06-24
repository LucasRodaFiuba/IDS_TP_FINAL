from flask import Flask, render_template
import os
from routes.servicios_extra import servicios_extra_bp
from routes.dashboard import dashboard_bp
from routes.usuarios import usuarios_bp
from routes.auth import auth_bp
from routes.reservas import reservas_bp
from routes.menu import menu_bp
from routes.mis_reservas import mis_reservas_bp
from routes.resenas import resenas_bp
from services.servicios_extra import obtener_servicios_extra

app = Flask(__name__) 
# Carpeta donde se guardan las imágenes
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img')
app.secret_key = "dev-secret-key-123"

app.register_blueprint(servicios_extra_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(menu_bp)
app.register_blueprint(mis_reservas_bp)
app.register_blueprint(resenas_bp)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/admin')
def pagina_admin():
    servicios_extra = obtener_servicios_extra()
    return render_template('admin.html', servicios_extra=servicios_extra)
    
if __name__ == "__main__":
       app.run(debug=True,port = 5001)
