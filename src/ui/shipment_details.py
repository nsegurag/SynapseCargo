import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QDoubleSpinBox, QFormLayout, 
    QGroupBox, QComboBox, QMessageBox, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from src.utils import get_db_connection

# --- ESTILOS FLUENT ---
BTN_BLUE = "QPushButton { background-color: #0067C0; color: white; border-radius: 6px; font-weight: bold; padding: 8px 16px; font-size: 14px; } QPushButton:hover { background-color: #0056a3; }"
BTN_WHITE = "QPushButton { background-color: white; border: 1px solid #D1D1D1; border-radius: 6px; color: #333; padding: 8px 16px; } QPushButton:hover { background-color: #F0F0F0; }"
INPUT_STYLE = "QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox { background-color: white; border: 1px solid #D1D1D1; border-radius: 4px; padding: 4px; } QLineEdit:focus { border: 2px solid #0067C0; }"

class AddressBlock(QGroupBox):
    """Componente reutilizable para Shipper y Consignee"""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("QGroupBox { font-weight: bold; color: #0067C0; border: 1px solid #E0E0E0; border-radius: 8px; margin-top: 10px; padding-top: 15px; background: #FFFFFF; }")
        
        layout = QFormLayout(self)
        layout.setSpacing(8)
        
        self.name = QLineEdit(); self.name.setPlaceholderText("Nombre de la empresa / Persona")
        self.account = QLineEdit(); self.account.setPlaceholderText("Número de Cuenta")
        self.address = QTextEdit(); self.address.setMaximumHeight(50); self.address.setPlaceholderText("Dirección calle, número...")
        
        row1 = QHBoxLayout()
        self.city = QLineEdit(); self.city.setPlaceholderText("Ciudad")
        self.zip = QLineEdit(); self.zip.setPlaceholderText("Zip Code")
        self.zip.setFixedWidth(80)
        row1.addWidget(self.city); row1.addWidget(self.zip)
        
        row2 = QHBoxLayout()
        self.state = QLineEdit(); self.state.setPlaceholderText("Estado/Provincia")
        self.country = QLineEdit(); self.country.setPlaceholderText("País (ISO)")
        self.country.setFixedWidth(60)
        row2.addWidget(self.state); row2.addWidget(self.country)
        
        row3 = QHBoxLayout()
        self.phone = QLineEdit(); self.phone.setPlaceholderText("Teléfono")
        self.email = QLineEdit(); self.email.setPlaceholderText("Email")
        row3.addWidget(self.phone); row3.addWidget(self.email)

        # Aplicar estilos
        for w in [self.name, self.account, self.address, self.city, self.zip, self.state, self.country, self.phone, self.email]:
            w.setStyleSheet(INPUT_STYLE)

        layout.addRow("Name *:", self.name)
        layout.addRow("Account:", self.account)
        layout.addRow("Address *:", self.address)
        layout.addRow("City/Zip *:", row1)
        layout.addRow("State/Country:", row2)
        layout.addRow("Contact:", row3)

    def get_data(self):
        return {
            "name": self.name.text(), "account": self.account.text(), "address": self.address.toPlainText(),
            "city": self.city.text(), "zip": self.zip.text(), "state": self.state.text(),
            "country": self.country.text(), "phone": self.phone.text(), "email": self.email.text()
        }

    def set_data(self, d):
        self.name.setText(d.get("name","")); self.account.setText(d.get("account","")); self.address.setText(d.get("address",""))
        self.city.setText(d.get("city","")); self.zip.setText(d.get("zip","")); self.state.setText(d.get("state",""))
        self.country.setText(d.get("country","")); self.phone.setText(d.get("phone","")); self.email.setText(d.get("email",""))

class ShipmentDetailsDialog(QDialog):
    def __init__(self, shipment_id, shipment_num, is_house=False, parent=None):
        super().__init__(parent)

        self.shipment_id = shipment_id
        self.shipment_num = shipment_num
        self.is_house = is_house
        self.table_name = "houses" if is_house else "masters"

        type_str = "HAWB" if is_house else "MAWB"
        color = "#D32F2F" if is_house else "#0067C0"

        self.setWindowTitle(f"Editor {type_str} - {shipment_num}")
        self.resize(900, 700)
        self.setStyleSheet("background-color: #F3F3F3;")

        main_layout = QVBoxLayout(self)

        # HEADER
        header = QHBoxLayout()
        lbl_title = QLabel(f"📦 Gestión de {type_str}: {shipment_num}")
        lbl_title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {color};"
        )
        header.addWidget(lbl_title)
        header.addStretch()
        main_layout.addLayout(header)

        # --- TABS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #C0C0C0; background: white; border-radius: 6px; }
            QTabBar::tab { background: #E0E0E0; padding: 10px 20px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #0067C0; font-weight: bold; color: #0067C0; }
        """)

        self.tab_general = QWidget()
        self.tab_cargo = QWidget()
        self.tab_accounting = QWidget()

        self.setup_tab_general()
        self.setup_tab_cargo()
        self.setup_tab_accounting()

        self.tabs.addTab(self.tab_general, "1. Partes")
        self.tabs.addTab(self.tab_cargo, "2. Carga y Dimensiones")
        self.tabs.addTab(self.tab_accounting, "3. Tarifas")

        main_layout.addWidget(self.tabs)

        # FOOTER
        btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(BTN_WHITE)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("💾 Guardar Datos")
        btn_save.setStyleSheet(BTN_BLUE)
        btn_save.clicked.connect(self.save_all)

        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)

        main_layout.addLayout(btns)

        self.load_from_db()


    def setup_tab_general(self):
        layout = QHBoxLayout(self.tab_general)
        layout.setSpacing(20)
        self.shipper_block = AddressBlock("🛫 Shipper (Remitente)")
        self.consignee_block = AddressBlock("🛬 Consignee (Destinatario)")
        layout.addWidget(self.shipper_block)
        layout.addWidget(self.consignee_block)

    def setup_tab_cargo(self):
        layout = QVBoxLayout(self.tab_cargo)
        
        # Grid para inputs rápidos
        grid_info = QHBoxLayout()
        self.inp_pieces = QDoubleSpinBox(); self.inp_pieces.setRange(0,99999); self.inp_pieces.setDecimals(0); self.inp_pieces.setSuffix(" pcs")
        self.inp_gross = QDoubleSpinBox(); self.inp_gross.setRange(0,999999); self.inp_gross.setSuffix(" kg")
        self.inp_desc = QLineEdit(); self.inp_desc.setPlaceholderText("NATURE AND QUANTITY OF GOODS (Ej: CONSOLIDATION)")
        self.inp_desc.setStyleSheet(INPUT_STYLE)

        # Estilizar SpinBox
        for s in [self.inp_pieces, self.inp_gross]: s.setStyleSheet(INPUT_STYLE)

        grid_info.addWidget(QLabel("Total Piezas:")); grid_info.addWidget(self.inp_pieces)
        grid_info.addWidget(QLabel("Peso Bruto Total:")); grid_info.addWidget(self.inp_gross)
        grid_info.addWidget(QLabel("Descripción:")); grid_info.addWidget(self.inp_desc, 1)
        layout.addLayout(grid_info)

        # TABLA DE DIMENSIONES
        group_dims = QGroupBox("📏 Dimensiones (Calculadora Volumétrica)")
        group_dims.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #DDD; margin-top: 10px; }")
        l_dims = QVBoxLayout(group_dims)
        
        # Botones tabla
        h_tools = QHBoxLayout()
        self.combo_unit = QComboBox(); self.combo_unit.addItems(["CM", "INCH"]); self.combo_unit.setFixedWidth(70)
        btn_add_dim = QPushButton("➕ Agregar Línea"); btn_add_dim.clicked.connect(self.add_dim_row); btn_add_dim.setStyleSheet(BTN_WHITE)
        btn_del_dim = QPushButton("🗑️ Borrar Línea"); btn_del_dim.clicked.connect(self.del_dim_row); btn_del_dim.setStyleSheet("color: red; border: 1px solid red; background: white; border-radius: 6px; padding: 6px;")
        h_tools.addWidget(QLabel("Unidad:")); h_tools.addWidget(self.combo_unit); h_tools.addWidget(btn_add_dim); h_tools.addWidget(btn_del_dim); h_tools.addStretch()
        l_dims.addLayout(h_tools)

        self.table_dims = QTableWidget(0, 5)
        self.table_dims.setHorizontalHeaderLabels(["Piezas", "Largo", "Ancho", "Alto", "Volumen (CBM)"])
        self.table_dims.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_dims.setStyleSheet("QTableWidget { background: white; border: 1px solid #DDD; }")
        self.table_dims.itemChanged.connect(self.calculate_row_volume) # Auto calculo
        l_dims.addWidget(self.table_dims)

        # Resultados
        h_res = QHBoxLayout()
        self.lbl_total_cbm = QLabel("Total Vol: 0.000 m³"); self.lbl_total_cbm.setStyleSheet("font-size: 14px; font-weight: bold; color: #0067C0;")
        self.lbl_chg_w = QLabel("Peso Cobrable: 0.00 kg"); self.lbl_chg_w.setStyleSheet("font-size: 14px; font-weight: bold; color: #D32F2F;")
        h_res.addStretch(); h_res.addWidget(self.lbl_total_cbm); h_res.addSpacing(20); h_res.addWidget(self.lbl_chg_w)
        l_dims.addLayout(h_res)
        
        layout.addWidget(group_dims)

    def setup_tab_accounting(self):
        layout = QFormLayout(self.tab_accounting)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.combo_pp_cc = QComboBox(); self.combo_pp_cc.addItems(["PP (Prepaid)", "CC (Charges Collect)"])
        self.inp_currency = QLineEdit("USD"); self.inp_currency.setFixedWidth(60)
        
        self.inp_rate = QDoubleSpinBox(); self.inp_rate.setRange(0, 99999); self.inp_rate.setPrefix("$ "); self.inp_rate.setDecimals(2)
        self.inp_rate.valueChanged.connect(self.calc_freight_total)
        
        self.inp_total_freight = QDoubleSpinBox(); self.inp_total_freight.setRange(0, 999999); self.inp_total_freight.setPrefix("$ "); self.inp_total_freight.setDecimals(2)
        
        self.txt_other_charges = QTextEdit(); self.txt_other_charges.setPlaceholderText("Ej: DUE AGENT: $50\nFSC: $0.15/kg...")
        self.txt_other_charges.setMaximumHeight(100)

        for w in [self.combo_pp_cc, self.inp_currency, self.inp_rate, self.inp_total_freight, self.txt_other_charges]: w.setStyleSheet(INPUT_STYLE)

        layout.addRow("Modo de Pago:", self.combo_pp_cc)
        layout.addRow("Moneda:", self.inp_currency)
        layout.addRow("Tarifa por Kg (Rate):", self.inp_rate)
        layout.addRow("Total Flete (Estimado):", self.inp_total_freight)
        layout.addRow("Otros Cargos / Ratings:", self.txt_other_charges)

    # --- LOGICA DIMENSIONES ---
    def add_dim_row(self):
        row = self.table_dims.rowCount()
        self.table_dims.insertRow(row)
        for i in range(4): self.table_dims.setItem(row, i, QTableWidgetItem("0"))
        self.table_dims.setItem(row, 4, QTableWidgetItem("0.000")) # Columna calc
        
    def del_dim_row(self):
        r = self.table_dims.currentRow()
        if r >= 0: self.table_dims.removeRow(r); self.recalc_totals()

    def calculate_row_volume(self, item):
        row = item.row()
        col = item.column()
        if col == 4: return # Evitar loop infinito si editamos el resultado
        
        try:
            pcs = float(self.table_dims.item(row, 0).text())
            l = float(self.table_dims.item(row, 1).text())
            w = float(self.table_dims.item(row, 2).text())
            h = float(self.table_dims.item(row, 3).text())
            
            # Calculo CBM: (LxWxH * Pcs) / 1,000,000 para CM
            factor = 1000000 if self.combo_unit.currentText() == "CM" else 61024 # Aprox para inch a cbm
            cbm = (l * w * h * pcs) / factor
            
            self.table_dims.blockSignals(True)
            self.table_dims.setItem(row, 4, QTableWidgetItem(f"{cbm:.3f}"))
            self.table_dims.blockSignals(False)
            self.recalc_totals()
        except:
            pass

    def recalc_totals(self):
        total_cbm = 0.0
        for r in range(self.table_dims.rowCount()):
            try: total_cbm += float(self.table_dims.item(r, 4).text())
            except: pass
        
        # Vol Weight Ratio 1:6000 standard IATA
        vol_w = total_cbm * 166.67 
        
        self.lbl_total_cbm.setText(f"Total Vol: {total_cbm:.3f} m³")
        
        gross = self.inp_gross.value()
        chargeable = max(gross, vol_w)
        self.lbl_chg_w.setText(f"Peso Cobrable: {chargeable:.2f} kg")
        self.calc_freight_total()

    def calc_freight_total(self):
        # Tomar el peso cobrable del label (parsear texto)
        try:
            txt = self.lbl_chg_w.text().replace("Peso Cobrable:", "").replace("kg", "").strip()
            chg_w = float(txt)
            rate = self.inp_rate.value()
            self.inp_total_freight.setValue(chg_w * rate)
        except: pass

    # --- CARGA Y GUARDADO ---
    def load_from_db(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            base_fields = """
                shipper_name, sh_account, shipper_address, sh_city, sh_zip, sh_state, sh_country, sh_phone, sh_email,
                consignee_name, cn_account, consignee_address, cn_city, cn_zip, cn_state, cn_country, cn_phone, cn_email,
                weight_gross, nature_of_goods,
                payment_mode, dimensions_data
            """

            if not self.is_house:
                base_fields += """
                    , total_pieces, currency, freight_rate, freight_total, other_charges
                """
            else:
                base_fields += """
                    , pieces, 'USD', 0.0, 0.0, ''
                """

            query = f"SELECT {base_fields} FROM {self.table_name} WHERE id = %s"
            cur.execute(query, (self.shipment_id,))
            r = cur.fetchone()
            conn.close()

            if not r:
                return

            # SHIPPER / CONSIGNEE
            self.shipper_block.set_data({
                "name": r[0], "account": r[1], "address": r[2],
                "city": r[3], "zip": r[4], "state": r[5],
                "country": r[6], "phone": r[7], "email": r[8]
            })

            self.consignee_block.set_data({
                "name": r[9], "account": r[10], "address": r[11],
                "city": r[12], "zip": r[13], "state": r[14],
                "country": r[15], "phone": r[16], "email": r[17]
            })

            # CARGA
            self.inp_gross.setValue(float(r[18] or 0))
            self.inp_desc.setText(r[19] or "")

            # PAGO
            self.combo_pp_cc.setCurrentIndex(0 if r[20] == "PP" else 1)

            # DIMENSIONES
            if r[21]:
                dims = json.loads(r[21])
                for d in dims:
                    row = self.table_dims.rowCount()
                    self.table_dims.insertRow(row)
                    self.table_dims.setItem(row, 0, QTableWidgetItem(str(d["pcs"])))
                    self.table_dims.setItem(row, 1, QTableWidgetItem(str(d["l"])))
                    self.table_dims.setItem(row, 2, QTableWidgetItem(str(d["w"])))
                    self.table_dims.setItem(row, 3, QTableWidgetItem(str(d["h"])))
                    self.table_dims.setItem(row, 4, QTableWidgetItem(str(d["vol"])))
                self.recalc_totals()

            # CAMPOS EXTRA
            self.inp_pieces.setValue(r[22] or 0)
            self.inp_currency.setText(r[23])
            self.inp_rate.setValue(float(r[24]))
            self.inp_total_freight.setValue(float(r[25]))
            self.txt_other_charges.setText(r[26])

        except Exception as e:
            print(f"Error cargando datos: {e}")

    def save_all(self):
        s = self.shipper_block.get_data()
        c = self.consignee_block.get_data()

        dims = []
        for r in range(self.table_dims.rowCount()):
            try:
                dims.append({
                    "pcs": self.table_dims.item(r, 0).text(),
                    "l": self.table_dims.item(r, 1).text(),
                    "w": self.table_dims.item(r, 2).text(),
                    "h": self.table_dims.item(r, 3).text(),
                    "vol": self.table_dims.item(r, 4).text()
                })
            except:
                pass

        dims_json = json.dumps(dims)
        pay_mode = "PP" if self.combo_pp_cc.currentIndex() == 0 else "CC"

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            if not self.is_house:
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
                    pay_mode, self.inp_currency.text(), self.inp_rate.value(),
                    self.inp_total_freight.value(), self.txt_other_charges.toPlainText(),
                    dims_json, self.shipment_id
                ))
            else:
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
                    self.inp_pieces.value(), self.inp_gross.value(),
                    self.inp_desc.text().upper(),
                    pay_mode, dims_json, self.shipment_id
                ))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Éxito", "Datos guardados correctamente.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
