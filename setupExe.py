import os
import subprocess
import sys

def build_executable():
    # Vérifie si PyInstaller est installé, sinon l'installe
    try:
        import PyInstaller
    except ImportError:
        print("Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Commande pour créer l'exécutable
    command = [
        "pyinstaller",
        "--onefile",          # Crée un seul fichier exécutable
        "--windowed",         # Empêche l'ouverture d'une console
        "--add-data", "settings.py;.",  # Ajoute settings.py
        "main.py"             # Point d'entrée du jeu
    ]

    # Exécute la commande
    print("Génération de l'exécutable...")
    subprocess.run([sys.executable, "-m", "PyInstaller"] + command[1:], shell=True)

    # Affiche l'emplacement du fichier final
    exe_path = os.path.join("dist", "LunarLander.exe")
    if os.path.exists(exe_path):
        print(f"Exécutable créé avec succès : {exe_path}")
    else:
        print("Une erreur s'est produite lors de la création de l'exécutable.")

if __name__ == "__main__":
    build_executable()
