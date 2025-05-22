import os
import sys
import threading
import time
import subprocess
import webview
import socket

# Vérifier si le port est disponible
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

# Fonction pour démarrer le serveur Django en arrière-plan
def start_django_server():
    # Attendre que le port soit disponible
    port = 8000
    while not is_port_available(port):
        port += 1
    
    # Définir l'environnement pour fonctionner sans navigateur
    os.environ['DJANGO_SETTINGS_MODULE'] = 'foodproject.settings'
    
    # Chemin vers le répertoire du projet Django
    django_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'foodproject')
    
    # Démarrer le serveur Django avec le port sélectionné
    cmd = [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{port}']
    
    # Lancer le processus
    process = subprocess.Popen(
        cmd,
        cwd=django_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW  # Cache la fenêtre de console sous Windows
    )
    
    return process, port

def create_window(url, title="FoodFlex - Cuisine Marocaine"):
    # Créer la fenêtre principale avec les contrôles natifs de Windows
    window = webview.create_window(
        title, 
        url, 
        width=1200, 
        height=800,
        frameless=False,         # Utiliser le cadre système natif avec boutons de contrôle
        easy_drag=False,         # Désactiver le drag personnalisé
        fullscreen=False,
        min_size=(800, 600),     # Taille minimale de la fenêtre
        confirm_close=False      # Ne pas demander confirmation à la fermeture
    )
    return window

if __name__ == '__main__':
    # Afficher un écran de démarrage pendant le chargement
    splash_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background-color: #141414;
                color: white;
                font-family: 'Poppins', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                overflow: hidden;
            }
            .splash-container {
                text-align: center;
            }
            .logo {
                font-size: 42px;
                font-weight: 700;
                color: #ff6b6b;
                margin-bottom: 20px;
            }
            .tagline {
                font-size: 18px;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 30px;
            }
            .loading {
                display: inline-block;
                position: relative;
                width: 80px;
                height: 80px;
            }
            .loading div {
                position: absolute;
                top: 33px;
                width: 13px;
                height: 13px;
                border-radius: 50%;
                background: #ff6b6b;
                animation-timing-function: cubic-bezier(0, 1, 1, 0);
            }
            .loading div:nth-child(1) {
                left: 8px;
                animation: loading1 0.6s infinite;
            }
            .loading div:nth-child(2) {
                left: 8px;
                animation: loading2 0.6s infinite;
            }
            .loading div:nth-child(3) {
                left: 32px;
                animation: loading2 0.6s infinite;
            }
            .loading div:nth-child(4) {
                left: 56px;
                animation: loading3 0.6s infinite;
            }
            @keyframes loading1 {
                0% { transform: scale(0); }
                100% { transform: scale(1); }
            }
            @keyframes loading2 {
                0% { transform: translate(0, 0); }
                100% { transform: translate(24px, 0); }
            }
            @keyframes loading3 {
                0% { transform: scale(1); }
                100% { transform: scale(0); }
            }
        </style>
    </head>
    <body>
        <div class="splash-container">
            <div class="logo">FoodFlex</div>
            <div class="tagline">Cuisine Marocaine Authentique</div>
            <div class="loading"><div></div><div></div><div></div><div></div></div>
        </div>
    </body>
    </html>
    """
    
    # Créer d'abord une fenêtre avec le splash screen, avec cadre natif
    splash_window = webview.create_window('FoodFlex - Démarrage', html=splash_html, width=600, height=400, resizable=False, frameless=False)
    
    # Variable pour stocker la fenêtre principale
    main_window = None
    
    def on_loaded():
        # Cette fonction est appelée une fois que la fenêtre de splash est chargée
        def startup():
            global main_window
            
            # Démarrer le serveur Django
            process, port = start_django_server()
            
            # Attendre que le serveur soit prêt (5 secondes)
            time.sleep(5)
            
            url = f"http://127.0.0.1:{port}/accueil/"
            
            # Créer la fenêtre principale avec les contrôles natifs
            main_window = create_window(url)
            
            # Fermer la fenêtre de splash après un court délai
            def close_splash():
                splash_window.destroy()
            
            threading.Timer(1.5, close_splash).start()
        
        # Démarrer le processus de démarrage dans un thread séparé
        threading.Thread(target=startup).start()
    
    # Définir le rappel lorsque la fenêtre de splash est chargée
    splash_window.events.loaded += on_loaded
    
    # Démarrer l'application avec l'interface système native
    webview.start(debug=False, gui='system') 