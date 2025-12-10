import sys
import os
import psycopg2
import urllib.parse

# ======================================================
#  CONFIGURACIÓN DE IDENTIDAD
# ======================================================
APP_NAME = "SynapseCargo"
APP_VERSION = "3.0.0"
ORG_NAME = "NSLabs"

# ======================================================
#  CONFIGURACIÓN DE SUPABASE (CONEXIÓN ROBUSTA)
# ======================================================
# Tu contraseña real
RAW_PASSWORD = "10Chocolates@"

# 1. Usamos el Host Universal de AWS (Más compatible y estable)
DB_HOST = "aws-0-us-east-1.pooler.supabase.com"

# 2. Puerto del Pooler (Evita bloqueos comunes del 5432)
DB_PORT = "6543" 

# 3. Base de datos
DB_NAME = "postgres"

# 4. USUARIO COMPUESTO (Obligatorio para el puerto 6543)
# Formato: usuario.id_proyecto
DB_USER = "postgres.wskrvdxmugddtyeikeyx"

# ======================================================
#  CONFIGURACIÓN DE VERSIONES
# ======================================================
CURRENT_VERSION = "3.0"
UPDATE_URL = "https://raw.githubusercontent.com/nsegurag/LabelGenerator/refs/heads/main/version.txt"
RELEASE_URL = "https://github.com/nsegurag/LabelGenerator/releases/latest"

def resource_path(relative_path):
    """Obtiene ruta absoluta para recursos dentro del exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """Ruta segura en AppData"""
    path = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_db_connection():
    """
    Conexión directa usando el Pooler de AWS.
    Esta configuración salta los problemas de DNS y IPv6.
    """
    try:
        # Codificamos la contraseña para evitar errores con símbolos (@)
        encoded_pass = urllib.parse.quote_plus(RAW_PASSWORD)
        
        # Construimos la URL de conexión segura
        db_uri = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
        
        # Conectamos
        conn = psycopg2.connect(db_uri)
        return conn
        
    except Exception as e:
        print(f"❌ Error crítico conectando a Supabase: {e}")
        # Relanzamos el error para que la interfaz gráfica lo muestre
        raise e