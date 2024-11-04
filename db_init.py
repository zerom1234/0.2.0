from app import create_app
from app.db import db

# Crée l'application Flask avec la configuration de développement
app = create_app('development')

# Crée la base de données et les tables
with app.app_context():
    db.create_all()
    print("Base de données créée avec succès.")