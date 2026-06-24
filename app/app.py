from flask import Flask
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.cursos import cursos_bp

app = Flask(__name__)
app.config.from_object('config.config.Config')

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cursos_bp)

@app.route('/')
def index():
    return "ProgramaYA prueba de flask"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)