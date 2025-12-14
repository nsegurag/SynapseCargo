import sys
import os
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ✅ IMPORTACIÓN CORRECTA
from src.utils import get_db_connection, get_user_data_dir
# ✅ NUEVO IMPORT: Para regenerar códigos perdidos al vuelo
from src.logic.barcode_utils import generate_barcode_image 

# ------------------ TAMAÑOS DE ETIQUETA ------------------
def get_page_size(size):
    if size == "4x6":
        return (4 * inch, 6 * inch)
    elif size == "4x4":
        return (4 * inch, 4 * inch)
    elif size == "4x2":  
        return (4 * inch, 2 * inch) 
    else:
        return (4 * inch, 6 * inch)

# ------------------ MOTOR DE DIBUJO ADAPTATIVO ------------------
def draw_flexible_label(c, w, h, data):
    """
    Dibuja una etiqueta estilo IATA profesional.
    Busca el código de barras en la carpeta AppData del usuario.
    """
    is_compact = h < (3 * inch)

    # Márgenes
    margin = 4 if is_compact else 10
    safe_w = w - (2 * margin)
    safe_h = h - (2 * margin)
    
    # Fuente inteligente
    font_s = h / 14 if is_compact else w / 24
    c.setLineWidth(1.0 if is_compact else 1.2)      
    
    # Grid
    if is_compact:
        pct_header, pct_route, pct_details, pct_total = 0.16, 0.22, 0.18, 0.12 
    else:
        pct_header, pct_route, pct_details, pct_total = 0.18, 0.24, 0.18, 0.10    
    
    y_top = h - margin
    h_header = safe_h * pct_header
    y_header = y_top - h_header
    h_route = safe_h * pct_route
    y_route = y_header - h_route
    h_details = safe_h * pct_details
    y_details = y_route - h_details
    h_total = safe_h * pct_total
    y_total = y_details - h_total
    h_barcode = y_total - margin 
    y_barcode = margin

    # 1. HEADER
    c.rect(margin, y_header, safe_w, h_header)
    c.setFont("Helvetica", font_s * 0.6)
    c.drawString(margin + 5, y_top - (5 if is_compact else 10), "MAWB No.")
    c.setFont("Helvetica-Bold", font_s * (1.5 if is_compact else 1.8))
    c.drawCentredString(w / 2, y_header + (h_header * 0.25), data['mawb'])

    # 2. RUTA
    c.rect(margin, y_route, safe_w, h_route)
    mid_x = w / 2
    c.line(mid_x, y_route, mid_x, y_route + h_route)
    offset_lbl = 5 if is_compact else 10
    
    c.setFont("Helvetica", font_s * 0.6)
    c.drawString(margin + 5, y_header - offset_lbl, "Origin")
    c.setFont("Helvetica-Bold", font_s * 2.0) 
    c.drawCentredString(margin + (safe_w / 4), y_route + (h_route * 0.30), data['origin'])
    
    c.setFont("Helvetica", font_s * 0.6)
    c.drawString(mid_x + 5, y_header - offset_lbl, "Dest")
    c.setFont("Helvetica-Bold", font_s * 2.0) 
    c.drawCentredString(mid_x + (safe_w / 4), y_route + (h_route * 0.30), data['dest'])

    # 3. DETALLES
    c.rect(margin, y_details, safe_w, h_details)
    if data['hawb']:
        split_x = margin + (safe_w * 0.6)
        c.line(split_x, y_details, split_x, y_details + h_details)
        c.setFont("Helvetica", font_s * 0.6)
        c.drawString(margin + 5, y_route - offset_lbl, "HAWB")
        c.setFont("Helvetica-Bold", font_s * 1.1)
        c.drawCentredString(margin + (safe_w * 0.3), y_details + (h_details * 0.30), data['hawb'])
        c.setFont("Helvetica", font_s * 0.6)
        c.drawString(split_x + 5, y_route - offset_lbl, "Pcs")
        c.setFont("Helvetica-Bold", font_s * 1.1)
        c.drawCentredString(split_x + (safe_w * 0.2), y_details + (h_details * 0.30), data['counter_str'])
    else:
        c.setFont("Helvetica", font_s * 0.6)
        c.drawString(margin + 5, y_route - offset_lbl, "Piece No")
        c.setFont("Helvetica-Bold", font_s * 1.4)
        c.drawCentredString(w / 2, y_details + (h_details * 0.30), data['counter_str'])

    # 3.5 TOTAL
    c.rect(margin, y_total, safe_w, h_total)
    
    # Texto a mostrar (Prioridad al contador MAWB)
    total_text = data.get('mawb_counter_str', f"{data['total_pcs']} PCS")

    if is_compact:
        c.setFont("Helvetica-Bold", font_s * 0.9)
        c.drawCentredString(w / 2, y_total + (h_total * 0.3), f"MAWB: {total_text}")
    else:
        c.setFont("Helvetica", font_s * 0.5)
        c.drawString(margin + 4, y_details - 8, "Total No.")
        c.setFont("Helvetica-Bold", font_s * 1.3) 
        c.drawCentredString(w / 2, y_total + 5, total_text)

    # 4. BARCODE
    barcode_filename = f"{data['barcode_text']}.png"
    barcode_path = os.path.join(get_user_data_dir(), "barcodes", barcode_filename)
    
    # 🛠️ AUTO-REPARACIÓN: Si no existe (por cambio de nombre/PC), lo creamos YA
    if not os.path.exists(barcode_path):
        print(f"♻️ Regenerando código de barras perdido: {data['barcode_text']}")
        generate_barcode_image(data['barcode_text'])
    
    if os.path.exists(barcode_path):
        try:
            img = ImageReader(barcode_path)
            iw, ih = img.getSize()
            aspect = ih / float(iw)
            
            draw_w = safe_w * 0.90
            draw_h = draw_w * aspect
            
            max_h = h_barcode * 0.90 
            if draw_h > max_h:
                draw_h = max_h
                draw_w = draw_h / aspect
            
            x_img = (w - draw_w) / 2
            y_img = margin + (h_barcode - draw_h) / 2 
            
            c.drawImage(img, x_img, y_img, width=draw_w, height=draw_h, mask='auto')
            
            # Texto debajo
            if not is_compact:
                c.setFont("Helvetica", font_s * 0.5)
                c.drawCentredString(w/2, margin - 2, data['barcode_text'])
                
        except Exception as e:
            print(f"Error dibujando barcode: {e}")
    else:
        print(f"⚠️ Barcode NO encontrado ni regenerado: {barcode_path}")
        c.setFont("Helvetica", 6)
        c.drawString(margin, margin + 10, "ERROR: Barcode Missing")
        c.drawString(margin, margin + 2, f"Code: {data['barcode_text']}")

# ------------------ FUNCIÓN PRINCIPAL ------------------
def generate_labels_pdf(master_id, file_path, size="4x6"):
    w, h = get_page_size(size)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT mawb_number, origin, destination, total_pieces FROM masters WHERE id=%s", (master_id,))
    master = cursor.fetchone()
    
    if not master:
        conn.close()
        return
    
    mawb, org, dest, total_pcs = master

    cursor.execute("""
        SELECT l.mawb_counter, l.hawb_counter, l.barcode_data, h.hawb_number
        FROM labels l
        LEFT JOIN houses h ON l.house_id = h.id
        WHERE l.master_id = %s
        ORDER BY l.id ASC
    """, (master_id,))
    
    labels = cursor.fetchall()
    conn.close()

    if not labels:
        return

    c = canvas.Canvas(file_path, pagesize=(w, h))

    for lbl in labels:
        m_cnt, h_cnt, b_code, h_num = lbl
        
        mawb_counter_display = m_cnt.replace("/", " of ") if m_cnt else ""
        
        if h_num:
            counter_display = h_cnt.replace("/", " of ")
        else:
            counter_display = mawb_counter_display

        data = {
            "mawb": mawb,
            "origin": org,
            "dest": dest,
            "total_pcs": total_pcs,
            "counter_str": counter_display,
            "mawb_counter_str": mawb_counter_display,
            "barcode_text": b_code,
            "hawb": h_num if h_num else ""
        }

        draw_flexible_label(c, w, h, data)
        c.showPage()

    c.save()
    print(f"✅ PDF Generado: {file_path}")