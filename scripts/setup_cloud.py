import psycopg2
import urllib.parse
import sys

# ======================================================
#  CONFIGURACIÓN DE INSTALACIÓN (NUEVO PROYECTO)
# ======================================================
# Tu contraseña real
RAW_PASSWORD = "10Chocolates@" 

# DATOS DEL POOLER (Los que obtuviste del nuevo proyecto)
DB_HOST = "aws-1-us-east-1.pooler.supabase.com"
DB_PORT = "5432" # Usamos 5432 para crear tablas (Session Mode)
DB_NAME = "postgres"
DB_USER = "postgres.brcqimesmfyagpxjwreb" # Tu usuario largo nuevo

def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) DEFAULT 'user'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS masters (
            id SERIAL PRIMARY KEY,
            mawb_number VARCHAR(50) NOT NULL,
            origin VARCHAR(10) NOT NULL,
            destination VARCHAR(10) NOT NULL,
            service VARCHAR(10),
            total_pieces INTEGER DEFAULT 0,
            label_size VARCHAR(10) DEFAULT '4x6',
            created_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS houses (
            id SERIAL PRIMARY KEY,
            master_id INTEGER REFERENCES masters(id) ON DELETE CASCADE,
            hawb_number VARCHAR(50) NOT NULL,
            pieces INTEGER DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS labels (
            id SERIAL PRIMARY KEY,
            master_id INTEGER REFERENCES masters(id) ON DELETE CASCADE,
            house_id INTEGER REFERENCES houses(id) ON DELETE CASCADE,
            mawb_counter VARCHAR(20),
            hawb_counter VARCHAR(20),
            barcode_data VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(50),
            action VARCHAR(50),
            mawb_number VARCHAR(50),
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    try:
        print(f"🔌 Conectando a Supabase (AWS Pooler)...")
        print(f"    Host: {DB_HOST}")
        
        # Construcción segura de la URL
        encoded_pass = urllib.parse.quote_plus(RAW_PASSWORD)
        db_uri = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
        
        conn = psycopg2.connect(db_uri)
        cur = conn.cursor()

        print("🔨 Creando tablas en la nube...")
        for command in commands:
            cur.execute(command)

        print("👤 Verificando usuario admin...")
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        if cur.fetchone() is None:
            cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                        ('admin', 'admin123', 'admin'))
            print("✅ Usuario 'admin' creado exitosamente (Pass: admin123)")
        else:
            print("ℹ️ El usuario 'admin' ya existe.")

        cur.close()
        conn.commit()
        conn.close()
        print("🚀 ¡ÉXITO! Base de datos SynapseCargo configurada y lista.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        print("💡 Verifica que la contraseña en el script sea correcta.")

if __name__ == '__main__':
    create_tables()