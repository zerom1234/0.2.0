from app import create_app

# Créez l'application Flask avec la configuration pour l'environnement de développement
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True)