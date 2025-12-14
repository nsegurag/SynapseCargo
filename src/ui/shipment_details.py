import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QDoubleSpinBox, QFormLayout, 
    QGroupBox, QComboBox, QMessageBox, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont
from src.utils import get_db_connection

# ================= ESTILOS WINDOWS 11 FLUENT =================
STYLESHEET = """
    QDialog { background-color: #F3F3F3; font-family: 'Segoe UI'; }
    
    /* --- TARJETAS (CARDS) --- */
    QGroupBox {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        margin-top: 10px;
        font-weight: bold;
        color: #0067C0;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }

    /* --- INPUTS --- */
    QLineEdit, QTextEdit, QDoubleSpinBox, QComboBox {
        background-color: #FFFFFF;
        border: 1px solid #D1D1D1;
        border-bottom: 2px solid #D1D1D1; /* Estilo Win11 */
        border-radius: 4px;
        padding: 6px;
        color: #333;
        selection-background-color: #0067C0;
    }
    QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {
        border-bottom: 2px solid #0067C0;
        background-color: #FAFAFA;
    }

    /* --- TABS --- */
    QTabWidget::pane { border: none; }
    QTabBar::tab {
        background: transparent;
        color: #666;
        padding: 10px 20px;
        border-bottom: 2px solid transparent;
        font-weight: 600;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        color: #0067C0;
        border-bottom: 2px solid #0067C0;
    }
    QTabBar::tab:hover { background-color: #EAEAEA; border-radius: 4px; }

    /* --- TABLAS --- */
    QTableWidget {
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        gridline-color: #F0F0F0;
    }
    QHeaderView::section {
        background-color: #FAFAFA;
        border: none;
        border-bottom: 1px solid #E0E0E0;
        padding: 6px;
        font-weight: bold;
        color: #555;
    }
"""

BTN_BLUE = """
    QPushButton { background-color: #0067C0; color: white; border-radius: 5px; font-weight: bold; padding: 8px 16px; border: 1px solid #005a9e; }
    QPushButton:hover { background-color: #005a9e; }
"""
BTN_WHITE = """
    QPushButton { background-color: white; border: 1px solid #CCC; border-radius: 5px; color: #333; font-weight: 600; padding: 8px 16px; }
    QPushButton:hover { background-color: #F9F9F9; border-color: #999; }
"""

class AddressBlock(QGroupBox):
    """Componente reutilizable para Shipper y Consignee"""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        self.name = QLineEdit(); self.name.setPlaceholderText("Nombre Completo / Razón Social")
        self.account = QLineEdit(); self.account.setPlaceholderText("Account No.")
        self.address = QTextEdit(); self.address.setMaximumHeight(60); self.address.setPlaceholderText("Calle, Número, Edificio...")
        
        row1 = QHBoxLayout()
        self.city = QLineEdit(); self.city.setPlaceholderText("Ciudad")
        self.zip = QLineEdit(); self.zip.setPlaceholderText("Zip / CP")
        self.zip.setFixedWidth(100)
        row1.addWidget(self.city); row1.addWidget(self.zip)
        
        row2 = QHBoxLayout()
        self.state = QLineEdit(); self.state.setPlaceholderText("Estado / Prov")
        self.country = QLineEdit(); self.country.setPlaceholderText("País (ISO)")
        self.country.setFixedWidth(80)
        row2.addWidget(self.state); row2.addWidget(self.country)
        
        row3 = QHBoxLayout()
        self.phone = QLineEdit(); self.phone.setPlaceholderText("Teléfono")
        self.email = QLineEdit(); self.email.setPlaceholderText("Email de contacto")
        row3.addWidget(self.phone); row3.addWidget(self.email)

        layout.addRow("Nombre *:", self.name)
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

class ShipmentDetailsDialog(QDialog):
    def __init__(self, shipment_id, shipment_num, is_house=False, parent=None):
        super().__init__(parent)
        self.shipment_id = shipment_id
        self.shipment_num = shipment_num
        self.is_house = is_house
        self.table_name = "houses" if is_house else "masters"
        
        # Color temático
        self.accent_color = "#D83B01" if is_house else "#0078D4" # Naranja para House, Azul para Master
        type_label = "HAWB (Hija)" if is_house else "MAWB (Master)"

        self.setWindowTitle(f"Detalles de Embarque - {self.shipment_num}")
        self.resize(950, 750)
        self.setStyleSheet(STYLESHEET)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- HEADER FLUENT ---
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0,0,0,0)
        
        lbl_icon = QLabel("📦")
        lbl_icon.setStyleSheet("font-size: 32px;")
        
        lbl_info = QLabel(f"{type_label}\n{self.shipment_num}")
        lbl_info.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.accent_color};")
        
        hl.addWidget(lbl_icon)
        hl.addWidget(lbl_info)
        hl.addStretch()
        
        main_layout.addWidget(header)

        # --- TABS ---
        self.tabs = QTabWidget()
        
        self.tab_general = QWidget()
        self.tab_cargo = QWidget()
        self.tab_rates = QWidget()
        self.tab_houses = QWidget() # NUEVO: Pestaña de Hijas
        
        self.setup_general_tab()
        self.setup_cargo_tab()
        self.setup_rates_tab()
        
        self.tabs.addTab(self.tab_general, "1. Remitente y Destinatario")
        self.tabs.addTab(self.tab_cargo, "2. Carga y Dimensiones")
        self.tabs.addTab(self.tab_rates, "3. Tarifas y Contabilidad")
        
        # Solo mostramos la pestaña de Hijas si es una MASTER
        if not self.is_house:
            self.setup_houses_tab()
            self.tabs.addTab(self.tab_houses, "4. Guías Hijas (HAWBs)")

        main_layout.addWidget(self.tabs)

        # --- FOOTER ---
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 10, 0, 0)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(BTN_WHITE)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("💾  Guardar y Sincronizar")
        btn_save.setStyleSheet(BTN_BLUE)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.save_all)
        
        footer.addStretch()
        footer.addWidget(btn_cancel)
        footer.addWidget(btn_save)
        main_layout.addLayout(footer)

        self.load_data()

    def setup_general_tab(self):
        layout = QHBoxLayout(self.tab_general)
        layout.setSpacing(20)
        self.shipper_block = AddressBlock("🛫 Shipper (Remitente)")
        self.consignee_block = AddressBlock("🛬 Consignee (Destinatario)")
        layout.addWidget(self.shipper_block)
        layout.addWidget(self.consignee_block)

    def setup_cargo_tab(self):
        layout = QVBoxLayout(self.tab_cargo)
        layout.setSpacing(15)
        
        # Info básica
        gb_basic = QGroupBox("📦 Descripción Física")
        l_basic = QFormLayout(gb_basic)
        l_basic.setContentsMargins(15, 20, 15, 15)
        
        row_qty = QHBoxLayout()
        self.inp_pieces = QDoubleSpinBox(); self.inp_pieces.setRange(0, 99999); self.inp_pieces.setDecimals(0); self.inp_pieces.setSuffix(" pcs")
        self.inp_gross = QDoubleSpinBox(); self.inp_gross.setRange(0, 999999); self.inp_gross.setSuffix(" kg")
        row_qty.addWidget(QLabel("Piezas:")); row_qty.addWidget(self.inp_pieces)
        row_qty.addWidget(QLabel("Peso Bruto:")); row_qty.addWidget(self.inp_gross)
        
        self.inp_desc = QLineEdit()
        self.inp_desc.setPlaceholderText("Descripción de la mercancía (Ej: CONSOLIDATION, FRESH FLOWERS...)")
        
        l_basic.addRow("Cantidades:", row_qty)
        l_basic.addRow("Naturaleza:", self.inp_desc)
        layout.addWidget(gb_basic)

        # Dimensiones
        gb_dims = QGroupBox("📏 Calculadora Volumétrica")
        l_dims = QVBoxLayout(gb_dims)
        l_dims.setContentsMargins(15, 20, 15, 15)
        
        tools = QHBoxLayout()
        self.combo_unit = QComboBox(); self.combo_unit.addItems(["CM", "INCH"]); self.combo_unit.setFixedWidth(80)
        btn_add = QPushButton("➕ Agregar"); btn_add.setFixedWidth(80); btn_add.setStyleSheet(BTN_WHITE); btn_add.clicked.connect(self.add_dim_row)
        btn_del = QPushButton("🗑️"); btn_del.setFixedWidth(40); btn_del.setStyleSheet("color: red; border: 1px solid #CCC; background: white; border-radius: 4px;"); btn_del.clicked.connect(self.del_dim_row)
        
        tools.addWidget(QLabel("Unidad:"))
        tools.addWidget(self.combo_unit)
        tools.addWidget(btn_add)
        tools.addWidget(btn_del)
        tools.addStretch()
        l_dims.addLayout(tools)

        self.table_dims = QTableWidget(0, 5)
        self.table_dims.setHorizontalHeaderLabels(["Pcs", "Largo", "Ancho", "Alto", "Vol (m³)"])
        self.table_dims.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_dims.itemChanged.connect(self.calculate_row_volume)
        l_dims.addWidget(self.table_dims)

        # Totales Calculados
        res_layout = QHBoxLayout()
        self.lbl_vol_total = QLabel("Volumen: 0.000 m³")
        self.lbl_chg_w = QLabel("Peso Cobrable: 0.00 kg")
        self.lbl_chg_w.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.accent_color};")
        
        res_layout.addStretch()
        res_layout.addWidget(self.lbl_vol_total)
        res_layout.addSpacing(20)
        res_layout.addWidget(self.lbl_chg_w)
        l_dims.addLayout(res_layout)
        
        layout.addWidget(gb_dims)

    def setup_rates_tab(self):
        layout = QFormLayout(self.tab_rates)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        self.combo_pp_cc = QComboBox(); self.combo_pp_cc.addItems(["PP (Prepaid)", "CC (Charges Collect)"])
        self.inp_currency = QLineEdit("USD"); self.inp_currency.setFixedWidth(80)
        
        self.inp_rate = QDoubleSpinBox(); self.inp_rate.setRange(0, 99999); self.inp_rate.setPrefix("$ "); self.inp_rate.setDecimals(2)
        self.inp_rate.valueChanged.connect(self.calc_freight_total)
        
        self.inp_total_freight = QDoubleSpinBox(); self.inp_total_freight.setRange(0, 999999); self.inp_total_freight.setPrefix("$ "); self.inp_total_freight.setDecimals(2)
        
        self.txt_charges = QTextEdit(); self.txt_charges.setPlaceholderText("Otros Cargos (DUE AGENT, FSC, SSC...)")
        
        layout.addRow("Modo de Pago:", self.combo_pp_cc)
        layout.addRow("Moneda:", self.inp_currency)
        layout.addRow("Tarifa (Rate/Kg):", self.inp_rate)
        layout.addRow("Flete Total:", self.inp_total_freight)
        layout.addRow("Otros Cargos:", self.txt_charges)

    def setup_houses_tab(self):
        """Pestaña exclusiva para Masters que muestra sus HAWBs"""
        layout = QVBoxLayout(self.tab_houses)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info = QLabel("💡 Haz doble clic en una Guía Hija para editar sus detalles individuales.")
        info.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info)
        
        self.table_houses = QTableWidget()
        self.table_houses.setColumnCount(4)
        self.table_houses.setHorizontalHeaderLabels(["ID", "HAWB Number", "Piezas", "Peso (Kg)"])
        self.table_houses.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_houses.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_houses.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_houses.itemDoubleClicked.connect(self.open_sub_hawb)
        
        layout.addWidget(self.table_houses)
        
        btn_refresh = QPushButton("🔄 Recargar Lista")
        btn_refresh.setStyleSheet(BTN_WHITE)
        btn_refresh.clicked.connect(self.load_houses_list)
        layout.addWidget(btn_refresh)

    # --- LÓGICA DE CARGA DE DATOS ---
    def load_data(self):
        try:
            conn = get_db_connection(); cur = conn.cursor()
            
            # NOTA: Ajustamos las columnas según si es Master o House
            # Masters tiene 'weight_kg' y 'total_pieces'. Houses tiene 'weight_gross' y 'pieces'.
            
            if not self.is_house:
                # Carga para MASTER
                query = """
                    SELECT shipper_name, sh_account, shipper_address, sh_city, sh_zip, sh_state, sh_country, sh_phone, sh_email,
                           consignee_name, cn_account, consignee_address, cn_city, cn_zip, cn_state, cn_country, cn_phone, cn_email,
                           weight_kg, nature_of_goods, 
                           payment_mode, currency, freight_rate, freight_total, other_charges, 
                           dimensions_data, total_pieces
                    FROM masters WHERE id = %s
                """
            else:
                # Carga para HOUSE
                query = """
                    SELECT shipper_name, sh_account, shipper_address, sh_city, sh_zip, sh_state, sh_country, sh_phone, sh_email,
                           consignee_name, cn_account, consignee_address, cn_city, cn_zip, cn_state, cn_country, cn_phone, cn_email,
                           weight_gross, description, 
                           payment_mode, 'USD', 0.0, 0.0, '', 
                           dimensions_data, pieces
                    FROM houses WHERE id = %s
                """
            
            cur.execute(query, (self.shipment_id,))
            r = cur.fetchone()
            conn.close()
            
            if r:
                # Mapeo seguro (evita Nones)
                self.shipper_block.set_data({"name": r[0], "account": r[1], "address": r[2], "city": r[3], "zip": r[4], "state": r[5], "country": r[6], "phone": r[7], "email": r[8]})
                self.consignee_block.set_data({"name": r[9], "account": r[10], "address": r[11], "city": r[12], "zip": r[13], "state": r[14], "country": r[15], "phone": r[16], "email": r[17]})
                
                self.inp_gross.setValue(float(r[18] or 0))
                self.inp_desc.setText(r[19] or "")
                
                self.combo_pp_cc.setCurrentIndex(0 if r[20] == "PP" else 1)
                self.inp_currency.setText(r[21] or "USD")
                self.inp_rate.setValue(float(r[22] or 0))
                self.inp_total_freight.setValue(float(r[23] or 0))
                self.txt_charges.setText(r[24] or "")
                
                # Dimensiones
                if r[25]:
                    try:
                        dims = json.loads(r[25])
                        for d in dims:
                            row = self.table_dims.rowCount()
                            self.table_dims.insertRow(row)
                            self.table_dims.setItem(row, 0, QTableWidgetItem(str(d.get('pcs','0'))))
                            self.table_dims.setItem(row, 1, QTableWidgetItem(str(d.get('l','0'))))
                            self.table_dims.setItem(row, 2, QTableWidgetItem(str(d.get('w','0'))))
                            self.table_dims.setItem(row, 3, QTableWidgetItem(str(d.get('h','0'))))
                            self.table_dims.setItem(row, 4, QTableWidgetItem(str(d.get('vol','0'))))
                        self.recalc_totals()
                    except: pass

                self.inp_pieces.setValue(r[26] or 0)

            if not self.is_house:
                self.load_houses_list()

        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"No se pudieron cargar los datos:\n{e}")

    def load_houses_list(self):
        """Carga la lista de HAWBs en la pestaña 4"""
        self.table_houses.setRowCount(0)
        try:
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("SELECT id, hawb_number, pieces, weight_gross FROM houses WHERE master_id = %s ORDER BY id ASC", (self.shipment_id,))
            rows = cur.fetchall()
            conn.close()
            
            for i, row in enumerate(rows):
                self.table_houses.insertRow(i)
                self.table_houses.setItem(i, 0, QTableWidgetItem(str(row[0])))
                self.table_houses.setItem(i, 1, QTableWidgetItem(row[1]))
                self.table_houses.setItem(i, 2, QTableWidgetItem(str(row[2])))
                self.table_houses.setItem(i, 3, QTableWidgetItem(str(row[3] or 0)))
        except: pass

    def open_sub_hawb(self, item):
        """Abre recursivamente otra ventana para la HAWB seleccionada"""
        row = item.row()
        hid = int(self.table_houses.item(row, 0).text())
        hnum = self.table_houses.item(row, 1).text()
        
        dialog = ShipmentDetailsDialog(hid, hnum, is_house=True, parent=self)
        dialog.exec()
        self.load_houses_list() # Recargar al volver

    # --- GUARDADO ---
    def save_all(self):
        s = self.shipper_block.get_data()
        c = self.consignee_block.get_data()
        
        dims = []
        for r in range(self.table_dims.rowCount()):
            try:
                dims.append({
                    "pcs": self.table_dims.item(r,0).text(), "l": self.table_dims.item(r,1).text(),
                    "w": self.table_dims.item(r,2).text(), "h": self.table_dims.item(r,3).text(),
                    "vol": self.table_dims.item(r,4).text()
                })
            except: pass
        dims_json = json.dumps(dims)
        
        pay_mode = "PP" if self.combo_pp_cc.currentIndex() == 0 else "CC"
        
        try:
            conn = get_db_connection(); cur = conn.cursor()
            
            if not self.is_house:
                # UPDATE MASTER (Usando weight_kg)
                cur.execute("""
                    UPDATE masters SET 
                        shipper_name=%s, sh_account=%s, shipper_address=%s, sh_city=%s, sh_zip=%s, sh_state=%s, sh_country=%s, sh_phone=%s, sh_email=%s,
                        consignee_name=%s, cn_account=%s, consignee_address=%s, cn_city=%s, cn_zip=%s, cn_state=%s, cn_country=%s, cn_phone=%s, cn_email=%s,
                        total_pieces=%s, weight_kg=%s, nature_of_goods=%s,
                        payment_mode=%s, currency=%s, freight_rate=%s, freight_total=%s, other_charges=%s, dimensions_data=%s
                    WHERE id=%s
                """, (
                    s['name'], s['account'], s['address'], s['city'], s['zip'], s['state'], s['country'], s['phone'], s['email'],
                    c['name'], c['account'], c['address'], c['city'], c['zip'], c['state'], c['country'], c['phone'], c['email'],
                    self.inp_pieces.value(), self.inp_gross.value(), self.inp_desc.text().upper(),
                    pay_mode, self.inp_currency.text(), self.inp_rate.value(), self.inp_total_freight.value(),
                    self.txt_charges.toPlainText(), dims_json,
                    self.shipment_id
                ))
            else:
                # UPDATE HOUSE (Usando weight_gross y description)
                cur.execute("""
                    UPDATE houses SET 
                        shipper_name=%s, sh_account=%s, shipper_address=%s, sh_city=%s, sh_zip=%s, sh_state=%s, sh_country=%s, sh_phone=%s, sh_email=%s,
                        consignee_name=%s, cn_account=%s, consignee_address=%s, cn_city=%s, cn_zip=%s, cn_state=%s, cn_country=%s, cn_phone=%s, cn_email=%s,
                        pieces=%s, weight_gross=%s, description=%s,
                        payment_mode=%s, dimensions_data=%s
                    WHERE id=%s
                """, (
                    s['name'], s['account'], s['address'], s['city'], s['zip'], s['state'], s['country'], s['phone'], s['email'],
                    c['name'], c['account'], c['address'], c['city'], c['zip'], c['state'], c['country'], c['phone'], c['email'],
                    self.inp_pieces.value(), self.inp_gross.value(), self.inp_desc.text().upper(),
                    pay_mode, dims_json,
                    self.shipment_id
                ))

            conn.commit(); conn.close()
            QMessageBox.information(self, "Guardado", "Datos actualizados correctamente.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # --- UTILIDADES DE CALCULO ---
    def add_dim_row(self):
        r = self.table_dims.rowCount(); self.table_dims.insertRow(r)
        for i in range(4): self.table_dims.setItem(r, i, QTableWidgetItem("0"))
        self.table_dims.setItem(r, 4, QTableWidgetItem("0.000"))

    def del_dim_row(self):
        r = self.table_dims.currentRow()
        if r >= 0: self.table_dims.removeRow(r); self.recalc_totals()

    def calculate_row_volume(self, item):
        r = item.row(); c = item.column()
        if c == 4: return
        try:
            pcs = float(self.table_dims.item(r, 0).text())
            l = float(self.table_dims.item(r, 1).text())
            w = float(self.table_dims.item(r, 2).text())
            h = float(self.table_dims.item(r, 3).text())
            factor = 1000000 if self.combo_unit.currentText() == "CM" else 61024
            cbm = (l * w * h * pcs) / factor
            self.table_dims.blockSignals(True)
            self.table_dims.setItem(r, 4, QTableWidgetItem(f"{cbm:.3f}"))
            self.table_dims.blockSignals(False)
            self.recalc_totals()
        except: pass

    def recalc_totals(self):
        tot = 0.0
        for r in range(self.table_dims.rowCount()):
            try: tot += float(self.table_dims.item(r, 4).text())
            except: pass
        vol_w = tot * 166.67
        self.lbl_vol_total.setText(f"Volumen: {tot:.3f} m³")
        chg = max(self.inp_gross.value(), vol_w)
        self.lbl_chg_w.setText(f"Peso Cobrable: {chg:.2f} kg")
        self.calc_freight_total()

    def calc_freight_total(self):
        try:
            txt = self.lbl_chg_w.text().replace("Peso Cobrable:", "").replace("kg", "").strip()
            w = float(txt)
            self.inp_total_freight.setValue(w * self.inp_rate.value())
        except: pass