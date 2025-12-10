from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QColor

# --- Importamos las Vistas ---
from src.ui.home_page import HomePage
from src.ui.mawb_manager import MAWBManager
# Importamos la vista del generador con su nuevo nombre
from src.ui.label_generator import LabelGeneratorWidget as LabelGenView

class SidebarButton(QPushButton):
    """Botón personalizado para la barra lateral - Estilo Azul Clásico"""
    def __init__(self, text, icon_char, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIconSize(QSize(24, 24))
        
        # Espaciado para el icono y texto
        self.setText(f"  {icon_char}   {text}")
        
        # --- AQUÍ ESTÁ EL CAMBIO DE COLOR ---
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 20px;
                border: none;
                border-radius: 8px;
                color: #333333;          /* Texto oscuro normal */
                font-size: 14px;
                font-weight: 500;
                background-color: transparent; /* Fondo transparente normal */
            }
            QPushButton:hover {
                background-color: #E3F2FD; /* Azul muy clarito al pasar el mouse */
                color: #0067C0;            /* Texto azul al pasar el mouse */
            }
            QPushButton:checked {
                background-color: #0067C0; /* <--- ¡AZUL SÓLIDO CUANDO SE SELECCIONA! */
                color: white;              /* <--- Texto BLANCO para contraste */
                font-weight: bold;
            }
        """)
        self.setCheckable(True)
        self.setAutoExclusive(True)

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"SynapseCargo - {self.username}") # Título con usuario
        self.resize(1280, 800)
        self.setStyleSheet("background-color: #F5F7FA;") # Fondo general un poco más gris

        # --- LAYOUT PRINCIPAL (Horizontal: Sidebar | Contenido) ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ================= BARRA LATERAL (SIDEBAR) =================
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        # Sombra sutil en el borde derecho
        self.sidebar.setStyleSheet("""
            background-color: white;
            border-right: 1px solid #E0E0E0;
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(10)

        # Logo / Título
        lbl_logo = QLabel("SynapseCargo")
        # Azul corporativo más fuerte
        lbl_logo.setStyleSheet("font-size: 24px; font-weight: 900; color: #0056a3; padding-left: 10px;")
        sidebar_layout.addWidget(lbl_logo)
        sidebar_layout.addSpacing(30)

        # Botones del Menú
        self.btn_home = SidebarButton("Inicio", "🏠")
        self.btn_ops = SidebarButton("Operaciones", "🏷️")
        self.btn_inv = SidebarButton("Inventario", "📦")
        self.btn_profile = SidebarButton("Perfil", "👤")
        self.btn_settings = SidebarButton("Configuración", "⚙️")
        
        # Conectar botones
        self.btn_home.clicked.connect(lambda: self.switch_page(0))
        self.btn_ops.clicked.connect(lambda: self.switch_page(1))
        self.btn_inv.clicked.connect(lambda: self.switch_page(2))
        self.btn_profile.clicked.connect(lambda: self.switch_page(3))
        self.btn_settings.clicked.connect(lambda: self.switch_page(4))

        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_ops)
        sidebar_layout.addWidget(self.btn_inv)
        sidebar_layout.addWidget(self.btn_profile)
        sidebar_layout.addWidget(self.btn_settings)
        
        sidebar_layout.addStretch()

        # Botón Logout (Estilo Rojo específico)
        self.btn_logout = SidebarButton("Cerrar Sesión", "🚪")
        # Sobreescribimos el estilo SOLO para este botón para que sea rojo
        self.btn_logout.setStyleSheet("""
            QPushButton {
                text-align: left; padding-left: 20px; border: none; border-radius: 8px;
                color: #D32F2F; font-size: 14px; font-weight: 500; background-color: transparent;
            }
            QPushButton:hover { background-color: #FFEBEE; color: #C62828; }
            QPushButton:checked { background-color: #D32F2F; color: white; font-weight: bold; }
        """)
        self.btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.btn_logout)

        # ================= CONTENIDO (STACKED) =================
        self.content_area = QStackedWidget()
        # Fondo limpio para el contenido
        self.content_area.setStyleSheet("background-color: #FFFFFF; border-top-left-radius: 15px;")

        # Página 0: Inicio
        self.page_home = HomePage(self.username)
        self.content_area.addWidget(self.page_home)

        # Página 1: Generador (Tu viejo main)
        self.page_ops = LabelGenView(self.username) 
        self.content_area.addWidget(self.page_ops)

        # Página 2: Inventario (MAWB Manager)
        self.page_inv = MAWBManager(self.username)
        self.content_area.addWidget(self.page_inv)

        # Página 3: Perfil (Placeholder)
        self.page_profile = QLabel("👤 Módulo de Perfil")
        self.page_profile.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_profile.setStyleSheet("font-size: 24px; color: #CCC; font-weight: bold;")
        self.content_area.addWidget(self.page_profile)

        # Página 4: Configuración (Placeholder)
        self.page_settings = QLabel("⚙️ Configuración del Sistema")
        self.page_settings.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_settings.setStyleSheet("font-size: 24px; color: #CCC; font-weight: bold;")
        self.content_area.addWidget(self.page_settings)

        # Ensamblar con un pequeño margen para que se vea el fondo gris
        container_content = QWidget()
        layout_content = QVBoxLayout(container_content)
        layout_content.setContentsMargins(10, 10, 0, 0) # Margen superior e izquierdo
        layout_content.addWidget(self.content_area)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(container_content)

        # Seleccionar inicio por defecto
        self.btn_home.click()

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)
        # Recargar datos si vamos a Inventario
        if index == 2:
            self.page_inv.load_data()
        # Podrías añadir un refresh para HomePage (index 0) si fuera necesario

    def logout(self):
        from src.ui.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()