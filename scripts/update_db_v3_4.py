import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.utils import get_db_connection

def update_db():
    print("🔌 Actualizando base de datos para v3.4...")
    commands = [
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS itinerary_data TEXT;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS itinerary_data TEXT;"
    ]
    try:
        conn = get_db_connection(); cur = conn.cursor()
        for sql in commands:
            try: cur.execute(sql)
            except Exception as e: print(f"Nota: {e}"); conn.rollback()
            else: conn.commit()
        conn.close()
        print("✅ Base de datos lista para Itinerarios y Cargos IATA.")
    except Exception as e: print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_db()