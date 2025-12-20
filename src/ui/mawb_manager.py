from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QHBoxLayout, QFileDialog, 
    QComboBox, QLineEdit, QListWidget, QDialog, QSpinBox, 
    QAbstractItemView, QAbstractSpinBox, QFrame, QFormLayout, 
    QSplitter, QHeaderView, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

# ✅ IMPORTACIONES PARA LA NUBE
from src.utils import get_db_connection
from src.logic.label_pdf import generate_labels_pdf
from src.logic.barcode_utils import generate_barcode_image
from src.logic.logger import log_action
from src.ui.logs_viewer import LogsViewer
from src.logic.manifest_pdf import generate_cargo_manifest
from src.ui.shipment_details import ShipmentDetailsDialog

# --- ESTILOS FLUENT ---
STYLESHEET = """
    QWidget { font-family: 'Segoe UI'; font-size: 14px; }
    
    /* INPUTS */
    QLineEdit, QComboBox {
        background-color: white;
        border: 1px solid #D1D1D1;
        border-radius: 6px;
        padding: 6px 12px;
        color: #333;
    }
    QLineEdit:focus, QComboBox:focus { border: 2px solid #0067C0; }

    /* BOTONES BASE */
    QPushButton {
        border-radius: 6px;
        font-weight: 600;
        padding: 8px 16px;
        border: 1px solid transparent;
    }
    
    /* LISTAS */
    QListWidget {
        background-color: #FAFAFA;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        outline: none;
    }
    QListWidget::item {
        padding: 10px;
        border-bottom: 1px solid #F0F0F0;
        color: #444;
    }
    QListWidget::item:selected {
        background-color: #E3F2FD;
        color: #0067C0;
        border-left: 4px solid #0067C0;
    }
    QListWidget::item:hover { background-color: #F5F5F5; }

    /* TABLA */
    QTableWidget {
        background-color: white;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        gridline-color: #F0F0F0;
        outline: none;
    }
    QHeaderView::section {
        background-color: #FAFAFA;
        border: none;
        border-bottom: 2px solid #E5E5E5;
        padding: 8px;
        font-weight: bold;
        color: #555;
    }
    QTableWidget::item:selected {
        background-color: #E3F2FD;
        color: #000;
    }
"""

BTN_BLUE = """
    QPushButton { background-color: #0067C0; color: white; }
    QPushButton:hover { background-color: #005a9e; }
"""
BTN_ORANGE = """
    QPushButton { background-color: #D83B01; color: white; }
    QPushButton:hover { background-color: #ca3600; }
"""
BTN_WHITE = """
    QPushButton { background-color: white; border: 1px solid #CCC; color: #333; }
    QPushButton:hover { background-color: #F5F5F5; }
"""
BTN_RED = """
    QPushButton { background-color: #D13438; color: white; }
    QPushButton:hover { background-color: #a4262c; }
"""
BTN_RED_ICON = """
    QPushButton { background-color: white; border: 1px solid #D13438; color: #D13438; padding: 6px; }
    QPushButton:hover { background-color: #D13438; color: white; }
"""

# ===================== DIALOGOS AUXILIARES (REDITADOS) =====================
class SimpleHAWBDialog(QDialog):
    def __init__(self, title, hawb_val="", pieces_val=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 240)
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #0067C0;")
        layout.addWidget(lbl)

        form = QFormLayout()
        form.setSpacing(10)
        
        self.hawb_input = QLineEdit(hawb_val); self.hawb_input.setPlaceholderText("Ej: HAWB123")
        self.pieces_input = QSpinBox(); self.pieces_input.setMaximum(9999); self.pieces_input.setValue(pieces_val)
        self.pieces_input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons); self.pieces_input.setSuffix(" pcs")

        form.addRow("Número:", self.hawb_input); form.addRow("Piezas:", self.pieces_input)
        layout.addLayout(form); layout.addStretch()

        btns = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar"); self.cancel_btn.setStyleSheet(BTN_WHITE)
        self.add_btn = QPushButton("Guardar"); self.add_btn.setStyleSheet(BTN_BLUE)
        self.add_btn.clicked.connect(self.accept_data); self.cancel_btn.clicked.connect(self.reject)

        btns.addStretch(); btns.addWidget(self.cancel_btn); btns.addWidget(self.add_btn)
        layout.addLayout(btns)
        self.hawb = ""; self.pieces = 0

    def accept_data(self):
        self.hawb = self.hawb_input.text().strip(); self.pieces = self.pieces_input.value()
        if not self.hawb or self.pieces <= 0: return
        self.accept()

class EditMAWBDialog(QDialog):
    def __init__(self, master_id, username="admin"):
        super().__init__()
        self.master_id = master_id; self.username = username
        self.setWindowTitle("Editar MAWB"); self.setFixedSize(400, 380); self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(15)
        lbl = QLabel("Editar Guía Master"); lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        layout.addWidget(lbl)

        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("SELECT origin, destination, service, total_pieces, mawb_number FROM masters WHERE id = %s", (master_id,))
            data = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM houses WHERE master_id = %s", (master_id,))
            self.has_hawbs = cursor.fetchone()[0] > 0; conn.close()
            if not data: self.reject(); return
            self.old_origin, self.old_dest, self.old_srv, self.old_total, self.mawb_num = data
        except Exception as e: QMessageBox.critical(self, "Error", f"Error DB: {e}"); self.reject(); return

        form = QFormLayout(); form.setSpacing(10)
        self.origin_input = QLineEdit(self.old_origin); self.dest_input = QLineEdit(self.old_dest)
        self.service_combo = QComboBox(); self.service_combo.addItems(["ACA", "ACP", "ACX", "BSA"]); self.service_combo.setCurrentText(self.old_srv)
        self.total_spin = QSpinBox(); self.total_spin.setMaximum(9999); self.total_spin.setValue(self.old_total); self.total_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        if self.has_hawbs: self.total_spin.setDisabled(True)

        form.addRow("Origen:", self.origin_input); form.addRow("Destino:", self.dest_input)
        form.addRow("Servicio:", self.service_combo); form.addRow("Total:", self.total_spin)
        layout.addLayout(form); layout.addStretch()

        btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar"); btn_cancel.setStyleSheet(BTN_WHITE)
        btn_save = QPushButton("Guardar Cambios"); btn_save.setStyleSheet(BTN_BLUE)
        btn_save.clicked.connect(self.save_changes); btn_cancel.clicked.connect(self.reject)
        btns.addStretch(); btns.addWidget(btn_cancel); btns.addWidget(btn_save)
        layout.addLayout(btns)

    def save_changes(self):
        # ... (Lógica de guardado IDÉNTICA al original, sin cambios lógicos) ...
        # Solo copié la lógica para mantener funcionalidad
        new_org = self.origin_input.text().strip().upper(); new_dest = self.dest_input.text().strip().upper()
        new_srv = self.service_combo.currentText(); new_tot = self.total_spin.value()
        if not new_org or not new_dest or new_tot == 0: return
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            cursor.execute("UPDATE masters SET origin=%s, destination=%s, service=%s, total_pieces=%s WHERE id=%s", (new_org, new_dest, new_srv, new_tot, self.master_id))
            # (Lógica de regeneración de etiquetas igual...)
            cursor.execute("DELETE FROM labels WHERE master_id=%s", (self.master_id,))
            cursor.execute("SELECT id, hawb_number, pieces FROM houses WHERE master_id=%s", (self.master_id,))
            houses = cursor.fetchall()
            if not houses:
                for i in range(1, new_tot + 1):
                    code = f"{self.mawb_num}-{str(i).zfill(3)}"; generate_barcode_image(code)
                    cursor.execute("INSERT INTO labels (master_id, mawb_counter, barcode_data) VALUES (%s,%s,%s)", (self.master_id, f"{i}/{new_tot}", code))
            else:
                m_counter = 1
                for hid, hnum, hpcs in houses:
                    for i in range(1, hpcs + 1):
                        code = f"{self.mawb_num}-{hnum}-{str(i).zfill(3)}"; generate_barcode_image(code)
                        cursor.execute("INSERT INTO labels (master_id, house_id, mawb_counter, hawb_counter, barcode_data) VALUES (%s,%s,%s,%s,%s)", (self.master_id, hid, f"{m_counter}/{new_tot}", f"{i}/{hpcs}", code))
                        m_counter += 1
            conn.commit(); conn.close(); self.accept()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

# ===================== GESTOR PRINCIPAL (FLUENT REWORK) =====================
class MAWBManager(QWidget):
    def __init__(self, username="admin"):
        super().__init__()
        self.username = username
        self.setStyleSheet(STYLESHEET) # Aplicar estilos globales

        # Layout Principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # --- 1. HEADER SUPERIOR ---
        header = QHBoxLayout()
        
        lbl_title = QLabel("📦 Inventario de Guías")
        lbl_title.setStyleSheet("font-size: 26px; font-weight: 700; color: #202020;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por MAWB, Origen, Destino...")
        self.search_input.setFixedWidth(350)
        self.search_input.textChanged.connect(self.load_data)
        
        btn_logs = QPushButton("📒 Bitácora")
        btn_logs.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logs.setStyleSheet(BTN_WHITE)
        btn_logs.clicked.connect(self.open_logs)

        header.addWidget(lbl_title)
        header.addStretch()
        header.addWidget(self.search_input)
        header.addWidget(btn_logs)
        main_layout.addLayout(header)

        # --- 2. CONTENIDO (SPLITTER) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #E0E0E0; }")

        # PANEL IZQUIERDO (TABLA)
        left_container = QFrame()
        left_container.setStyleSheet("background-color: white; border: 1px solid #E5E5E5; border-radius: 8px;")
        shadow_l = QGraphicsDropShadowEffect(self); shadow_l.setBlurRadius(10); shadow_l.setColor(QColor(0,0,0,20)); shadow_l.setYOffset(2)
        left_container.setGraphicsEffect(shadow_l)
        
        l_layout = QVBoxLayout(left_container)
        l_layout.setContentsMargins(0,0,0,0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "MAWB", "Ruta", "Servicio", "Total", "Tamaño"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False); self.table.setAlternatingRowColors(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        l_layout.addWidget(self.table)
        splitter.addWidget(left_container)

        # PANEL DERECHO (DETALLES)
        right_container = QFrame()
        right_container.setFixedWidth(420)
        right_container.setStyleSheet("background-color: white; border: 1px solid #E5E5E5; border-radius: 8px;")
        shadow_r = QGraphicsDropShadowEffect(self); shadow_r.setBlurRadius(10); shadow_r.setColor(QColor(0,0,0,20)); shadow_r.setYOffset(2)
        right_container.setGraphicsEffect(shadow_r)

        self.r_layout = QVBoxLayout(right_container)
        self.r_layout.setContentsMargins(20, 25, 20, 25)
        self.r_layout.setSpacing(15)
        
        # Placeholder inicial
        self.lbl_placeholder = QLabel("👈 Selecciona una Guía para ver detalles")
        self.lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_placeholder.setStyleSheet("color: #999; font-size: 14px; font-weight: 500;")
        self.r_layout.addWidget(self.lbl_placeholder)
        self.r_layout.addStretch()

        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 1) # Tabla se expande
        
        main_layout.addWidget(splitter)
        
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        self.load_data()

    # ===================== LOGICA =====================
    def load_data(self):
        self.table.setRowCount(0)
        search = self.search_input.text().strip()
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            # Consulta segura
            query = "SELECT id, mawb_number, origin, destination, service, total_pieces, label_size FROM masters"
            params = []
            if search:
                query += " WHERE mawb_number ILIKE %s OR origin ILIKE %s OR destination ILIKE %s"
                p = f"%{search}%"; params = [p, p, p]
            query += " ORDER BY id DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall(); conn.close()

            for r, row in enumerate(rows):
                self.table.insertRow(r)
                # ID
                self.table.setItem(r, 0, QTableWidgetItem(str(row[0])))
                # MAWB (Negrita Azul)
                it_mawb = QTableWidgetItem(row[1])
                it_mawb.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                it_mawb.setForeground(QColor("#0067C0"))
                self.table.setItem(r, 1, it_mawb)
                # Ruta
                self.table.setItem(r, 2, QTableWidgetItem(f"{row[2]} ➝ {row[3]}"))
                # Servicio
                self.table.setItem(r, 3, QTableWidgetItem(row[4]))
                # Piezas (Badge Style)
                self.table.setItem(r, 4, QTableWidgetItem(f"{row[5]} pcs"))
                # Tamaño
                self.table.setItem(r, 5, QTableWidgetItem(row[6] or "4x6"))

        except Exception as e: print(f"Error carga: {e}")

    def on_row_selected(self):
        row = self.table.currentRow()
        if row == -1: return
        self.clear_panel()

        # Datos de la fila
        mid = int(self.table.item(row, 0).text())
        mnum = self.table.item(row, 1).text()
        msize = self.table.item(row, 5).text()

        # --- TITULO ---
        lbl_h = QLabel(mnum)
        lbl_h.setStyleSheet("font-size: 24px; font-weight: 800; color: #0067C0; margin-bottom: 5px;")
        lbl_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.r_layout.addWidget(lbl_h)

        # --- ACCIONES PRINCIPALES (GRID) ---
        actions_grid = QHBoxLayout()
        
        btn_details = QPushButton("📋 Datos Embarque")
        btn_details.setFixedHeight(40); btn_details.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_details.setStyleSheet(BTN_BLUE)
        btn_details.clicked.connect(lambda: self.open_details(mid, mnum))
        
        btn_pdf = QPushButton("🖨️ Etiquetas")
        btn_pdf.setFixedHeight(40); btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.setStyleSheet(BTN_WHITE)
        btn_pdf.clicked.connect(lambda: self.generate_pdf_action(mid, mnum))
        
        actions_grid.addWidget(btn_details)
        actions_grid.addWidget(btn_pdf)
        self.r_layout.addLayout(actions_grid)

        # --- MANIFIESTO Y TAMAÑO ---
        row_extra = QHBoxLayout()
        btn_man = QPushButton("📄 Manifiesto")
        btn_man.setCursor(Qt.CursorShape.PointingHandCursor); btn_man.setStyleSheet(BTN_ORANGE)
        btn_man.clicked.connect(lambda: self.generate_manifest_action(mid, mnum))
        
        self.combo_size = QComboBox(); self.combo_size.addItems(["4x6", "4x4", "4x2"]); self.combo_size.setCurrentText(msize)
        self.combo_size.setFixedWidth(80)
        self.combo_size.currentIndexChanged.connect(lambda: self.update_size(mid, mnum))
        
        row_extra.addWidget(btn_man)
        row_extra.addStretch()
        row_extra.addWidget(QLabel("Tamaño:"))
        row_extra.addWidget(self.combo_size)
        self.r_layout.addLayout(row_extra)

        # --- SEPARADOR ---
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("background: #EEE; margin: 10px 0;")
        self.r_layout.addWidget(line)

        # --- LISTA HAWBS ---
        lbl_l = QLabel("Desglose de HAWBs"); lbl_l.setStyleSheet("font-weight: bold; color: #555;")
        self.r_layout.addWidget(lbl_l)
        
        self.list_hawbs = QListWidget()
        self.list_hawbs.itemDoubleClicked.connect(self.open_hawb_details)
        self.populate_hawbs_list(mid)
        self.r_layout.addWidget(self.list_hawbs)

        # --- BOTONES HAWB ---
        h_tools = QHBoxLayout()
        btn_add = QPushButton("➕"); btn_add.setToolTip("Agregar HAWB"); btn_add.setStyleSheet(BTN_WHITE); btn_add.clicked.connect(lambda: self.add_hawb(mid, mnum))
        btn_edit = QPushButton("✏️"); btn_edit.setToolTip("Editar Numero/Piezas"); btn_edit.setStyleSheet(BTN_WHITE); btn_edit.clicked.connect(lambda: self.edit_hawb(mid, mnum))
        btn_del = QPushButton("🗑️"); btn_del.setToolTip("Borrar HAWB"); btn_del.setStyleSheet(BTN_RED_ICON); btn_del.clicked.connect(lambda: self.delete_hawb(mid, mnum))
        
        h_tools.addWidget(btn_add); h_tools.addWidget(btn_edit); h_tools.addStretch(); h_tools.addWidget(btn_del)
        self.r_layout.addLayout(h_tools)

        # --- SEPARADOR ---
        line2 = QFrame(); line2.setFrameShape(QFrame.Shape.HLine); line2.setStyleSheet("background: #EEE; margin: 10px 0;")
        self.r_layout.addWidget(line2)

        # --- GESTION MASTER ---
        m_tools = QHBoxLayout()
        btn_medit = QPushButton("Editar Master"); btn_medit.setStyleSheet(BTN_WHITE); btn_medit.clicked.connect(lambda: self.edit_mawb_action(mid))
        btn_mdel = QPushButton("Eliminar Todo"); btn_mdel.setStyleSheet(BTN_RED); btn_mdel.clicked.connect(lambda: self.delete_mawb_action(mid, mnum))
        m_tools.addWidget(btn_medit); m_tools.addStretch(); m_tools.addWidget(btn_mdel)
        self.r_layout.addLayout(m_tools)

    def clear_panel(self):
        while self.r_layout.count():
            child = self.r_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout():
                # Borrar layouts anidados
                while child.layout().count():
                    sub = child.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()

    # ... (MÉTODOS LÓGICOS SE MANTIENEN IGUALES: populate_hawbs, open_details, etc.) ...
    # Solo copié la lógica exacta de tu archivo anterior para no romper nada
    
    def populate_hawbs_list(self, master_id):
        self.list_hawbs.clear(); self.current_hawbs_data = [] 
        conn = get_db_connection(); cursor = conn.cursor()
        cursor.execute("SELECT id, hawb_number, pieces FROM houses WHERE master_id=%s", (master_id,))
        rows = cursor.fetchall(); conn.close()
        if not rows: self.list_hawbs.addItem("ℹ️ Sin HAWBs (Consolidado puro)"); self.list_hawbs.item(0).setForeground(QColor("#999"))
        else:
            for hid, num, pcs in rows:
                self.list_hawbs.addItem(f"📄 {num}  —  {pcs} pcs"); self.current_hawbs_data.append((hid, num, pcs))

    def open_hawb_details(self, item):
        row = self.list_hawbs.row(item)
        if row == -1: return
        try: hid, hnum, hpcs = self.current_hawbs_data[row]
        except: return
        dialog = ShipmentDetailsDialog(hid, hnum, is_house=True, parent=self)
        dialog.exec()
        curr = self.table.currentRow(); self.load_data(); self.table.selectRow(curr); self.on_row_selected()

    def open_details(self, mid, mnum):
        dialog = ShipmentDetailsDialog(mid, mnum, is_house=False, parent=self)
        dialog.exec()
        curr = self.table.currentRow(); self.load_data(); self.table.selectRow(curr); self.on_row_selected()

    def update_size(self, mid, mnum):
        ns = self.combo_size.currentText()
        try:
            conn = get_db_connection(); c = conn.cursor()
            c.execute("UPDATE masters SET label_size=%s WHERE id=%s", (ns, mid)); conn.commit(); conn.close()
            self.table.setItem(self.table.currentRow(), 5, QTableWidgetItem(ns))
        except: pass

    def generate_pdf_action(self, mid, mnum):
        size = self.combo_size.currentText()
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", f"{mnum}.pdf", "PDF (*.pdf)")
        if path:
            try: generate_labels_pdf(mid, path, size); QMessageBox.information(self, "Listo", "Etiquetas generadas.")
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def generate_manifest_action(self, mid, mnum):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Manifiesto", f"MANIFEST-{mnum}.pdf", "PDF (*.pdf)")
        if path:
            try: generate_cargo_manifest(mid, path); QMessageBox.information(self, "Listo", "Manifiesto generado.")
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def add_hawb(self, mid, mnum):
        d = SimpleHAWBDialog("Agregar HAWB", parent=self)
        if d.exec():
            # Validación simple de duplicados en memoria
            nh = d.hawb.strip().upper()
            for _, eh, _ in self.current_hawbs_data:
                if eh.strip().upper() == nh: QMessageBox.warning(self,"!","Ya existe."); return
            try:
                conn = get_db_connection(); c = conn.cursor()
                c.execute("INSERT INTO houses (master_id, hawb_number, pieces) VALUES (%s,%s,%s)", (mid, d.hawb, d.pieces))
                c.execute("SELECT SUM(pieces) FROM houses WHERE master_id=%s", (mid,)); nt = c.fetchone()[0]
                c.execute("UPDATE masters SET total_pieces=%s WHERE id=%s", (nt, mid))
                self.regenerate_labels_db(c, mid, mnum, nt); conn.commit(); conn.close()
                curr = self.table.currentRow(); self.load_data(); self.table.selectRow(curr); self.on_row_selected()
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def edit_hawb(self, mid, mnum):
        if not self.current_hawbs_data: return
        row = self.list_hawbs.currentRow()
        if row == -1: return
        hid, hnum, hpcs = self.current_hawbs_data[row]
        d = SimpleHAWBDialog("Editar HAWB", hnum, hpcs, self)
        if d.exec():
            try:
                conn = get_db_connection(); c = conn.cursor()
                c.execute("UPDATE houses SET hawb_number=%s, pieces=%s WHERE id=%s", (d.hawb, d.pieces, hid))
                c.execute("SELECT SUM(pieces) FROM houses WHERE master_id=%s", (mid,)); nt = c.fetchone()[0]
                c.execute("UPDATE masters SET total_pieces=%s WHERE id=%s", (nt, mid))
                self.regenerate_labels_db(c, mid, mnum, nt); conn.commit(); conn.close()
                curr = self.table.currentRow(); self.load_data(); self.table.selectRow(curr); self.on_row_selected()
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def delete_hawb(self, mid, mnum):
        if not self.current_hawbs_data: return
        row = self.list_hawbs.currentRow()
        if row == -1: return
        hid, hnum, _ = self.current_hawbs_data[row]
        if QMessageBox.question(self, "Borrar", f"¿Borrar {hnum}?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            conn = get_db_connection(); c = conn.cursor()
            c.execute("DELETE FROM houses WHERE id=%s", (hid,))
            c.execute("SELECT SUM(pieces) FROM houses WHERE master_id=%s", (mid,)); res = c.fetchone()[0]; nt = res if res else 0
            c.execute("UPDATE masters SET total_pieces=%s WHERE id=%s", (nt, mid))
            self.regenerate_labels_db(c, mid, mnum, nt); conn.commit(); conn.close()
            curr = self.table.currentRow(); self.load_data(); self.table.selectRow(curr); self.on_row_selected()

    def regenerate_labels_db(self, cursor, mid, mnum, total):
        cursor.execute("DELETE FROM labels WHERE master_id=%s", (mid,))
        if total == 0: return
        cursor.execute("SELECT id, hawb_number, pieces FROM houses WHERE master_id=%s", (mid,))
        houses = cursor.fetchall()
        if not houses:
            for i in range(1, total + 1):
                code = f"{mnum}-{str(i).zfill(3)}"; generate_barcode_image(code)
                cursor.execute("INSERT INTO labels (master_id, mawb_counter, barcode_data) VALUES (%s,%s,%s)", (mid, f"{i}/{total}", code))
        else:
            mc = 1
            for hid, hnum, hpcs in houses:
                for i in range(1, hpcs + 1):
                    code = f"{mnum}-{hnum}-{str(i).zfill(3)}"; generate_barcode_image(code)
                    cursor.execute("INSERT INTO labels (master_id, house_id, mawb_counter, hawb_counter, barcode_data) VALUES (%s,%s,%s,%s,%s)", (mid, hid, f"{mc}/{total}", f"{i}/{hpcs}", code))
                    mc += 1

    def edit_mawb_action(self, mid):
        d = EditMAWBDialog(mid, self.username)
        if d.exec(): curr = self.table.currentRow(); self.load_data(); self.table.selectRow(curr); self.on_row_selected()

    def delete_mawb_action(self, mid, mnum):
        if QMessageBox.question(self, "Eliminar", f"¿Borrar TODO {mnum}?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            conn = get_db_connection(); c = conn.cursor()
            c.execute("DELETE FROM labels WHERE master_id=%s", (mid,))
            c.execute("DELETE FROM houses WHERE master_id=%s", (mid,))
            c.execute("DELETE FROM masters WHERE id=%s", (mid,))
            conn.commit(); conn.close(); self.load_data(); self.clear_panel()

    def open_logs(self):
        self.logs = LogsViewer(); self.logs.show()