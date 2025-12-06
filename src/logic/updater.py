import requests
import webbrowser
from PyQt6.QtWidgets import QMessageBox
from src.utils import CURRENT_VERSION, UPDATE_URL, RELEASE_URL

def check_for_updates(parent_window):
    """
    Consulta internet para ver si hay una versión nueva.
    Si la hay, muestra una alerta y ofrece ir a descargarla.
    """
    print("🔍 Buscando actualizaciones...")
    try:
        # Descargamos el archivo version.txt de internet (timeout de 3 seg para no trabar la app)
        response = requests.get(UPDATE_URL, timeout=3)
        
        if response.status_code == 200:
            # Limpiamos el texto (quitamos espacios o saltos de línea)
            latest_version = response.text.strip()
            
            # COMPARACIÓN DE VERSIONES
            # Si la versión de internet es diferente a la local...
            if latest_version != CURRENT_VERSION:
                print(f"⚠️ Nueva versión detectada: {latest_version} (Actual: {CURRENT_VERSION})")
                
                # Preguntar al usuario
                reply = QMessageBox.question(
                    parent_window, 
                    "Actualización Disponible ✨",
                    f"¡Hay una nueva versión disponible!\n\n"
                    f"Versión Actual: {CURRENT_VERSION}\n"
                    f"Nueva Versión: {latest_version}\n\n"
                    f"¿Quieres descargarla ahora?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Abrir el navegador para descargar
                    webbrowser.open(RELEASE_URL)
                    return True
            else:
                print("✅ Tienes la última versión.")
                
    except Exception as e:
        print(f"⚠️ No se pudo verificar actualizaciones: {e}")
    
    return False