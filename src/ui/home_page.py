from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGraphicsDropShadowEffect, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from src.utils import get_db_connection

class StatCard(QFrame):
    def __init__(self, title, value, icon, color):
        super().__init__()
        self.setFixedSize(220, 140)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 15px;
                border-left: 5px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0,30))
        shadow.setYOffset(4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(f"font-size: 30px; color: {color};")
        
        # Guardamos la referencia (self.lbl_val) para poder cambiar el texto luego
        self.lbl_val = QLabel(str(value))
        self.lbl_val.setStyleSheet("font-size: 32px; font-weight: bold; color: #333;")
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 14px; color: #777; font-weight: 500;")
        
        layout.addWidget(lbl_icon)
        layout.addWidget(self.lbl_val)
        layout.addWidget(lbl_title)

    def update_value(self, new_value):
        """Actualiza el número en la tarjeta al instante"""
        self.lbl_val.setText(str(new_value))

class HomePage(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Bienvenida
        lbl_welcome = QLabel(f"Hola, {username} 👋")
        lbl_welcome.setStyleSheet("font-size: 36px; font-weight: bold; color: #222;")
        lbl_desc = QLabel("Bienvenido a SynapseCargo. Aquí tienes el resumen de hoy.")
        lbl_desc.setStyleSheet("font-size: 16px; color: #666;")
        
        main_layout.addWidget(lbl_welcome)
        main_layout.addWidget(lbl_desc)
        main_layout.addSpacing(10)

        # Grid de Estadísticas
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Obtener datos iniciales
        total_mawb, total_labels = self.get_stats()

        # Guardamos las tarjetas en variables (self.card1...) para usarlas en refresh_stats
        self.card1 = StatCard("Guías Creadas", total_mawb, "📦", "#0067C0")
        self.card2 = StatCard("Etiquetas Generadas", total_labels, "🏷️", "#00C04B")
        self.card3 = StatCard("Alertas Pendientes", "0", "🔔", "#FF9900")

        stats_layout.addWidget(self.card1)
        stats_layout.addWidget(self.card2)
        stats_layout.addWidget(self.card3)
        
        main_layout.addLayout(stats_layout)
        main_layout.addStretch()

    def get_stats(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Contar MAWBs totales
            cur.execute("SELECT COUNT(*) FROM masters")
            mawbs = cur.fetchone()[0]
            # Contar Etiquetas totales
            cur.execute("SELECT COUNT(*) FROM labels")
            labels = cur.fetchone()[0]
            conn.close()
            return mawbs, labels
        except:
            return 0, 0

    def refresh_stats(self):
        """
        MÉTODO DE ACTUALIZACIÓN:
        Vuelve a consultar la base de datos y actualiza los números en pantalla.
        """
        mawbs, labels = self.get_stats()
        self.card1.update_value(mawbs)
        self.card2.update_value(labels)