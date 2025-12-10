import sys
import os
import requests
import subprocess
import tempfile
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
from src.utils import CURRENT_VERSION, VERSION_URL, GITHUB_REPO_API

def check_for_updates(parent=None, silent=False):
    """
    Verifica si hay una nueva versión y gestiona la descarga/instalación.
    """
    print("🔍 Buscando actualizaciones...")
    
    try:
        # 1. Consultar el archivo version.txt
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code != 200:
            if not silent: print("⚠️ No se pudo leer version.txt")
            return

        latest_version = response.text.strip()
        
        print(f"Versión Local: {CURRENT_VERSION} | Remota: {latest_version}")

        # Si las versiones son iguales, no hacemos nada
        if latest_version == CURRENT_VERSION:
            if not silent: print("✅ El sistema está actualizado.")
            return

        # 2. ¡HAY NUEVA VERSIÓN! Preguntar al usuario
        reply = QMessageBox.question(
            parent, 
            "Actualización Disponible", 
            f"Hay una nueva versión disponible ({latest_version}).\n\n"
            "¿Deseas descargarla e instalarla automáticamente ahora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            download_and_install(parent)

    except Exception as e:
        print(f"❌ Error buscando actualizaciones: {e}")

def download_and_install(parent):
    """
    Descarga el instalador desde GitHub Releases y lo ejecuta.
    """
    try:
        # 1. Obtener la URL del .exe desde la API de GitHub
        print("🔗 Consultando API de GitHub...")
        api_response = requests.get(GITHUB_REPO_API, timeout=10)
        api_data = api_response.json()
        
        exe_url = None
        exe_name = "Setup_Update.exe"

        # Buscar en los "assets" el archivo que termine en .exe
        if "assets" in api_data:
            for asset in api_data["assets"]:
                if asset["name"].endswith(".exe"):
                    exe_url = asset["browser_download_url"]
                    exe_name = asset["name"]
                    break
        
        if not exe_url:
            QMessageBox.warning(parent, "Error", "No se encontró el archivo instalador en la Release de GitHub.")
            return

        # 2. Descargar el archivo con barra de progreso
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, exe_name)
        
        progress = QProgressDialog("Descargando actualización...", "Cancelar", 0, 100, parent)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Descargando SynapseCargo")
        progress.show()

        print(f"⬇️ Descargando de: {exe_url}")
        
        with requests.get(exe_url, stream=True) as r:
            r.raise_for_status()
            total_length = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(installer_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if progress.wasCanceled():
                        return # Cancelar descarga
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_length > 0:
                            percent = int((downloaded / total_length) * 100)
                            progress.setValue(percent)

        progress.setValue(100)
        
        # 3. Ejecutar el instalador y cerrar la app
        print("🚀 Ejecutando instalador...")
        subprocess.Popen([installer_path, "/SILENT"]) # /SILENT intenta instalar sin molestar tanto
        sys.exit(0) # Cerramos SynapseCargo para que el instalador pueda sobrescribir archivos

    except Exception as e:
        QMessageBox.critical(parent, "Error de Actualización", f"Ocurrió un error al actualizar:\n{e}")