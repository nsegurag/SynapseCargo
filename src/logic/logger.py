import datetime
# ✅ CAMBIO: Usamos la conexión a la nube
from src.utils import get_db_connection

def log_action(user, action, mawb_number, details=""):
    """
    Guarda un evento en la bitácora (tabla logs) en la nube.
    Diseñado para no romper el programa si la conexión falla (solo avisa en consola).
    """
    try:
        # 1. Conectamos a Supabase
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Ejecutamos el INSERT (Sintaxis PostgreSQL: %s)
        # Nota: La columna en la base de datos se llama 'user_name'
        cursor.execute("""
            INSERT INTO logs (user_name, action, mawb_number, details)
            VALUES (%s, %s, %s, %s)
        """, (user, action, mawb_number, details))
        
        conn.commit()
        conn.close()

        # 3. Feedback en consola
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"📝 [{timestamp}] LOG: {user} -> {action} ({mawb_number}) | {details}")

    except Exception as e:
        # Si falla el log (ej. sin internet), no detenemos el programa principal
        print(f"❌ ERROR CRÍTICO EN LOGGER: {e}")