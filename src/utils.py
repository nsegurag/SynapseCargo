import sys
import os
import psycopg2
import urllib.parse

# ======================================================
#  IDENTIDAD DE LA APP
# ======================================================
APP_NAME = "SynapseCargo"
APP_VERSION = "3.0.0"
ORG_NAME = "NSLabs"

# ======================================================
#  CONFIGURACIÓN DE CONEXIÓN BLINDADA (AWS POOLER)
# ======================================================
RAW_PASSWORD = "10Chocolates@"

# 1. HOST: Usamos la dirección de Amazon que te dio Supabase.
# Esta dirección NUNCA falla por DNS porque es un dominio global de AWS.
DB_HOST = "aws-1-us-east-1.pooler.supabase.com"

# 2. PUERTO: Usamos 5432 (Session Mode).
# Es más estable para aplicaciones de escritorio que el 6543.
DB_PORT = "5432"

# 3. BASE DE DATOS
DB_NAME = "postgres"

# 4. USUARIO: El usuario largo que te dio Supabase.
# Es OBLIGATORIO usar este formato con el host de AWS.
DB_USER = "postgres.brcqimesmfyagpxjwreb"

# ======================================================
#  CONFIGURACIÓN DE VERSIONES
# ======================================================
CURRENT_VERSION = "3.0"
UPDATE_URL = "https://raw.githubusercontent.com/nsegurag/LabelGenerator/refs/heads/main/version.txt"
RELEASE_URL = "https://github.com/nsegurag/LabelGenerator/releases/latest"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    path = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_db_connection():
    """
    Conexión directa al Pooler de Supabase (AWS).
    Estabilidad garantizada en IPv4 y redes corporativas.
    """
    try:
        encoded_pass = urllib.parse.quote_plus(RAW_PASSWORD)
        
        # Construimos la URL
        db_uri = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
        
        conn = psycopg2.connect(db_uri)
        return conn
        
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        raise e