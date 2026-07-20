"""
Migra contraseñas en texto plano a hashed (werkzeug).
Ejecutar UNA SOLA VEZ si ya tenías usuarios registrados antes del hashing.
Uso: python scripts/migrate_passwords.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from werkzeug.security import generate_password_hash
from database import ejecutar_consulta

app = Flask(__name__)
app.config.from_object('config.config.Config')

with app.app_context():
    usuarios = ejecutar_consulta(
        "SELECT id_user, password FROM users;", es_select=True
    )
    if not usuarios:
        print("No hay usuarios en la DB.")
        sys.exit(0)

    # Formatos de hash de werkzeug: scrypt:..., pbkdf2:..., $2..., $scrypt$...
    def es_hash_valido(pwd):
        return (len(pwd) > 30 and (
            pwd.startswith('scrypt:') or
            pwd.startswith('pbkdf2:') or
            pwd.startswith('$')
        ))

    contador = 0
    for u in usuarios:
        pwd = u['password']
        if es_hash_valido(pwd):
            continue
        hashed = generate_password_hash(pwd)
        ok = ejecutar_consulta(
            "UPDATE users SET password = %s WHERE id_user = %s;",
            (hashed, u['id_user']), es_select=False
        )
        if ok:
            contador += 1
            print(f"  [OK] Usuario {u['id_user']} migrado")

    print(f"\n{contador} contraseñas migradas. El resto ya estaban hasheadas.")
