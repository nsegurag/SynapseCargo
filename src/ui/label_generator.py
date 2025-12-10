from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox,
    QComboBox, QSpinBox, QScrollArea, QDialog, 
    QAbstractSpinBox, QGroupBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QFont

# ✅ IMPORTACIONES CORRECTAS (Nube + Logica)
from src.logic.barcode_utils import generate_barcode_image
from src.logic.logger import log_action
from src.utils import get_db_connection

# ===================== DIALOGO AGREGAR HAWB =====================
class AddHAWBDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Guía Hija")
        self.setFixedSize(360, 240)
        
        self.setStyleSheet("QDialog { background-color: white; } QLabel { background-color: transparent; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("Nueva HAWB")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0067C0; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        
        self.hawb_input = QLineEdit()
        self.hawb_input.setPlaceholderText("Número (Ej: HAWB123)")
        self.hawb_input.setMinimumHeight(32)
        
        self.pieces_input = QSpinBox()
        self.pieces_input.setMaximum(9999)
        self.pieces_input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.pieces_input.setMinimumHeight(32)
        self.pieces_input.setMinimumWidth(100)

        form.addRow("Número:", self.hawb_input)
        form.addRow("Piezas:", self.pieces_input)
        layout.addLayout(form)

        layout.addStretch()

        btns = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.add_btn = QPushButton("Agregar")
        self.add_btn.setObjectName("Primary")

        self.add_btn.clicked.connect(self.accept_data)
        self.cancel_btn.clicked.connect(self.reject)

        btns.addStretch()
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.add_btn)
        layout.addLayout(btns)

        self.setLayout(layout)
        
        self.hawb_input.returnPressed.connect(self.pieces_input.setFocus)
        self.pieces_input.editingFinished.connect(self.add_btn.setFocus)

    def accept_data(self):
        self.hawb = self.hawb_input.text().strip()
        self.pieces = self.pieces_input.value()
        if not self.hawb or self.pieces <= 0:
            return
        self.accept()

# ===================== WIDGET GENERADOR DE ETIQUETAS =====================
# Renombrado a LabelGeneratorWidget para evitar conflictos
class LabelGeneratorWidget(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        
        # Eliminamos setMinimumSize para que se adapte al Dashboard
        # self.setMinimumSize(600, 750) 
        
        self.setStyleSheet("""
            QLabel { 
                background-color: transparent; 
                color: #333;
                font-weight: 500;
            }
            QGroupBox {
                background-color: white; 
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #0067C0;
                font-weight: bold;
            }
            QWidget#ScrollContent {
                background-color: transparent;
            }
        """)
        
        self.hawb_rows = [] 

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        title_lbl = QLabel("Generar Nueva Guía Master")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #222;")
        header.addWidget(title_lbl)
        header.addStretch()
        
        # Eliminamos el botón "Ver Inventario" porque ya está en la Sidebar
        main_layout.addLayout(header)

        # 1. SECCIÓN MAWB
        gb_mawb = QGroupBox("Datos Master (MAWB)")
        gb_mawb.setObjectName("Card") 
        form_mawb = QFormLayout(gb_mawb)
        form_mawb.setContentsMargins(20, 25, 20, 20)
        form_mawb.setSpacing(15)
        form_mawb.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # MAWB
        row_mawb = QHBoxLayout()
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("XXX")
        self.prefix_input.setMaxLength(3)
        self.prefix_input.setFixedWidth(70)
        self.prefix_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("12345678")
        self.number_input.setMaxLength(8)
        
        row_mawb.addWidget(self.prefix_input)
        row_mawb.addWidget(QLabel("-", styleSheet="color: #AAA; font-size: 18px; font-weight: bold; border:none;"))
        row_mawb.addWidget(self.number_input)
        form_mawb.addRow("Número:", row_mawb)

        # Ruta
        row_route = QHBoxLayout()
        self.origin_input = QLineEdit()
        self.origin_input.setPlaceholderText("Origen")
        self.origin_input.setMaxLength(3)
        
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("Destino")
        self.dest_input.setMaxLength(3)
        
        row_route.addWidget(self.origin_input)
        row_route.addWidget(QLabel("→", styleSheet="color: #AAA; font-size: 18px; font-weight: bold; border:none;"))
        row_route.addWidget(self.dest_input)
        form_mawb.addRow("Ruta:", row_route)

        # Detalles
        row_details = QHBoxLayout()
        self.service_combo = QComboBox()
        self.service_combo.addItems(["ACA", "ACP", "ACX", "BSA"])
        self.service_combo.setMinimumWidth(120)
        
        self.total_pieces = QSpinBox()
        self.total_pieces.setMaximum(9999)
        self.total_pieces.setSuffix(" pcs")
        self.total_pieces.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.total_pieces.setMinimumHeight(30)
        
        row_details.addWidget(self.service_combo)
        row_details.addSpacing(20)
        row_details.addWidget(QLabel("Total:"))
        row_details.addWidget(self.total_pieces)
        
        form_mawb.addRow("Detalles:", row_details)
        main_layout.addWidget(gb_mawb)

        # 2. SECCIÓN HAWB
        gb_hawb = QGroupBox("Guías Hijas (Opcional)")
        gb_hawb.setObjectName("Card")
        layout_hawb = QVBoxLayout(gb_hawb)
        layout_hawb.setContentsMargins(20, 25, 20, 20)

        header_h = QHBoxLayout()
        header_h.addWidget(QLabel("Desglose de HAWBs:"))
        header_h.addStretch()
        self.btn_add_hawb = QPushButton("➕ Agregar Hija")
        self.btn_add_hawb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_hawb.clicked.connect(self.add_hawb_dialog)
        header_h.addWidget(self.btn_add_hawb)
        layout_hawb.addLayout(header_h)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("ScrollContent")
        self.hawb_list_layout = QVBoxLayout(scroll_content)
        self.hawb_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.hawb_list_layout.setSpacing(10)
        
        scroll.setWidget(scroll_content)
        layout_hawb.addWidget(scroll)
        
        main_layout.addWidget(gb_hawb, stretch=1)

        # 3. BOTÓN GUARDAR
        self.btn_save = QPushButton("💾  GUARDAR Y GENERAR ETIQUETAS")
        self.btn_save.setObjectName("Primary")
        self.btn_save.setMinimumHeight(50)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("font-size: 14px; letter-spacing: 1px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_data)
        main_layout.addWidget(self.btn_save)

        self.setLayout(main_layout)

        # Navegación Teclado
        self.setTabOrder(self.prefix_input, self.number_input)
        self.setTabOrder(self.number_input, self.origin_input)
        self.setTabOrder(self.origin_input, self.dest_input)
        self.setTabOrder(self.dest_input, self.service_combo)
        self.setTabOrder(self.service_combo, self.total_pieces)
        self.setTabOrder(self.total_pieces, self.btn_add_hawb)
        self.setTabOrder(self.btn_add_hawb, self.btn_save)

        self.prefix_input.returnPressed.connect(self.number_input.setFocus)
        self.number_input.returnPressed.connect(self.origin_input.setFocus)
        self.origin_input.returnPressed.connect(self.dest_input.setFocus)
        self.dest_input.returnPressed.connect(self.total_pieces.setFocus)
        
        self.prefix_input.setFocus()

    # ===================== FILAS HAWB =====================
    def add_hawb_dialog(self):
        dialog = AddHAWBDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_hawb = dialog.hawb.strip().upper()
            for row in self.hawb_rows:
                if row["hawb"].strip().upper() == new_hawb:
                    QMessageBox.warning(self, "Duplicado", f"La HAWB '{new_hawb}' ya está en la lista.")
                    return
            self.add_hawb_row(dialog.hawb, dialog.pieces)

    def add_hawb_row(self, hawb, pieces):
        row_widget = QWidget()
        row_widget.setFixedHeight(55)
        row_widget.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
        """)
        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        lbl_icon = QLabel("📄")
        lbl_icon.setStyleSheet("border: none; background: transparent; font-size: 16px;")

        inp_hawb = QLineEdit(hawb)
        inp_hawb.setPlaceholderText("HAWB")
        inp_hawb.setMinimumHeight(32)
        inp_hawb.setReadOnly(True) 
        inp_hawb.setStyleSheet("border: none; background: transparent; font-size: 14px; font-weight: bold; color: #333;") 
        
        inp_pcs = QLineEdit(f"{pieces} pcs")
        inp_pcs.setReadOnly(True)
        inp_pcs.setFixedWidth(80)
        inp_pcs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inp_pcs.setStyleSheet("border: 1px solid #EEE; background: #FAFAFA; border-radius: 15px; color: #555;")

        btn_del = QPushButton("🗑") 
        btn_del.setFixedSize(32, 32)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip("Eliminar HAWB")
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: #FFF0F0; 
                color: #D32F2F; 
                border: 1px solid #FFCDCD;
                border-radius: 6px;
                font-size: 16px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
                color: white;
                border-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)
        btn_del.clicked.connect(lambda: self.delete_hawb_row(row_widget))

        layout.addWidget(lbl_icon)
        layout.addWidget(inp_hawb, 1)
        layout.addWidget(inp_pcs, 0)
        layout.addWidget(btn_del, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.hawb_list_layout.addWidget(row_widget)
        self.hawb_rows.append({"widget": row_widget, "hawb": hawb, "pieces": pieces})

    def delete_hawb_row(self, widget):
        self.hawb_rows = [row for row in self.hawb_rows if row["widget"] != widget]
        widget.deleteLater()

    def reset_fields(self):
        self.prefix_input.clear()
        self.number_input.clear()
        self.origin_input.clear()
        self.dest_input.clear()
        self.total_pieces.setValue(0)
        for row in self.hawb_rows:
            row["widget"].deleteLater()
        self.hawb_rows = []
        self.prefix_input.setFocus() 

    # ===================== GUARDADO (CONECTADO A LA NUBE) =====================
    def save_data(self):
        prefix = self.prefix_input.text().strip()
        number = self.number_input.text().strip()
        origin = self.origin_input.text().strip().upper()
        dest = self.dest_input.text().strip().upper()
        service = self.service_combo.currentText()
        total = self.total_pieces.value()

        if not prefix or not number or not origin or not dest or total == 0:
            QMessageBox.warning(self, "Atención", "Completa todos los campos obligatorios.")
            return

        full_mawb = f"{prefix}-{number}"
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM masters WHERE mawb_number = %s", (full_mawb,))
            exists = cursor.fetchone()
            
            if exists:
                conn.close()
                QMessageBox.warning(self, "Duplicado", f"La MAWB {full_mawb} ya existe en el inventario.")
                return
                
        except Exception as e:
            if conn: conn.close()
            QMessageBox.critical(self, "Error de Conexión", f"Error verificando duplicados:\n{e}")
            return

        active_hawbs = []
        for row in self.hawb_rows:
            active_hawbs.append((row["hawb"], row["pieces"]))

        if active_hawbs:
            sum_hawbs = sum(p for h, p in active_hawbs)
            if sum_hawbs != total:
                if conn: conn.close()
                QMessageBox.critical(self, "Error", f"Total declarado ({total}) no coincide con suma de HAWBs ({sum_hawbs}).")
                return

        try:
            if conn.closed:
                conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO masters (mawb_number, origin, destination, service, total_pieces, created_by)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (full_mawb, origin, dest, service, total, self.username))
            
            master_id = cursor.fetchone()[0]
            
            mawb_counter = 1
            if not active_hawbs:
                for i in range(1, total + 1):
                    mawb_c = f"{i}/{total}"
                    code = f"{full_mawb}-{str(i).zfill(3)}"
                    generate_barcode_image(code)
                    cursor.execute("INSERT INTO labels (master_id, mawb_counter, barcode_data) VALUES (%s, %s, %s)", 
                                   (master_id, mawb_c, code))
            else:
                for hawb_num, pcs in active_hawbs:
                    cursor.execute("INSERT INTO houses (master_id, hawb_number, pieces) VALUES (%s, %s, %s) RETURNING id", 
                                   (master_id, hawb_num, pcs))
                    house_id = cursor.fetchone()[0]
                    
                    for i in range(1, pcs + 1):
                        mawb_c = f"{mawb_counter}/{total}"
                        hawb_c = f"{i}/{pcs}"
                        code = f"{full_mawb}-{hawb_num}-{str(i).zfill(3)}"
                        generate_barcode_image(code)
                        cursor.execute("""
                            INSERT INTO labels (master_id, house_id, mawb_counter, hawb_counter, barcode_data)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (master_id, house_id, mawb_c, hawb_c, code))
                        mawb_counter += 1

            conn.commit()
            conn.close()
            
            log_action(self.username, "CREO MAWB", full_mawb, f"Total: {total}")
            QMessageBox.information(self, "Éxito", "Etiquetas generadas y guardadas.")
            self.reset_fields()

        except Exception as e:
            if conn: conn.close()
            QMessageBox.critical(self, "Error al Guardar", str(e))