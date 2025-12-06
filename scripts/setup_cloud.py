import psycopg2
import urllib.parse 

# ======================================================
#  CONFIGURACIÓN (SOLO PON TU CONTRASEÑA AQUÍ)
# ======================================================
# Escribe tu contraseña tal cual, con todos sus símbolos.
# NO borres las comillas.
RAW_PASSWORD = "10Chocolates@" 

# He configurado esto con TU dirección exacta de Supabase.
# NO lo toques.
HOST_STRING = "postgres@db.wskrvdxmugddtyeikeyx.supabase.co:5432/postgres"

# --- MAGIA PARA QUE NO FALLE ---
# Esto convierte símbolos problemáticos (como @, :, /) en código seguro
encoded_pass = urllib.parse.quote_plus(RAW_PASSWORD)

# Armamos la dirección final de forma segura
user_part, rest_of_host = HOST_STRING.split("@", 1)
DB_URI = f"postgresql://{user_part}:{encoded_pass}@{rest_of_host}"

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
        print(f"🔌 Conectando a Supabase...")
        print(f"    Servidor: {rest_of_host}")
        
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()

        print("🔨 Creando tablas...")
        for command in commands:
            cur.execute(command)

        print("👤 Verificando usuario admin...")
        cur.execute("SELECT * FROM users WHERE username = 'admin'")
        if cur.fetchone() is None:
            cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                        ('admin', 'admin123', 'admin'))
            print("✅ Usuario 'admin' creado (Pass: admin123)")
        else:
            print("ℹ️ El usuario 'admin' ya existe.")

        cur.close()
        conn.commit()
        conn.close()
        print("🚀 ¡ÉXITO! Base de datos en la nube configurada y lista.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Verifica que tu contraseña sea correcta.")

if __name__ == '__main__':
    create_tables()