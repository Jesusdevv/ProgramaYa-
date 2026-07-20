"""
Crea el primer usuario Administrador.
Uso: python scripts/seed_admin.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from werkzeug.security import generate_password_hash
from database import ejecutar_consulta

# Crear app mínima para que current_app funcione
app = Flask(__name__)
app.config.from_object('config.config.Config')

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@programaya.com'
ADMIN_PASSWORD = 'Admin123!'

with app.app_context():
    existente = ejecutar_consulta(
        "SELECT id_user FROM users WHERE role = 'Administrador';", es_select=True
    )
    if existente:
        print(f"Ya existe un administrador (ID {existente[0]['id_user']}). No se crea otro.")
        sys.exit(0)

    hashed = generate_password_hash(ADMIN_PASSWORD)
    ok = ejecutar_consulta(
        """INSERT INTO users (username, email, password, role, is_validated)
           VALUES (%s, %s, %s, 'Administrador', TRUE);""",
        (ADMIN_USERNAME, ADMIN_EMAIL, hashed), es_select=False
    )
    if ok:
        print(f"✓ Admin creado: {ADMIN_USERNAME} / {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    else:
        print("Error al crear admin.")
        sys.exit(1)
