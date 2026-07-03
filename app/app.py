import os
import sys

# Esto obliga a Python a buscar carpetas ('routes', 'static', etc.) en el directorio actual
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from routes.auth import auth_bp
from routes.cursos import cursos_bp
from routes.admin import admin_bp


app = Flask(__name__, template_folder='../Front', static_folder='../static')
app.config.from_object('config.config.Config')

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cursos_bp)

front_pages = {
    'inicio-sesion': 'inicio_sesion.html',
    'registro': 'registro_usuario.html',
    'perfil': 'perfil.html',
    'perfil-profesor': 'perfil_profesor.html',
    'perfil-estudiante': 'perfil_estudiante.html',
    'cursos': 'cursos.html',
    'ver-cursos': 'ver_cursos.html',
    'vercurso': 'vercurso.html',
    'curso-js': 'curso_js.html',
    'curso-python': 'curso_python.html',
    'pag_inicial_sinsesion': 'pag_inicial_sinsesion.html',
    'crear-curso': 'crear_curso.html',
    'dashboard-admin': 'dashboard_admin.html'
}

@app.route('/')
def index():
    return render_template('pag_inicial_sinsesion.html')

for ruta, archivo in front_pages.items():
    app.add_url_rule(f'/{ruta}', ruta.replace('-', '_'), lambda f=archivo: render_template(f))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)