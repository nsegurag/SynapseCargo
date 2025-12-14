import sys
import os

# Ajustar ruta para importar desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import get_db_connection

def add_missing_columns():
    print("🔌 Conectando a Supabase para actualizar estructura...")
    
    commands = [
        # --- TABLA MASTERS ---
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS weight_kg DECIMAL(10,2) DEFAULT 0.00;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS volume_m3 DECIMAL(10,3) DEFAULT 0.00;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS chargeable_weight DECIMAL(10,2) DEFAULT 0.00;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS nature_of_goods TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'OPEN';",
        
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS shipper_name TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS shipper_address TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS sh_account TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS sh_city TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS sh_state TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS sh_zip TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS sh_country TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS sh_phone TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS sh_email TEXT;",
        
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS consignee_name TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS consignee_address TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS cn_account TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS cn_city TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS cn_state TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS cn_zip TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS cn_country TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS cn_phone TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS cn_email TEXT;",
        
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS payment_mode VARCHAR(5) DEFAULT 'PP';",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS currency VARCHAR(5) DEFAULT 'USD';",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS freight_rate DECIMAL(10,2) DEFAULT 0.00;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS freight_total DECIMAL(10,2) DEFAULT 0.00;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS other_charges TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS dimensions_data TEXT;",
        "ALTER TABLE masters ADD COLUMN IF NOT EXISTS flight_number TEXT;",

        # --- TABLA HOUSES ---
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS weight_gross DECIMAL(10,2) DEFAULT 0.00;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS weight_chargeable DECIMAL(10,2) DEFAULT 0.00;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS volume_cbm DECIMAL(10,3) DEFAULT 0.00;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS description TEXT;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS payment_mode VARCHAR(5) DEFAULT 'PP';",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS dimensions_data TEXT;",
        
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS shipper_name TEXT;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS shipper_address TEXT;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS consignee_name TEXT;",
        "ALTER TABLE houses ADD COLUMN IF NOT EXISTS consignee_address TEXT;"
    ]

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        for sql in commands:
            try:
                cur.execute(sql)
            except Exception as e:
                # Ignoramos si la columna ya existe, seguimos con la siguiente
                print(f"Nota: {e}")
                conn.rollback() 
            else:
                conn.commit()
                
        conn.close()
        print("✅ Base de datos actualizada con éxito. Ahora puedes generar Manifiestos.")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    add_missing_columns()