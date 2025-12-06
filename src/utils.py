import sys
import os
import shutil
import psycopg2
import urllib.parse

# ======================================================
#  CONFIGURACIÓN DE SUPABASE (POSTGRESQL)
# ======================================================
# 1. Escribe tu contraseña aquí dentro de las comillas
RAW_PASSWORD = "TU_CONTRASEÑA_AQUI" 

# 2. Configuración de tu servidor (Ya está puesta con tus datos)
HOST_STRING = "postgres@db.wskrvdxmugddtyeikeyx.supabase.co:5432/postgres"

# 3. Construcción segura de la dirección (No tocar)
# Esto evita errores si tu contraseña tiene símbolos raros
encoded_pass = urllib.parse.quote_plus(RAW_PASSWORD)
user_part, rest_of_host = HOST_STRING.split("@", 1)
DB_URI = f"postgresql://{user_part}:{encoded_pass}@{rest_of_host}"

# ======================================================
#  CONFIGURACIÓN DE VERSIONES (AUTO-UPDATE)
# ======================================================
CURRENT_VERSION = "1.0"
UPDATE_URL = "https://raw.githubusercontent.com/nsegurag/LabelGenerator/refs/heads/main/version.txt"
RELEASE_URL = "https://github.com/nsegurag/LabelGenerator/releases/latest"

def resource_path(relative_path):
    """
    Obtiene ruta absoluta para recursos estáticos (imágenes fijas, iconos)
    dentro del exe.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """
    Retorna la ruta segura y escribible en AppData del usuario.
    Aquí guardaremos los BARCODES y PDFs generados (archivos temporales).
    Ruta: C:/Users/Usuario/AppData/Local/LabelGenerator
    """
    path = os.path.join(os.getenv('LOCALAPPDATA'), 'LabelGenerator')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_db_connection():
    """
    Crea y devuelve una conexión a la base de datos en la nube (Supabase).
    Reemplaza a la antigua función get_db_path.
    """
    try:
        # Intentamos conectar a la nube
        conn = psycopg2.connect(DB_URI)
        return conn
    except Exception as e:
        # Si falla (ej. sin internet), lanzamos el error para que la ventana muestre la alerta
        print(f"❌ Error conectando a Supabase: {e}")
        raise e