from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt

# ✅ CAMBIO: Importamos la conexión a la nube
from src.utils import get_db_connection

class LogsViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("📒 Bitácora del sistema (Nube)")
        self.setGeometry(300, 150, 900, 500)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("📒 Bitácora de acciones realizadas:"))

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Usuario",
            "Acción",
            "MAWB",
            "Detalles",
            "Fecha"
        ])

        # Configuración visual para que se vea bien y no sea editable
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_logs()

    def load_logs(self):
        self.table.setRowCount(0)

        try:
            # ✅ Conexión a PostgreSQL (Supabase)
            conn = get_db_connection()
            cursor = conn.cursor()

            # ✅ CAMBIO: 'user' -> 'user_name' (Así se llama la columna en la nube)
            cursor.execute("""
                SELECT 
                    id, 
                    user_name, 
                    action, 
                    mawb_number, 
                    details, 
                    created_at
                FROM logs
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()
            conn.close()

            for row_index, row_data in enumerate(rows):
                self.table.insertRow(row_index)

                for col_index, value in enumerate(row_data):
                    self.table.setItem(
                        row_index,
                        col_index,
                        QTableWidgetItem(str(value))
                    )
        
        except Exception as e:
            print(f"❌ Error cargando logs: {e}")
            # Opcional: Mostrar alerta si falla la carga
            # QMessageBox.warning(self, "Error", "No se pudo cargar la bitácora desde la nube.")