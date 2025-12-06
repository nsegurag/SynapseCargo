import os
from barcode import Code128
from barcode.writer import ImageWriter

# ✅ CORRECCIÓN: Usamos get_user_data_dir para guardar donde SÍ hay permisos
from src.utils import get_user_data_dir

# Guardar en AppData/LabelGenerator/barcodes
BARCODE_FOLDER = os.path.join(get_user_data_dir(), "barcodes")

def generate_barcode_image(text):
    """Genera el código de barras en la carpeta segura del usuario."""
    try:
        if not os.path.exists(BARCODE_FOLDER):
            os.makedirs(BARCODE_FOLDER)

        base_filename = os.path.join(BARCODE_FOLDER, text) 
        
        writer_options = {
            'module_width': 0.4, 
            'module_height': 15.0, 
            'quiet_zone': 1.0, 
            'font_size': 10, 
            'text_distance': 5.0, 
            'background': 'white', 
            'foreground': 'black',
            # ✅ IMPORTANTE: Desactivar texto para evitar errores de fuentes en el EXE
            'write_text': False 
        }
        
        code = Code128(text, writer=ImageWriter())
        saved_path = code.save(base_filename, options=writer_options)

        if not os.path.exists(saved_path):
            return None

        return saved_path

    except Exception as e:
        print(f"❌ ERROR generando barcode ({text}): {e}")
        return None