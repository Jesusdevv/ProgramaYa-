import os
import sys

# Esto obliga a Python a buscar carpetas ('routes', 'static', etc.) en el directorio actual
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, redirect
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
    'perfil-profesor': 'perfil_profesor.html',
    'perfil-estudiante': 'perfil_estudiante.html',
    'ver-cursos': 'ver_cursos.html',
    'curso-js': 'curso_js.html',
    'curso-python': 'curso_python.html',
    'crear-curso': 'crear_curso.html',
    'dashboard-admin': 'dashboard_admin.html',
    'pagina-inicio-sinsesion': 'pagina_inicio_sinsesion.html',
    'pagina-inicio-sesion-est': 'pagina_inicio_sesion_est.html',
    'pagina-inicio-sesion-prof': 'pagina_inicio_sesion_prof.html',
    'cambiar-contraseña': 'cambiar_contraseña.html',
    'crear-capitulo': 'crear_capitulo.html',
    'capitulo': 'capitulo.html'
}

@app.route('/')
def index():
    return render_template('pagina_inicio_sinsesion.html')

@app.route('/perfil')
def perfil_redirect():
    role = None
    return redirect('/perfil-estudiante')

for ruta, archivo in front_pages.items():
    app.add_url_rule(f'/{ruta}', ruta.replace('-', '_'), lambda f=archivo: render_template(f))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)