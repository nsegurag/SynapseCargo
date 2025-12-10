import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, 
    QGroupBox, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt
from src.utils import get_user_data_dir, APP_VERSION
from src.logic.updater import check_for_updates

# --- ESTILOS DIRECTOS ---
BTN_BLUE = """
    QPushButton {
        background-color: #0067C0; color: white; border: none; border-radius: 5px;
        font-weight: bold; padding: 8px 15px; font-size: 14px;
    }
    QPushButton:hover { background-color: #0056a3; }
"""

BTN_RED = """
    QPushButton {
        background-color: #D32F2F; color: white; border: none; border-radius: 5px;
        font-weight: bold; padding: 8px 15px; font-size: 14px;
    }
    QPushButton:hover { background-color: #C62828; }
"""

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        title = QLabel("Configuración del Sistema")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        main_layout.addWidget(title)

        # --- SECCIÓN 1: ALMACENAMIENTO ---
        gb_storage = QGroupBox("💾 Almacenamiento y Caché")
        gb_storage.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; border: 1px solid #DDD; border-radius: 8px; 
                margin-top: 10px; padding-top: 15px; background: white;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #555; }
        """)
        layout_storage = QVBoxLayout(gb_storage)
        layout_storage.setContentsMargins(20, 20, 20, 20)

        lbl_cache_info = QLabel("El sistema guarda imágenes temporales de los códigos de barras generados.\nPuedes borrarlas para liberar espacio en disco.")
        lbl_cache_info.setStyleSheet("color: #666; font-size: 13px;")
        
        btn_clear_cache = QPushButton("🗑️  Borrar Archivos Temporales")
        btn_clear_cache.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear_cache.setStyleSheet(BTN_RED)
        btn_clear_cache.setFixedWidth(250)
        btn_clear_cache.clicked.connect(self.clear_cache_action)

        layout_storage.addWidget(lbl_cache_info)
        layout_storage.addSpacing(10)
        layout_storage.addWidget(btn_clear_cache)
        main_layout.addWidget(gb_storage)

        # --- SECCIÓN 2: ACTUALIZACIONES ---
        gb_update = QGroupBox("🔄 Actualizaciones de Software")
        gb_update.setStyleSheet(gb_storage.styleSheet())
        layout_update = QVBoxLayout(gb_update)
        layout_update.setContentsMargins(20, 20, 20, 20)

        lbl_version = QLabel(f"Versión Actual Instalada: <b>v{APP_VERSION}</b>")
        lbl_version.setStyleSheet("font-size: 14px; color: #333;")

        btn_check_update = QPushButton("☁️  Buscar Actualizaciones Ahora")
        btn_check_update.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_check_update.setStyleSheet(BTN_BLUE)
        btn_check_update.setFixedWidth(250)
        btn_check_update.clicked.connect(self.check_updates_action)

        layout_update.addWidget(lbl_version)
        layout_update.addSpacing(10)
        layout_update.addWidget(btn_check_update)
        main_layout.addWidget(gb_update)

        # --- SECCIÓN 3: ACERCA DE ---
        gb_about = QGroupBox("ℹ️ Acerca de SynapseCargo")
        gb_about.setStyleSheet(gb_storage.styleSheet())
        layout_about = QVBoxLayout(gb_about)
        
        lbl_about = QLabel("Desarrollado por: <b>NSLabs</b>\nSoporte: nestor@synapsecargo.com\nLicencia: Enterprise Edition")
        lbl_about.setStyleSheet("color: #555; line-height: 1.5;")
        layout_about.addWidget(lbl_about)
        main_layout.addWidget(gb_about)

        main_layout.addStretch()

    def clear_cache_action(self):
        cache_path = os.path.join(get_user_data_dir(), "barcodes")
        if not os.path.exists(cache_path):
            QMessageBox.information(self, "Limpio", "La caché ya está vacía.")
            return

        reply = QMessageBox.question(self, "Confirmar", "¿Estás seguro de borrar todas las imágenes temporales?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(cache_path)
                os.makedirs(cache_path) # La recreamos vacía
                QMessageBox.information(self, "Éxito", "Caché eliminada correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo borrar la caché:\n{e}")

    def check_updates_action(self):
        # Llamamos a la lógica que ya creamos, pero sin modo silencioso para que avise si no hay nada
        check_for_updates(self, silent=False)