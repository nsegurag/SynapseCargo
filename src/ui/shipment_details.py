import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QDoubleSpinBox, QFormLayout, 
    QGroupBox, QComboBox, QMessageBox, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame, QMenu, QAbstractSpinBox, QDateEdit, QSplitter, QGridLayout
)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QColor, QFont, QAction, QCursor
from src.utils import get_db_connection

# ================= LISTA IATA COMPLETA =================
IATA_CHARGES = [
    "AW - CARGO FIJO", "CH - CLEARANCE/HANDLING", "DC - CORTE DE GUIA",
    "DG - DANGEROUS GOODS FEE", "DI - HIELO SECO INT", "FB - CERTIFICACION",
    "FL - SHC EXPRESS", "HD - PHARM HANDLING", "MA - DUE AGENT",
    "MC - OP TERRESTRE", "MO - DUE CARRIER", "MR - TC INTERNACIONAL",
    "MS - OVER COMMISSION", "MY - FUEL SURCHARGE", "MZ - OTRO",
    "OZ - PERISHABLE", "PK - FLEJE EMPAQUE", "RA - DANGEROUS GOODS",
    "SC - SECURITY", "SR - ALMACENAJE", "TE - TERMINAL INT",
    "TK - TRUCKING", "TL - HIGH VALUE", "TN - CHARGE",
    "TQ - AVI", "TR - DANGEROUS GOOD", "TT - DG DOMESTICO",
    "TV - IVA CENTROAMERICANO", "UA - COBRO AUTORIDAD"
]

# ================= ESTILOS FLUENT =================
STYLESHEET = """
    QDialog { background-color: #F3F3F3; font-family: 'Segoe UI'; font-size: 12px; }
    
    /* INPUTS */
    QLineEdit, QTextEdit, QDoubleSpinBox, QDateEdit, QComboBox {
        background-color: white; border: 1px solid #D1D1D1; border-radius: 4px; padding: 5px 8px; color: #333;
    }
    QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus {
        border: 1px solid #0067C0; background-color: #FFFFFF;
    }
    /* Sin flechas en Spinbox */
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button, QDateEdit::up-button, QDateEdit::down-button {
        width: 0px; border: none;
    }

    /* TARJETAS */
    QGroupBox {
        background-color: white; border: 1px solid #E0E0E0; border-radius: 6px;
        margin-top: 10px; padding-top: 15px; font-weight: 700; color: #0067C0;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }

    /* TABLAS */
    QTableWidget {
        background-color: white; border: 1px solid #CCC; border-radius: 4px; gridline-color: #EEE;
        selection-background-color: #E3F2FD; selection-color: #0067C0;
    }
    QHeaderView::section {
        background-color: #F8F8F8; border: none; border-bottom: 1px solid #CCC; padding: 4px; font-weight: bold; color: #555;
    }
    
    /* TABS */
    QTabWidget::pane { border: 1px solid #DDD; background: white; border-radius: 6px; }
    QTabBar::tab {
        background: #E5E5E5; color: #666; padding: 8px 15px;
        border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-weight: 600;
    }
    QTabBar::tab:selected { background: white; color: #0067C0; border-top: 3px solid #0067C0; }
"""

BTN_BLUE = "QPushButton { background-color: #0067C0; color: white; border-radius: 4px; font-weight: bold; padding: 6px 15px; border:none;} QPushButton:hover { background-color: #005a9e; }"
BTN_GREEN = "QPushButton { background-color: #107C10; color: white; border-radius: 4px; font-weight: bold; padding: 6px 15px; border:none;} QPushButton:hover { background-color: #0b5a0b; }"
BTN_WHITE = "QPushButton { background-color: white; border: 1px solid #CCC; border-radius: 4px; color: #333; font-weight: 600; padding: 6px 15px; } QPushButton:hover { background-color: #F5F5F5; }"

class CleanSpinBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setRange(0, 999999.99); self.setGroupSeparatorShown(True)

# --- BLOQUE DIRECCIÓN REDISEÑADO (PROFESIONAL) ---
class AddressBlock(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        # Usamos Grid Layout para alineación perfecta y compacta
        grid = QGridLayout(self)
        grid.setSpacing(8)
        grid.setContentsMargins(15, 25, 15, 15) # Top margin para el título
        
        lbl_style = "color:#555; font-size:11px; font-weight:normal;"

        # --- FILA 1: NOMBRE (2 Líneas) ---
        self.name = QTextEdit()
        self.name.setPlaceholderText("Nombre de la Empresa o Persona")
        self.name.setFixedHeight(45) # Altura exacta para 2 líneas
        grid.addWidget(QLabel("Nombre / Razón Social:", styleSheet=lbl_style), 0, 0, 1, 3)
        grid.addWidget(self.name, 1, 0, 1, 3) # Ocupa todo el ancho

        # --- FILA 2: DIRECCIÓN (3 Líneas) ---
        self.address = QTextEdit()
        self.address.setPlaceholderText("Calle, Número, Colonia, Edificio...")
        self.address.setFixedHeight(65) # Altura exacta para 3 líneas
        grid.addWidget(QLabel("Dirección Completa:", styleSheet=lbl_style), 2, 0, 1, 3)
        grid.addWidget(self.address, 3, 0, 1, 3) # Ocupa todo el ancho

        # --- FILA 3: GEOGRAFÍA ---
        self.city = QLineEdit(); self.city.setPlaceholderText("Ciudad")
        self.state = QLineEdit(); self.state.setPlaceholderText("Estado/Prov")
        self.country = QLineEdit(); self.country.setPlaceholderText("País"); self.country.setFixedWidth(50)
        
        grid.addWidget(QLabel("Ciudad:", styleSheet=lbl_style), 4, 0)
        grid.addWidget(self.city, 5, 0)
        
        grid.addWidget(QLabel("Estado:", styleSheet=lbl_style), 4, 1)
        grid.addWidget(self.state, 5, 1)
        
        grid.addWidget(QLabel("País:", styleSheet=lbl_style), 4, 2)
        grid.addWidget(self.country, 5, 2)

        # --- FILA 4: CONTACTO Y CUENTA ---
        self.zip = QLineEdit(); self.zip.setPlaceholderText("ZIP/CP"); self.zip.setFixedWidth(70)
        self.phone = QLineEdit(); self.phone.setPlaceholderText("Teléfono")
        self.account = QLineEdit(); self.account.setPlaceholderText("No. Cuenta")

        # Layout interno para la última fila
        h_last = QHBoxLayout()
        h_last.setSpacing(8)
        h_last.addWidget(self.zip); h_last.addWidget(self.phone); h_last.addWidget(self.account)
        
        grid.addWidget(QLabel("ZIP - Teléfono - Cuenta:", styleSheet=lbl_style), 6, 0, 1, 3)
        grid.addLayout(h_last, 7, 0, 1, 3)

        self.email = QLineEdit(); self.email.setPlaceholderText("Email de Contacto")
        grid.addWidget(QLabel("Email:", styleSheet=lbl_style), 8, 0, 1, 3)
        grid.addWidget(self.email, 9, 0, 1, 3)

    def get_data(self):
        return { "name": self.name.toPlainText(), "account": self.account.text(), "address": self.address.toPlainText(), "city": self.city.text(), "zip": self.zip.text(), "state": self.state.text(), "country": self.country.text(), "phone": self.phone.text(), "email": self.email.text() }
    def set_data(self, d):
        self.name.setText(d.get("name","")); self.account.setText(d.get("account","")); self.address.setText(d.get("address","")); self.city.setText(d.get("city","")); self.zip.setText(d.get("zip","")); self.state.setText(d.get("state","")); self.country.setText(d.get("country","")); self.phone.setText(d.get("phone","")); self.email.setText(d.get("email",""))

class ShipmentDetailsDialog(QDialog):
    def __init__(self, shipment_id, shipment_num, is_house=False, parent=None):
        super().__init__(parent)
        self.sid = shipment_id; self.snum = shipment_num; self.is_house = is_house
        self.table_name = "houses" if is_house else "masters"
        self.setWindowTitle(f"Gestión de Embarque - {self.snum}")
        self.resize(1000, 700)
        self.setStyleSheet(STYLESHEET)

        main = QVBoxLayout(self); main.setContentsMargins(15, 10, 15, 15); main.setSpacing(10)

        # Header
        h_layout = QHBoxLayout()
        title = QLabel(f"{'HAWB' if is_house else 'MAWB'} {self.snum}"); title.setStyleSheet("font-size: 18px; font-weight: 800; color: #222;")
        h_layout.addWidget(QLabel("✈️", styleSheet="font-size:20px")); h_layout.addWidget(title); h_layout.addStretch()
        main.addLayout(h_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_ops = QWidget(); self.tab_dims = QWidget(); self.tab_parties = QWidget(); self.tab_rates = QWidget(); self.tab_hawbs = QWidget()
        
        self.setup_ops_tab(); self.setup_dims_tab(); self.setup_parties_tab(); self.setup_rates_tab()
        if not self.is_house: self.setup_hawbs_tab()

        self.tabs.addTab(self.tab_ops, "Datos y Itinerarios")
        self.tabs.addTab(self.tab_dims, "Medidas y Pesos")
        self.tabs.addTab(self.tab_parties, "Shipper & Consignee")
        self.tabs.addTab(self.tab_rates, "Tarifas")
        if not self.is_house: self.tabs.addTab(self.tab_hawbs, "Hijas")
        
        main.addWidget(self.tabs)

        # Footer
        btns = QHBoxLayout()
        b_cancel = QPushButton("Cancelar"); b_cancel.setStyleSheet(BTN_WHITE); b_cancel.setCursor(Qt.CursorShape.PointingHandCursor); b_cancel.clicked.connect(self.reject)
        b_save = QPushButton("💾 Guardar Todo"); b_save.setStyleSheet(BTN_BLUE); b_save.setCursor(Qt.CursorShape.PointingHandCursor); b_save.clicked.connect(self.save_all)
        btns.addStretch(); btns.addWidget(b_cancel); btns.addWidget(b_save)
        main.addLayout(btns)
        self.load_data()

    # ================= 1. DATOS Y ITINERARIOS =================
    def setup_ops_tab(self):
        layout = QVBoxLayout(self.tab_ops); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(15)

        gb_main = QGroupBox("Información de Ruta y Carga")
        l_main = QVBoxLayout(gb_main)
        
        row1 = QHBoxLayout()
        self.inp_org = QLineEdit(); self.inp_org.setPlaceholderText("ORIG"); self.inp_org.setFixedWidth(70); self.inp_org.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.inp_dst = QLineEdit(); self.inp_dst.setPlaceholderText("DEST"); self.inp_dst.setFixedWidth(70); self.inp_dst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row1.addWidget(QLabel("Ruta:")); row1.addWidget(self.inp_org); row1.addWidget(QLabel("✈")); row1.addWidget(self.inp_dst)
        row1.addSpacing(50)
        self.inp_pcs = CleanSpinBox(); self.inp_pcs.setDecimals(0); self.inp_pcs.setSuffix(" pcs")
        self.inp_w = CleanSpinBox(); self.inp_w.setSuffix(" kg")
        self.inp_v_display = QLineEdit(); self.inp_v_display.setReadOnly(True); self.inp_v_display.setPlaceholderText("Calc. en Medidas")
        row1.addWidget(QLabel("Piezas:")); row1.addWidget(self.inp_pcs); row1.addWidget(QLabel("Peso Bruto:")); row1.addWidget(self.inp_w); row1.addWidget(QLabel("Volumen:")); row1.addWidget(self.inp_v_display)
        l_main.addLayout(row1)
        self.inp_desc = QLineEdit(); self.inp_desc.setPlaceholderText("Descripción de la mercancía (Ej: CONSOLIDATED CARGO)")
        l_main.addWidget(self.inp_desc)
        layout.addWidget(gb_main)

        gb_itin = QGroupBox("Itinerario de Vuelo")
        l_itin = QVBoxLayout(gb_itin)
        self.table_itin = QTableWidget(0, 7)
        self.table_itin.setHorizontalHeaderLabels(["Aerolínea", "Vuelo", "Fecha", "Origen", "Destino", "Piezas", "Peso"])
        self.table_itin.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_itin.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_itin.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_itin.customContextMenuRequested.connect(self.itin_menu)
        l_itin.addWidget(self.table_itin)
        l_itin.addWidget(QLabel("💡 Click derecho para agregar/eliminar vuelos.", styleSheet="color:#888; font-size:11px;"))
        layout.addWidget(gb_itin)

    def itin_menu(self, pos):
        m = QMenu(); m.addAction("➕ Agregar Vuelo", self.add_itin_row); m.addAction("🗑️ Eliminar Vuelo", self.del_itin_row); m.exec(QCursor.pos())
    def add_itin_row(self):
        r = self.table_itin.rowCount(); self.table_itin.insertRow(r)
        self.table_itin.setCellWidget(r, 2, QDateEdit(QDate.currentDate()))
    def del_itin_row(self):
        r = self.table_itin.currentRow(); 
        if r>=0: self.table_itin.removeRow(r)

    # ================= 2. MEDIDAS Y PESOS =================
    def setup_dims_tab(self):
        layout = QVBoxLayout(self.tab_dims); layout.setContentsMargins(15, 15, 15, 15)
        gb = QGroupBox("Dimensiones Físicas"); l = QVBoxLayout(gb)
        self.table_dims = QTableWidget(0, 6)
        self.table_dims.setHorizontalHeaderLabels(["Piezas", "Largo", "Ancho", "Alto", "Unidad", "Vol m³"])
        self.table_dims.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_dims.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_dims.customContextMenuRequested.connect(self.dims_menu)
        self.table_dims.itemChanged.connect(self.calc_row_vol)
        l.addWidget(self.table_dims)
        h_res = QHBoxLayout()
        self.lbl_total_vol = QLabel("Volumen Total: 0.000 m³")
        self.lbl_vol_w = QLabel("Peso Volumétrico: 0.00 kg"); self.lbl_vol_w.setStyleSheet("font-size: 16px; font-weight: bold; color: #D32F2F;")
        h_res.addWidget(QLabel("💡 Click derecho para gestionar líneas.")); h_res.addStretch()
        h_res.addWidget(self.lbl_total_vol); h_res.addSpacing(20); h_res.addWidget(self.lbl_vol_w)
        l.addLayout(h_res); layout.addWidget(gb)

    def dims_menu(self, pos):
        m = QMenu(); m.addAction("➕ Agregar Medida", self.add_dim_row); m.addAction("🗑️ Eliminar Medida", self.del_dim_row); m.exec(QCursor.pos())
    def add_dim_row(self):
        r = self.table_dims.rowCount(); self.table_dims.insertRow(r)
        for i in range(4): self.table_dims.setItem(r, i, QTableWidgetItem("0"))
        cb = QComboBox(); cb.addItems(["CM","INCH"]); cb.currentIndexChanged.connect(lambda: self.calc_row_vol(self.table_dims.item(r,0)))
        self.table_dims.setCellWidget(r, 4, cb); self.table_dims.setItem(r, 5, QTableWidgetItem("0.000"))
    def del_dim_row(self):
        r = self.table_dims.currentRow(); 
        if r>=0: self.table_dims.removeRow(r); self.recalc_totals()
    def calc_row_vol(self, item):
        if not item or item.column()==5: return
        r = item.row()
        try:
            p=float(self.table_dims.item(r,0).text()); l=float(self.table_dims.item(r,1).text())
            w=float(self.table_dims.item(r,2).text()); h=float(self.table_dims.item(r,3).text())
            u = self.table_dims.cellWidget(r,4).currentText()
            div = 1000000 if u=="CM" else 61024
            vol = (l*w*h*p)/div
            self.table_dims.blockSignals(True); self.table_dims.setItem(r,5,QTableWidgetItem(f"{vol:.3f}")); self.table_dims.blockSignals(False)
            self.recalc_totals()
        except: pass
    def recalc_totals(self):
        tv = 0.0
        for r in range(self.table_dims.rowCount()):
            try: tv += float(self.table_dims.item(r,5).text())
            except: pass
        self.inp_v_display.setText(f"{tv:.3f} m³"); self.lbl_total_vol.setText(f"Volumen Total: {tv:.3f} m³")
        vol_w_kg = tv * 166.667; self.lbl_vol_w.setText(f"Peso Volumétrico: {vol_w_kg:.2f} kg")

    # ================= 3. SHIPPER & CONSIGNEE =================
    def setup_parties_tab(self):
        layout = QHBoxLayout(self.tab_parties); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(20)
        self.ship_block = AddressBlock("Shipper (Remitente)"); self.cons_block = AddressBlock("Consignee (Destinatario)")
        layout.addWidget(self.ship_block); layout.addWidget(self.cons_block)

    # ================= 4. TARIFAS (AUTO-RATING) =================
    def setup_rates_tab(self):
        layout = QVBoxLayout(self.tab_rates); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(15)
        gb_info = QGroupBox("Datos Financieros"); f = QFormLayout(gb_info); f.setSpacing(15)
        self.combo_pay = QComboBox(); self.combo_pay.addItems(["PP (Prepaid)", "CC (Collect)"]); self.inp_curr = QLineEdit("USD")
        self.inp_rate = CleanSpinBox(); self.inp_rate.setPrefix("$ "); self.inp_total_freight = CleanSpinBox(); self.inp_total_freight.setPrefix("$ ")
        btn_autorate = QPushButton("⚡ Generar Rating Automático"); btn_autorate.setStyleSheet(BTN_GREEN); btn_autorate.setCursor(Qt.CursorShape.PointingHandCursor); btn_autorate.clicked.connect(self.generate_auto_rating)
        r1 = QHBoxLayout(); r1.addWidget(QLabel("Modo Pago:")); r1.addWidget(self.combo_pay); r1.addWidget(QLabel("Moneda:")); r1.addWidget(self.inp_curr)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("Rate / Kg:")); r2.addWidget(self.inp_rate); r2.addWidget(QLabel("Total Flete:")); r2.addWidget(self.inp_total_freight)
        f.addRow(r1); f.addRow(r2); f.addRow(btn_autorate); layout.addWidget(gb_info)

        gb_charges = QGroupBox("Otros Cargos"); v = QVBoxLayout(gb_charges)
        self.table_charges = QTableWidget(0, 3); self.table_charges.setHorizontalHeaderLabels(["Concepto", "Monto", "Tipo"])
        self.table_charges.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_charges.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_charges.customContextMenuRequested.connect(self.charges_menu)
        v.addWidget(self.table_charges); v.addWidget(QLabel("💡 Click derecho para agregar cargos.", styleSheet="color:#888; font-size:11px; margin-top:5px;"))
        layout.addWidget(gb_charges)

    def generate_auto_rating(self):
        tv = 0.0
        for r in range(self.table_dims.rowCount()):
            try: tv += float(self.table_dims.item(r,5).text())
            except: pass
        vol_w = tv * 166.667; gross_w = self.inp_w.value()
        chg_w = max(gross_w, vol_w)
        if chg_w <= 0: QMessageBox.warning(self, "Aviso", "No hay peso calculado."); return
        rate = self.inp_rate.value(); freight = chg_w * rate; self.inp_total_freight.setValue(freight)
        
        # GENERAR CARGOS
        self.table_charges.setRowCount(0)
        self.add_charge_row_val("MY - FUEL SURCHARGE", chg_w * 0.15, "PP")
        self.add_charge_row_val("SC - SECURITY", gross_w * 0.10, "PP")
        self.add_charge_row_val("AW - CARGO FIJO", 50.00, "PP")
        self.add_charge_row_val("UA - COBRO AUTORIDAD", 20.00, "PP") # <--- NUEVO
        
        QMessageBox.information(self, "Rating Generado", f"Calculado sobre Peso Cobrable: {chg_w:.2f} kg")

    def add_charge_row_val(self, code, amount, ctype):
        r = self.table_charges.rowCount(); self.table_charges.insertRow(r)
        cb = QComboBox(); cb.addItems(IATA_CHARGES); cb.setCurrentText(code); self.table_charges.setCellWidget(r, 0, cb)
        sp = CleanSpinBox(); sp.setPrefix("$ "); sp.setValue(amount); self.table_charges.setCellWidget(r, 1, sp)
        ct = QComboBox(); ct.addItems(["PP", "CC"]); ct.setCurrentText(ctype); self.table_charges.setCellWidget(r, 2, ct)

    def charges_menu(self, pos):
        m = QMenu(); m.addAction("➕ Agregar Cargo", self.add_charge); m.addAction("🗑️ Eliminar Cargo", self.del_charge); m.exec(QCursor.pos())
    def add_charge(self):
        self.add_charge_row_val(IATA_CHARGES[0], 0.0, "PP")
    def del_charge(self):
        r = self.table_charges.currentRow(); 
        if r>=0: self.table_charges.removeRow(r)

    # ================= 5. HIJAS =================
    def setup_hawbs_tab(self):
        layout = QVBoxLayout(self.tab_hawbs); layout.setContentsMargins(15,15,15,15)
        self.table_hawbs = QTableWidget(0, 3); self.table_hawbs.setHorizontalHeaderLabels(["HAWB", "Pcs", "Kg"])
        self.table_hawbs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_hawbs)

    # ================= CARGA/GUARDADO =================
    def load_data(self):
        try:
            conn = get_db_connection(); cur = conn.cursor()
            q = f"""SELECT shipper_name, sh_account, shipper_address, sh_city, sh_zip, sh_state, sh_country, sh_phone, sh_email,
                    consignee_name, cn_account, consignee_address, cn_city, cn_zip, cn_state, cn_country, cn_phone, cn_email,
                    {'weight_kg' if not self.is_house else 'weight_gross'}, 
                    {'total_pieces' if not self.is_house else 'pieces'},
                    {'nature_of_goods' if not self.is_house else 'description'},
                    origin, destination, itinerary_data, dimensions_data, payment_mode, 
                    {'currency, freight_rate, freight_total, other_charges' if not self.is_house else "'USD', 0, 0, ''"}
                    FROM {self.table_name} WHERE id=%s"""
            cur.execute(q, (self.sid,)); r = cur.fetchone(); conn.close()

            if r:
                self.ship_block.set_data({"name":r[0],"account":r[1],"address":r[2],"city":r[3],"zip":r[4],"state":r[5],"country":r[6],"phone":r[7],"email":r[8]})
                self.cons_block.set_data({"name":r[9],"account":r[10],"address":r[11],"city":r[12],"zip":r[13],"state":r[14],"country":r[15],"phone":r[16],"email":r[17]})
                self.inp_w.setValue(float(r[18] or 0)); self.inp_pcs.setValue(r[19] or 0); self.inp_desc.setText(r[20] or "")
                self.inp_org.setText(r[21] or ""); self.inp_dst.setText(r[22] or "")
                
                if r[23]:
                    try:
                        for i in json.loads(r[23]):
                            x = self.table_itin.rowCount(); self.table_itin.insertRow(x)
                            self.table_itin.setItem(x,0,QTableWidgetItem(i.get('air','')))
                            self.table_itin.setItem(x,1,QTableWidgetItem(i.get('flt','')))
                            de = QDateEdit(); de.setDate(QDate.fromString(i.get('date',''), "yyyy-MM-dd")); self.table_itin.setCellWidget(x,2,de)
                            self.table_itin.setItem(x,3,QTableWidgetItem(i.get('org','')))
                            self.table_itin.setItem(x,4,QTableWidgetItem(i.get('dst','')))
                            self.table_itin.setItem(x,5,QTableWidgetItem(i.get('pcs','')))
                            self.table_itin.setItem(x,6,QTableWidgetItem(i.get('wgt',''))) 
                    except: pass

                if r[24]:
                    try:
                        for d in json.loads(r[24]):
                            x = self.table_dims.rowCount(); self.table_dims.insertRow(x)
                            self.table_dims.setItem(x,0,QTableWidgetItem(str(d.get('pcs',0))))
                            self.table_dims.setItem(x,1,QTableWidgetItem(str(d.get('l',0))))
                            self.table_dims.setItem(x,2,QTableWidgetItem(str(d.get('w',0))))
                            self.table_dims.setItem(x,3,QTableWidgetItem(str(d.get('h',0))))
                            cb = QComboBox(); cb.addItems(["CM","INCH"]); cb.setCurrentText(d.get('u','CM')); 
                            cb.currentIndexChanged.connect(lambda: self.calc_row_vol(self.table_dims.item(x,0)))
                            self.table_dims.setCellWidget(x,4,cb); self.table_dims.setItem(x,5,QTableWidgetItem(str(d.get('vol',0))))
                        self.recalc_totals()
                    except: pass

                self.combo_pay.setCurrentText("PP (Prepaid)" if r[25]=="PP" else "CC (Collect)")
                self.inp_curr.setText(r[26] or "USD"); self.inp_rate.setValue(float(r[27] or 0)); self.inp_total_freight.setValue(float(r[28] or 0))

                if r[29]: 
                    try:
                        for c in json.loads(r[29]):
                            x = self.table_charges.rowCount(); self.table_charges.insertRow(x)
                            cb = QComboBox(); cb.addItems(IATA_CHARGES); cb.setCurrentText(c.get('code','')); self.table_charges.setCellWidget(x,0,cb)
                            sp = CleanSpinBox(); sp.setPrefix("$ "); sp.setValue(float(c.get('amt',0))); self.table_charges.setCellWidget(x,1,sp)
                            ct = QComboBox(); ct.addItems(["PP","CC"]); ct.setCurrentText(c.get('type','PP')); self.table_charges.setCellWidget(x,2,ct)
                    except: pass
            
            if not self.is_house: self.load_hawbs()
        except Exception as e: print(f"Error: {e}")

    def load_hawbs(self):
        try:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT hawb_number, pieces, weight_gross FROM houses WHERE master_id=%s", (self.sid,))
            for i, r in enumerate(cur.fetchall()):
                self.table_hawbs.insertRow(i)
                self.table_hawbs.setItem(i,0,QTableWidgetItem(r[0])); self.table_hawbs.setItem(i,1,QTableWidgetItem(str(r[1]))); self.table_hawbs.setItem(i,2,QTableWidgetItem(str(r[2])))
            conn.close()
        except: pass

    def save_all(self):
        s = self.ship_block.get_data(); c = self.cons_block.get_data()
        
        itin = []
        for r in range(self.table_itin.rowCount()):
            try: itin.append({
                "air":self.table_itin.item(r,0).text(), "flt":self.table_itin.item(r,1).text(),
                "date":self.table_itin.cellWidget(r,2).date().toString("yyyy-MM-dd"),
                "org":self.table_itin.item(r,3).text(), "dst":self.table_itin.item(r,4).text(),
                "pcs":self.table_itin.item(r,5).text(), "wgt":self.table_itin.item(r,6).text()
            })
            except: pass
            
        dims = []
        for r in range(self.table_dims.rowCount()):
            try: dims.append({"pcs":self.table_dims.item(r,0).text(),"l":self.table_dims.item(r,1).text(),"w":self.table_dims.item(r,2).text(),"h":self.table_dims.item(r,3).text(),"u":self.table_dims.cellWidget(r,4).currentText(),"vol":self.table_dims.item(r,5).text()})
            except: pass

        charges = []
        for r in range(self.table_charges.rowCount()):
            try: charges.append({"code":self.table_charges.cellWidget(r,0).currentText(),"amt":self.table_charges.cellWidget(r,1).value(),"type":self.table_charges.cellWidget(r,2).currentText()})
            except: pass

        try:
            conn = get_db_connection(); cur = conn.cursor()
            base_q = f"UPDATE {self.table_name} SET shipper_name=%s, sh_account=%s, shipper_address=%s, sh_city=%s, sh_zip=%s, sh_state=%s, sh_country=%s, sh_phone=%s, sh_email=%s, consignee_name=%s, cn_account=%s, consignee_address=%s, cn_city=%s, cn_zip=%s, cn_state=%s, cn_country=%s, cn_phone=%s, cn_email=%s, payment_mode=%s, origin=%s, destination=%s, itinerary_data=%s, dimensions_data=%s"
            args = [s['name'], s['account'], s['address'], s['city'], s['zip'], s['state'], s['country'], s['phone'], s['email'], c['name'], c['account'], c['address'], c['city'], c['zip'], c['state'], c['country'], c['phone'], c['email'], "PP" if "PP" in self.combo_pay.currentText() else "CC", self.inp_org.text().upper(), self.inp_dst.text().upper(), json.dumps(itin), json.dumps(dims)]

            if not self.is_house:
                base_q += ", weight_kg=%s, total_pieces=%s, nature_of_goods=%s, currency=%s, freight_rate=%s, freight_total=%s, other_charges=%s WHERE id=%s"
                args.extend([self.inp_w.value(), self.inp_pcs.value(), self.inp_desc.text().upper(), self.inp_curr.text(), self.inp_rate.value(), self.inp_total_freight.value(), json.dumps(charges), self.sid])
            else:
                base_q += ", weight_gross=%s, pieces=%s, description=%s WHERE id=%s"
                args.extend([self.inp_w.value(), self.inp_pcs.value(), self.inp_desc.text().upper(), self.sid])

            cur.execute(base_q, tuple(args)); conn.commit(); conn.close()
            QMessageBox.information(self, "Guardado", "Datos actualizados correctamente."); self.accept()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))