import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QDoubleSpinBox, QFormLayout, 
    QGroupBox, QComboBox, QMessageBox, QTabWidget, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIntValidator
from src.utils import get_db_connection
from src.logic.logger import log_action

# --- ESTILOS "CLEAN & FAST" ---
STYLESHEET = """
    QWidget { font-family: 'Segoe UI'; font-size: 13px; background-color: #F9F9F9; }
    
    /* HEADER COMPACTO */
    QLineEdit#MawbInput {
        font-size: 15px; font-weight: bold; color: #333;
        border: 1px solid #CCC; border-radius: 4px; padding: 4px 8px; background: white;
    }
    QLineEdit#MawbInput:focus { border: 2px solid #0067C0; }

    /* GRUPOS SIN BORDES (TUS "CUADROS" ELIMINADOS) */
    QGroupBox {
        background-color: transparent;
        border: none; 
        font-weight: 700; color: #0067C0;
        margin-top: 15px; padding-top: 5px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 0px; padding: 0 0 5px 0; }

    /* INPUTS FORMULARIO */
    QLineEdit, QTextEdit, QDoubleSpinBox, QComboBox {
        background-color: white; border: 1px solid #E0E0E0; border-radius: 4px; padding: 6px;
    }
    QLineEdit:disabled, QTextEdit:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {
        background-color: #F4F4F4; color: #AAA; border: 1px solid #EEE;
    }
    QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border: 1px solid #0067C0; background-color: #FFF;
    }

    /* TABS LIMPIOS */
    QTabWidget::pane { border: none; background: transparent; }
    QTabBar::tab {
        background: transparent; color: #666; padding: 8px 20px;
        border-bottom: 2px solid transparent; font-weight: 600;
    }
    QTabBar::tab:selected { color: #0067C0; border-bottom: 2px solid #0067C0; }
    QTabBar::tab:hover { background: #EEE; border-radius: 4px; }
"""

# BOTONES
BTN_BLUE = "QPushButton { background-color: #0067C0; color: white; border-radius: 4px; font-weight: 600; padding: 6px 15px; border: none; } QPushButton:hover { background-color: #005a9e; }"
BTN_GREEN = "QPushButton { background-color: #107C10; color: white; border-radius: 4px; font-weight: 600; padding: 6px 15px; border: none; } QPushButton:hover { background-color: #0b5a0b; }"
BTN_WHITE = "QPushButton { background-color: white; border: 1px solid #DDD; border-radius: 4px; color: #333; padding: 6px 12px; } QPushButton:hover { background-color: #F5F5F5; }"
BTN_RED_TEXT = "QPushButton { background: transparent; color: #D32F2F; font-weight: bold; border: none; } QPushButton:hover { background: #FFEBEE; border-radius: 4px; }"

class AddressBlock(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        layout = QFormLayout(self); layout.setSpacing(8); layout.setContentsMargins(0, 10, 0, 10)
        
        self.name = QLineEdit(); self.name.setPlaceholderText("Nombre / Razón Social")
        self.account = QLineEdit(); self.account.setPlaceholderText("Account No.")
        self.address = QTextEdit(); self.address.setMaximumHeight(45); self.address.setPlaceholderText("Dirección...")
        
        row1 = QHBoxLayout()
        self.city = QLineEdit(); self.city.setPlaceholderText("Ciudad")
        self.zip = QLineEdit(); self.zip.setPlaceholderText("Zip")
        self.zip.setFixedWidth(80)
        row1.addWidget(self.city); row1.addWidget(self.zip)
        
        row2 = QHBoxLayout()
        self.state = QLineEdit(); self.state.setPlaceholderText("Estado")
        self.country = QLineEdit(); self.country.setPlaceholderText("País")
        self.country.setFixedWidth(60)
        row2.addWidget(self.state); row2.addWidget(self.country)
        
        row3 = QHBoxLayout()
        self.phone = QLineEdit(); self.phone.setPlaceholderText("Tel")
        self.email = QLineEdit(); self.email.setPlaceholderText("Email")
        row3.addWidget(self.phone); row3.addWidget(self.email)

        layout.addRow("Nombre:", self.name)
        layout.addRow("Cuenta:", self.account)
        layout.addRow("Dirección:", self.address)
        layout.addRow("Ubicación:", row1)
        layout.addRow("", row2)
        layout.addRow("Contacto:", row3)

    def get_data(self):
        return {
            "name": self.name.text(), "account": self.account.text(), "address": self.address.toPlainText(),
            "city": self.city.text(), "zip": self.zip.text(), "state": self.state.text(),
            "country": self.country.text(), "phone": self.phone.text(), "email": self.email.text()
        }

    def set_data(self, d):
        self.name.setText(d.get("name","") or ""); self.account.setText(d.get("account","") or ""); self.address.setText(d.get("address","") or "")
        self.city.setText(d.get("city","") or ""); self.zip.setText(d.get("zip","") or ""); self.state.setText(d.get("state","") or "")
        self.country.setText(d.get("country","") or ""); self.phone.setText(d.get("phone","") or ""); self.email.setText(d.get("email","") or "")
    
    def clear_data(self):
        self.name.clear(); self.account.clear(); self.address.clear(); self.city.clear(); self.zip.clear()
        self.state.clear(); self.country.clear(); self.phone.clear(); self.email.clear()

class DocumentationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(STYLESHEET)
        self.current_master_id = None 
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)

        # 1. HEADER COMPACTO (La barra de herramientas que pediste)
        header = QFrame()
        hl = QHBoxLayout(header); hl.setContentsMargins(0, 0, 0, 10); hl.setSpacing(10)

        lbl_t = QLabel("MAWB CAPTURE"); lbl_t.setStyleSheet("font-weight: 900; color: #888; font-size: 14px; letter-spacing: 1px;")
        
        # Inputs Pequeños y Elegantes
        self.txt_prefix = QLineEdit(); self.txt_prefix.setObjectName("MawbInput")
        self.txt_prefix.setFixedWidth(65); self.txt_prefix.setMaxLength(3); self.txt_prefix.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_prefix.setPlaceholderText("Prefix"); self.txt_prefix.textChanged.connect(self.auto_focus_number) 

        self.txt_number = QLineEdit(); self.txt_number.setObjectName("MawbInput")
        self.txt_number.setFixedWidth(110); self.txt_number.setMaxLength(8); self.txt_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_number.setPlaceholderText("12345678"); self.txt_number.returnPressed.connect(self.search_or_load)

        btn_go = QPushButton("Cargar"); btn_go.setCursor(Qt.CursorShape.PointingHandCursor); btn_go.setStyleSheet(BTN_BLUE)
        btn_go.clicked.connect(self.search_or_load)

        # 🔥 BOTÓN LIMPIAR
        btn_clear = QPushButton("Limpiar / Nuevo"); btn_clear.setCursor(Qt.CursorShape.PointingHandCursor); btn_clear.setStyleSheet(BTN_WHITE)
        btn_clear.clicked.connect(self.reset_form)

        self.btn_save = QPushButton("💾 Guardar Todo"); self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor); self.btn_save.setStyleSheet(BTN_GREEN)
        self.btn_save.clicked.connect(self.save_data); self.btn_save.setEnabled(False)

        hl.addWidget(lbl_t); hl.addSpacing(15)
        hl.addWidget(self.txt_prefix); hl.addWidget(QLabel("-")); hl.addWidget(self.txt_number)
        hl.addWidget(btn_go); hl.addWidget(btn_clear)
        hl.addStretch()
        hl.addWidget(self.btn_save)
        
        main_layout.addWidget(header)

        # 2. CUERPO TABS
        self.tabs = QTabWidget()
        self.tabs.setEnabled(False) 
        
        self.tab_general = QWidget(); self.tab_cargo = QWidget(); self.tab_rates = QWidget(); self.tab_hawbs = QWidget()
        
        self.setup_general_tab(); self.setup_cargo_tab(); self.setup_rates_tab(); self.setup_hawbs_tab()
        
        self.tabs.addTab(self.tab_general, "General")
        self.tabs.addTab(self.tab_cargo, "Carga")
        self.tabs.addTab(self.tab_rates, "Tarifas")
        self.tabs.addTab(self.tab_hawbs, "Hijas")
        
        main_layout.addWidget(self.tabs)

    # --- SETUP UI TABS ---
    def setup_general_tab(self):
        layout = QHBoxLayout(self.tab_general); layout.setSpacing(40); layout.setContentsMargins(10,10,10,10)
        self.shipper_block = AddressBlock("Shipper / Remitente")
        self.consignee_block = AddressBlock("Consignee / Destinatario")
        layout.addWidget(self.shipper_block); layout.addWidget(self.consignee_block)

    def setup_cargo_tab(self):
        layout = QVBoxLayout(self.tab_cargo); layout.setContentsMargins(10,10,10,10); layout.setSpacing(20)
        
        # Fila 1: Ruta y Cantidades (Sin Grupo, directo al layout)
        r1 = QHBoxLayout()
        self.inp_org = QLineEdit(); self.inp_org.setPlaceholderText("ORIGEN"); self.inp_org.setFixedWidth(60)
        self.inp_dst = QLineEdit(); self.inp_dst.setPlaceholderText("DESTINO"); self.inp_dst.setFixedWidth(60)
        self.inp_pcs = QDoubleSpinBox(); self.inp_pcs.setRange(0,99999); self.inp_pcs.setDecimals(0); self.inp_pcs.setSuffix(" pcs")
        self.inp_w = QDoubleSpinBox(); self.inp_w.setRange(0,999999); self.inp_w.setSuffix(" kg")
        
        r1.addWidget(QLabel("Ruta:")); r1.addWidget(self.inp_org); r1.addWidget(QLabel("➝")); r1.addWidget(self.inp_dst)
        r1.addSpacing(30)
        r1.addWidget(QLabel("Piezas:")); r1.addWidget(self.inp_pcs)
        r1.addWidget(QLabel("Peso Bruto:")); r1.addWidget(self.inp_w)
        r1.addStretch()
        layout.addLayout(r1)

        self.inp_desc = QLineEdit(); self.inp_desc.setPlaceholderText("Descripción de la mercancía (Ej: CONSOLIDATION)")
        layout.addWidget(self.inp_desc)

        # Dimensiones (Titulo sutil)
        lbl_dim = QLabel("Calculadora Volumétrica"); lbl_dim.setStyleSheet("font-weight: bold; color: #0067C0; margin-top: 10px;")
        layout.addWidget(lbl_dim)

        h_tools = QHBoxLayout()
        self.combo_unit = QComboBox(); self.combo_unit.addItems(["CM", "INCH"])
        btn_add = QPushButton("➕"); btn_add.clicked.connect(self.add_dim_row); btn_add.setFixedWidth(40)
        btn_del = QPushButton("🗑️"); btn_del.clicked.connect(self.del_dim_row); btn_del.setStyleSheet(BTN_RED_TEXT); btn_del.setFixedWidth(40)
        h_tools.addWidget(QLabel("Unidad:")); h_tools.addWidget(self.combo_unit); h_tools.addWidget(btn_add); h_tools.addWidget(btn_del); h_tools.addStretch()
        layout.addLayout(h_tools)
        
        self.table_dims = QTableWidget(0, 5); self.table_dims.setHorizontalHeaderLabels(["Pcs", "L", "W", "H", "Vol m³"])
        self.table_dims.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_dims.itemChanged.connect(self.calc_row_vol); self.table_dims.setStyleSheet("border: 1px solid #DDD;")
        layout.addWidget(self.table_dims)
        
        h_res = QHBoxLayout()
        self.lbl_vol = QLabel("Vol: 0.000 m³"); self.lbl_chg = QLabel("Peso Cobrable: 0.00 kg")
        self.lbl_chg.setStyleSheet("font-weight: bold; color: #D83B01; font-size: 15px;")
        h_res.addStretch(); h_res.addWidget(self.lbl_vol); h_res.addSpacing(20); h_res.addWidget(self.lbl_chg)
        layout.addLayout(h_res)

    def setup_rates_tab(self):
        layout = QFormLayout(self.tab_rates); layout.setContentsMargins(30,30,30,30); layout.setSpacing(15)
        self.combo_pp_cc = QComboBox(); self.combo_pp_cc.addItems(["PP", "CC"])
        self.inp_curr = QLineEdit("USD")
        self.inp_rate = QDoubleSpinBox(); self.inp_rate.setRange(0,99999); self.inp_rate.setPrefix("$ "); self.inp_rate.valueChanged.connect(self.calc_totals)
        self.inp_total = QDoubleSpinBox(); self.inp_total.setRange(0,999999); self.inp_total.setPrefix("$ ")
        self.txt_other = QTextEdit(); self.txt_other.setMaximumHeight(80); self.txt_other.setPlaceholderText("Otros cargos...")
        layout.addRow("Modo Pago:", self.combo_pp_cc); layout.addRow("Moneda:", self.inp_curr)
        layout.addRow("Rate / Kg:", self.inp_rate); layout.addRow("Total Flete:", self.inp_total)
        layout.addRow("Otros Cargos:", self.txt_other)

    def setup_hawbs_tab(self):
        layout = QVBoxLayout(self.tab_hawbs); layout.setContentsMargins(10,10,10,10)
        self.table_hawbs = QTableWidget(0, 3); self.table_hawbs.setHorizontalHeaderLabels(["HAWB", "Piezas", "Peso"])
        self.table_hawbs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_hawbs.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers); self.table_hawbs.setStyleSheet("border: 1px solid #DDD;")
        layout.addWidget(self.table_hawbs)
        btn_refresh = QPushButton("Recargar Lista"); btn_refresh.setStyleSheet(BTN_WHITE); btn_refresh.clicked.connect(self.load_hawbs)
        layout.addWidget(btn_refresh)

    # --- LOGICA ---
    def auto_focus_number(self):
        if len(self.txt_prefix.text()) == 3: self.txt_number.setFocus()

    def reset_form(self):
        self.txt_prefix.clear(); self.txt_number.clear()
        self.clear_fields()
        self.tabs.setEnabled(False); self.btn_save.setEnabled(False)
        self.current_master_id = None; self.txt_prefix.setFocus()

    def search_or_load(self):
        prefix = self.txt_prefix.text().strip(); number = self.txt_number.text().strip()
        if len(prefix) != 3 or len(number) != 8: QMessageBox.warning(self, "Formato", "Formato: XXX - 12345678"); return
        full_mawb = f"{prefix}-{number}"
        
        try:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT id FROM masters WHERE mawb_number = %s", (full_mawb,))
            res = cur.fetchone(); conn.close()
            
            if res:
                self.current_master_id = res[0]; self.load_data_db(); self.tabs.setEnabled(True); self.btn_save.setEnabled(True)
                self.tabs.setCurrentIndex(0) # Ir a General
            else:
                if QMessageBox.question(self, "Nueva", f"¿Crear guía {full_mawb}?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                    self.create_new_mawb(full_mawb)
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def create_new_mawb(self, mawb_num):
        try:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO masters (mawb_number, total_pieces, status) VALUES (%s, 0, 'OPEN') RETURNING id", (mawb_num,))
            self.current_master_id = cur.fetchone()[0]; conn.commit(); conn.close()
            self.tabs.setEnabled(True); self.btn_save.setEnabled(True); self.clear_fields()
            QMessageBox.information(self, "Creada", "Lista para capturar datos.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def load_data_db(self):
        if not self.current_master_id: return
        try:
            conn = get_db_connection(); cur = conn.cursor()
            query = """SELECT origin, destination, total_pieces, weight_kg, nature_of_goods,
                       shipper_name, sh_account, shipper_address, sh_city, sh_zip, sh_state, sh_country, sh_phone, sh_email,
                       consignee_name, cn_account, consignee_address, cn_city, cn_zip, cn_state, cn_country, cn_phone, cn_email,
                       payment_mode, currency, freight_rate, freight_total, other_charges, dimensions_data
                FROM masters WHERE id = %s"""
            cur.execute(query, (self.current_master_id,)); r = cur.fetchone(); conn.close()
            
            if r:
                self.inp_org.setText(r[0] or ""); self.inp_dst.setText(r[1] or "")
                self.inp_pcs.setValue(r[2] or 0); self.inp_w.setValue(float(r[3] or 0)); self.inp_desc.setText(r[4] or "")
                self.shipper_block.set_data({"name": r[5], "account": r[6], "address": r[7], "city": r[8], "zip": r[9], "state": r[10], "country": r[11], "phone": r[12], "email": r[13]})
                self.consignee_block.set_data({"name": r[14], "account": r[15], "address": r[16], "city": r[17], "zip": r[18], "state": r[19], "country": r[20], "phone": r[21], "email": r[22]})
                self.combo_pp_cc.setCurrentText(r[23] or "PP"); self.inp_curr.setText(r[24] or "USD")
                self.inp_rate.setValue(float(r[25] or 0)); self.inp_total.setValue(float(r[26] or 0)); self.txt_other.setText(r[27] or "")
                
                self.table_dims.setRowCount(0)
                if r[28]:
                    try:
                        for d in json.loads(r[28]):
                            row = self.table_dims.rowCount(); self.table_dims.insertRow(row)
                            self.table_dims.setItem(row, 0, QTableWidgetItem(str(d.get('pcs','0'))))
                            self.table_dims.setItem(row, 1, QTableWidgetItem(str(d.get('l','0'))))
                            self.table_dims.setItem(row, 2, QTableWidgetItem(str(d.get('w','0'))))
                            self.table_dims.setItem(row, 3, QTableWidgetItem(str(d.get('h','0'))))
                            self.table_dims.setItem(row, 4, QTableWidgetItem(str(d.get('vol','0'))))
                        self.calc_totals()
                    except: pass
            self.load_hawbs()
        except: pass

    def save_data(self):
        if not self.current_master_id: return
        s = self.shipper_block.get_data(); c = self.consignee_block.get_data()
        dims = []
        for r in range(self.table_dims.rowCount()):
            try: dims.append({"pcs": self.table_dims.item(r,0).text(), "l": self.table_dims.item(r,1).text(), "w": self.table_dims.item(r,2).text(), "h": self.table_dims.item(r,3).text(), "vol": self.table_dims.item(r,4).text()})
            except: pass
        try:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("""UPDATE masters SET
                    origin=%s, destination=%s, total_pieces=%s, weight_kg=%s, nature_of_goods=%s,
                    shipper_name=%s, sh_account=%s, shipper_address=%s, sh_city=%s, sh_zip=%s, sh_state=%s, sh_country=%s, sh_phone=%s, sh_email=%s,
                    consignee_name=%s, cn_account=%s, consignee_address=%s, cn_city=%s, cn_zip=%s, cn_state=%s, cn_country=%s, cn_phone=%s, cn_email=%s,
                    payment_mode=%s, currency=%s, freight_rate=%s, freight_total=%s, other_charges=%s, dimensions_data=%s
                WHERE id=%s""", (
                self.inp_org.text().upper(), self.inp_dst.text().upper(), self.inp_pcs.value(), self.inp_w.value(), self.inp_desc.text().upper(),
                s['name'], s['account'], s['address'], s['city'], s['zip'], s['state'], s['country'], s['phone'], s['email'],
                c['name'], c['account'], c['address'], c['city'], c['zip'], c['state'], c['country'], c['phone'], c['email'],
                self.combo_pp_cc.currentText(), self.inp_curr.text(), self.inp_rate.value(), self.inp_total.value(), self.txt_other.toPlainText(),
                json.dumps(dims), self.current_master_id))
            conn.commit(); conn.close(); QMessageBox.information(self, "Guardado", "Datos actualizados.")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def clear_fields(self):
        self.inp_org.clear(); self.inp_dst.clear(); self.inp_pcs.setValue(0); self.inp_w.setValue(0); self.inp_desc.clear()
        self.shipper_block.clear_data(); self.consignee_block.clear_data()
        self.table_dims.setRowCount(0); self.inp_rate.setValue(0); self.inp_total.setValue(0); self.txt_other.clear()

    def load_hawbs(self):
        self.table_hawbs.setRowCount(0)
        try:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT hawb_number, pieces, weight_gross FROM houses WHERE master_id=%s", (self.current_master_id,))
            for i, r in enumerate(cur.fetchall()):
                self.table_hawbs.insertRow(i)
                self.table_hawbs.setItem(i,0,QTableWidgetItem(r[0])); self.table_hawbs.setItem(i,1,QTableWidgetItem(str(r[1]))); self.table_hawbs.setItem(i,2,QTableWidgetItem(str(r[2] or 0)))
            conn.close()
        except: pass

    def add_dim_row(self):
        r = self.table_dims.rowCount(); self.table_dims.insertRow(r)
        for i in range(5): self.table_dims.setItem(r,i,QTableWidgetItem("0"))
    
    def del_dim_row(self):
        r = self.table_dims.currentRow()
        if r>=0: self.table_dims.removeRow(r); self.calc_totals()

    def calc_row_vol(self, item):
        if item.column()==4: return
        r = item.row()
        try:
            p=float(self.table_dims.item(r,0).text()); l=float(self.table_dims.item(r,1).text())
            w=float(self.table_dims.item(r,2).text()); h=float(self.table_dims.item(r,3).text())
            div = 1000000 if self.combo_unit.currentText()=="CM" else 61024
            vol = (l*w*h*p)/div
            self.table_dims.blockSignals(True); self.table_dims.setItem(r,4,QTableWidgetItem(f"{vol:.3f}")); self.table_dims.blockSignals(False)
            self.calc_totals()
        except: pass

    def calc_totals(self):
        tot_vol = 0
        for r in range(self.table_dims.rowCount()):
            try: tot_vol += float(self.table_dims.item(r,4).text())
            except: pass
        cw = max(self.inp_w.value(), tot_vol * 166.67)
        self.lbl_vol.setText(f"Vol: {tot_vol:.3f} m³"); self.lbl_chg.setText(f"Peso Cobrable: {cw:.2f} kg")
        self.inp_total.setValue(cw * self.inp_rate.value())