# launch_offline.py
import os
import sys
import subprocess
import json
import webbrowser
import time

def check_and_install_dependencies():
    """Vérifie et installe les dépendances si nécessaire"""
    try:
        import streamlit, pandas, plotly
        print("✅ Dépendances déjà installées")
        return True
    except ImportError:
        print("📦 Installation des dépendances...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "streamlit", "pandas", "plotly", "--quiet"
            ])
            print("✅ Dépendances installées avec succès !")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'installation : {e}")
            return False

def ensure_data_files():
    """Crée les fichiers de données s'ils n'existent pas"""
    # Créer le dossier user_data s'il n'existe pas
    if not os.path.exists("user_data"):
        os.makedirs("user_data")
        print("✅ Dossier user_data créé")
    
    # Créer users.json s'il n'existe pas
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
        print("✅ Fichier users.json créé")

def launch_app():
    """Lance l'application Streamlit en mode hors ligne"""
    print("🚀 Lancement de MGA Finance Tracker (Mode Hors Ligne)...")
    print("📱 L'application va s'ouvrir dans votre navigateur")
    print("ℹ️  Si le navigateur ne s'ouvre pas, allez sur http://localhost:8503")
    print("")
    print("=" * 50)
    print("⚠️  Pour arrêter l'application, appuyez sur Ctrl+C")
    print("=" * 50)
    print("")
    
    # Ouvrir le navigateur après un court délai
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8503")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Lancer Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8503",
            "--server.address=localhost",
            "--server.headless=true",
            "--browser.serverAddress=localhost",
            "--global.developmentMode=false",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'application...")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    print("=" * 50)
    print("   MGA Finance Tracker - Mode Hors Ligne")
    print("=" * 50)
    print("")
    
    if check_and_install_dependencies():
        ensure_data_files()
        launch_app()
    else:
        print("❌ Impossible d'installer les dépendances.")
        print("Assurez-vous d'avoir Python installé.")
        input("Appuyez sur Entrée pour fermer...")