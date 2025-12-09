import sys
import os
import socket
import psycopg2
import urllib.parse

# ======================================================
#  CONFIGURACIÓN DE SUPABASE
# ======================================================
RAW_PASSWORD = "10Chocolates@"  # <--- ¡NO OLVIDES TU CONTRASEÑA!

# Configuración Estándar (La que funcionaba antes)
DB_HOST = "db.wskrvdxmugddtyeikeyx.supabase.co"
DB_PORT = "5432"  # Volvemos al puerto estándar
DB_NAME = "postgres"
DB_USER = "postgres" # Volvemos al usuario simple

# ======================================================
#  CONFIGURACIÓN DE VERSIONES
# ======================================================
CURRENT_VERSION = "2.0"
UPDATE_URL = "https://raw.githubusercontent.com/nsegurag/LabelGenerator/refs/heads/main/version.txt"
RELEASE_URL = "https://github.com/nsegurag/LabelGenerator/releases/latest"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    path = os.path.join(os.getenv('LOCALAPPDATA'), 'LabelGenerator')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def resolve_host_to_ipv4(hostname):
    """
    Intenta resolver la IP numérica. Si falla, devuelve el nombre original silenciosamente.
    """
    try:
        info = socket.getaddrinfo(hostname, None, family=socket.AF_INET)
        ip_address = info[0][4][0]
        return ip_address
    except Exception:
        # Si falla la resolución forzada, NO imprimimos error para no asustar.
        # Simplemente devolvemos el hostname original y dejamos que el conector decida.
        return hostname

def get_db_connection():
    try:
        # 1. Obtenemos la IP numérica (Ej: 12.34.56.78) en lugar del nombre
        target_host = resolve_host_to_ipv4(DB_HOST)
        
        # 2. Codificamos la contraseña
        encoded_pass = urllib.parse.quote_plus(RAW_PASSWORD)
        
        # 3. Construimos la URL usando la IP directa y el puerto 5432
        # Al usar la IP, saltamos el problema de DNS/IPv6 del router
        db_uri = f"postgresql://{DB_USER}:{encoded_pass}@{target_host}:{DB_PORT}/{DB_NAME}?sslmode=require"
        
        conn = psycopg2.connect(db_uri)
        return conn
        
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        raise e