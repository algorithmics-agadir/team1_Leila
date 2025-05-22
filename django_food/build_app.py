import os
import sys
import subprocess
import shutil

def build_app():
    print("Préparation de la création de l'application FoodFlex...")
    
    # Vérifier que PyInstaller est installé
    try:
        import PyInstaller
    except ImportError:
        print("Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Vérifier que les autres dépendances sont installées
    print("Installation des dépendances...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Créer le dossier de build s'il n'existe pas
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # Préparation du fichier spec pour PyInstaller
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('foodproject', 'foodproject'),
]

a = Analysis(
    ['app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'django',
        'django.middleware',
        'django.template.defaulttags',
        'django.template.loader_tags',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'foodproject',
        'foodproject.foodapp',
        'webview',
        'socket',
        'threading',
        'time',
        'subprocess',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FoodFlex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='foodproject/static/foodapp/img/favicon.ico',
)
"""
    
    # Écrire le fichier spec
    with open("FoodFlex.spec", "w") as f:
        f.write(spec_content)
    
    # Exécuter PyInstaller pour créer une application autonome
    print("Construction de l'application avec PyInstaller...")
    subprocess.check_call([
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "FoodFlex.spec"
    ])
    
    # Créer un fichier README pour l'installation
    readme_content = """# FoodFlex - Application Autonome

## Instructions d'installation

1. Téléchargez et décompressez le fichier zip.
2. Exécutez simplement "FoodFlex.exe" pour lancer l'application.
3. Aucune installation de Python ou d'autres dépendances n'est requise.

## Support

En cas de problème, veuillez contacter l'équipe de support.
"""

    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("L'application a été construite avec succès!")
    print("Vous pouvez trouver l'application dans le fichier dist/FoodFlex.exe")
    print("Partagez le fichier exe avec vos utilisateurs, ils n'auront pas besoin d'installer Python.")

if __name__ == "__main__":
    build_app() 