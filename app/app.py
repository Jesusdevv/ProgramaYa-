import os
import sys

# Esto obliga a Python a buscar carpetas ('routes', 'static', etc.) en el directorio actual
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, redirect
from routes.auth import auth_bp
from routes.cursos import cursos_bp
from routes.admin import admin_bp
from routes.perfil import perfil_bp
from routes.ejercicios import ejercicios_bp


app = Flask(__name__, template_folder='../Front', static_folder='../static')
app.config.from_object('config.config.Config')

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cursos_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(ejercicios_bp)


@app.route('/')
def index():
    return render_template('pagina_inicio_sinsesion.html')

@app.route('/perfil')
def perfil_redirect():
    return redirect('/ver-cursos')

# --- Rutas a páginas frontend ---
@app.route('/inicio-sesion')
def inicio_sesion():
    return render_template('inicio_sesion.html')

@app.route('/registro')
def registro():
    return render_template('registro_usuario.html')

@app.route('/perfil-profesor')
def perfil_profesor():
    return render_template('perfil_profesor.html')

@app.route('/perfil-estudiante')
def perfil_estudiante():
    return render_template('perfil_estudiante.html')

@app.route('/ver-cursos')
def ver_cursos():
    return render_template('ver_cursos.html')

@app.route('/curso-js')
def curso_js():
    return render_template('curso_js.html')

@app.route('/curso-python')
def curso_python():
    return render_template('curso_python.html')

@app.route('/crear-curso')
def crear_curso():
    return render_template('crear_curso.html')

@app.route('/dashboard-admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')

@app.route('/pagina-inicio-sinsesion')
def pagina_inicio_sinsesion():
    return render_template('pagina_inicio_sinsesion.html')

@app.route('/pagina-inicio-sesion-est')
def pagina_inicio_sesion_est():
    return render_template('pagina_inicio_sesion_est.html')

@app.route('/pagina-inicio-sesion-prof')
def pagina_inicio_sesion_prof():
    return render_template('pagina_inicio_sesion_prof.html')

@app.route('/cambiar-contrasena')
def cambiar_contrasena():
    return render_template('cambiar_contraseña.html')

@app.route('/crear-capitulo')
def crear_capitulo():
    return render_template('crear_capitulo.html')

@app.route('/capitulo')
def capitulo():
    return render_template('capitulo.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)