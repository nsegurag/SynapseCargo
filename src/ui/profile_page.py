from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QMessageBox, QGroupBox, QFormLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from src.utils import get_db_connection

# --- ESTILOS DIRECTOS (Para mantener la consistencia) ---
BTN_BLUE = """
    QPushButton {
        background-color: #0067C0; color: white; border: none; border-radius: 5px;
        font-weight: bold; padding: 8px 15px; font-size: 14px;
    }
    QPushButton:hover { background-color: #0056a3; }
"""

class ProfilePage(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        title = QLabel(f"Perfil de Usuario: {self.username}")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        main_layout.addWidget(title)

        # --- SECCIÓN 1: DATOS DE LA CUENTA ---
        gb_info = QGroupBox("👤 Información de la Cuenta")
        gb_info.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; border: 1px solid #DDD; border-radius: 8px; 
                margin-top: 10px; padding-top: 15px; background: white;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #0067C0; }
        """)
        layout_info = QFormLayout(gb_info)
        layout_info.setContentsMargins(20, 20, 20, 20)
        layout_info.setSpacing(15)

        # Obtenemos el rol desde la DB
        role = self.get_user_role()
        
        lbl_user = QLabel(self.username)
        lbl_user.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        
        lbl_role = QLabel(role.upper())
        lbl_role.setStyleSheet("font-size: 14px; font-weight: bold; color: #0067C0; background-color: #E3F2FD; padding: 4px 8px; border-radius: 4px;")

        layout_info.addRow("Usuario:", lbl_user)
        layout_info.addRow("Rol:", lbl_role)
        
        main_layout.addWidget(gb_info)

        # --- SECCIÓN 2: SEGURIDAD (CAMBIAR CONTRASEÑA) ---
        gb_sec = QGroupBox("🔒 Seguridad y Contraseña")
        gb_sec.setStyleSheet(gb_info.styleSheet())
        layout_sec = QVBoxLayout(gb_sec)
        layout_sec.setContentsMargins(20, 20, 20, 20)
        layout_sec.setSpacing(15)

        form_pass = QFormLayout()
        
        self.input_curr_pass = QLineEdit()
        self.input_curr_pass.setPlaceholderText("Ingresa tu contraseña actual")
        self.input_curr_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_curr_pass.setMinimumHeight(35)

        self.input_new_pass = QLineEdit()
        self.input_new_pass.setPlaceholderText("Nueva contraseña")
        self.input_new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_new_pass.setMinimumHeight(35)

        self.input_confirm_pass = QLineEdit()
        self.input_confirm_pass.setPlaceholderText("Repite la nueva contraseña")
        self.input_confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm_pass.setMinimumHeight(35)

        form_pass.addRow("Contraseña Actual:", self.input_curr_pass)
        form_pass.addRow("Nueva Contraseña:", self.input_new_pass)
        form_pass.addRow("Confirmar:", self.input_confirm_pass)
        
        layout_sec.addLayout(form_pass)

        btn_change = QPushButton("Actualizar Contraseña")
        btn_change.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_change.setStyleSheet(BTN_BLUE)
        btn_change.setFixedWidth(200)
        btn_change.clicked.connect(self.change_password)
        
        # Alineamos el botón a la derecha
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(btn_change)
        
        layout_sec.addLayout(btn_container)
        main_layout.addWidget(gb_sec)

        main_layout.addStretch()

    def get_user_role(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE username = %s", (self.username,))
            res = cur.fetchone()
            conn.close()
            return res[0] if res else "Desconocido"
        except:
            return "Error"

    def change_password(self):
        curr = self.input_curr_pass.text().strip()
        new_p = self.input_new_pass.text().strip()
        conf_p = self.input_confirm_pass.text().strip()

        if not curr or not new_p or not conf_p:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor llena todos los campos.")
            return

        if new_p != conf_p:
            QMessageBox.warning(self, "Error", "Las nuevas contraseñas no coinciden.")
            return

        if len(new_p) < 4:
            QMessageBox.warning(self, "Seguridad", "La contraseña es muy corta.")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # 1. Verificar contraseña actual
            cur.execute("SELECT id FROM users WHERE username=%s AND password=%s", (self.username, curr))
            user = cur.fetchone()
            
            if not user:
                conn.close()
                QMessageBox.critical(self, "Error", "La contraseña actual es incorrecta.")
                return

            # 2. Actualizar
            cur.execute("UPDATE users SET password=%s WHERE username=%s", (new_p, self.username))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Contraseña actualizada correctamente.")
            
            # Limpiar campos
            self.input_curr_pass.clear()
            self.input_new_pass.clear()
            self.input_confirm_pass.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error de Conexión", str(e))