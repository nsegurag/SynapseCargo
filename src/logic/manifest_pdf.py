import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from src.utils import get_db_connection

def generate_cargo_manifest(master_id, file_path):
    try:
        # 1. OBTENER DATOS DE LA DB
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Datos de la Master
        cur.execute("""
            SELECT mawb_number, origin, destination, total_pieces, weight_kg, 
                   shipper_name, consignee_name, flight_number, status
            FROM masters WHERE id = %s
        """, (master_id,))
        mawb = cur.fetchone()
        
        # Datos de las HAWBs
        cur.execute("""
            SELECT hawb_number, pieces, weight_gross, description, shipper_name, consignee_name
            FROM houses WHERE master_id = %s ORDER BY hawb_number ASC
        """, (master_id,))
        hawbs = cur.fetchall()
        
        conn.close()

        if not mawb: return False

        # Desempaquetar Master
        mawb_num, org, dest, tot_pcs, tot_w, sh_name, cn_name, flt, status = mawb
        
        # 2. CONFIGURAR PDF
        doc = SimpleDocTemplate(file_path, pagesize=landscape(LETTER),
                                rightMargin=30, leftMargin=30, 
                                topMargin=30, bottomMargin=18)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilos Personalizados
        style_title = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, fontSize=18, spaceAfter=20)
        style_normal = styles['Normal']
        style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

        # 3. ENCABEZADO
        elements.append(Paragraph(f"CARGO MANIFEST / CONSOLIDATION", style_title))
        
        # Tabla de Info General (Master)
        data_header = [
            [f"MAWB: {mawb_num}", f"Origin: {org}", f"Dest: {dest}"],
            [f"Shipper: {sh_name or 'N/A'}", f"Consignee: {cn_name or 'N/A'}", f"Status: {status}"]
        ]
        
        t_head = Table(data_header, colWidths=[240, 240, 240])
        t_head.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(t_head)
        elements.append(Spacer(1, 20))

        # 4. TABLA DE HAWBS (El contenido principal)
        # Encabezados
        table_data = [['HAWB No.', 'Shipper', 'Consignee', 'Pieces', 'Weight (Kg)', 'Description']]
        
        total_h_pcs = 0
        total_h_w = 0.0

        # Filas
        for h in hawbs:
            # h: [num, pcs, w, desc, ship, cons]
            h_num, pcs, w, desc, h_ship, h_cons = h
            
            table_data.append([
                h_num, 
                h_ship or "", 
                h_cons or "", 
                str(pcs), 
                f"{float(w):.2f}", 
                desc or ""
            ])
            
            total_h_pcs += pcs
            total_h_w += float(w or 0)

        # Fila de Totales
        table_data.append(['TOTALS', '', '', str(total_h_pcs), f"{total_h_w:.2f}", ''])

        # Crear Tabla
        t_body = Table(table_data, colWidths=[100, 150, 150, 60, 80, 180])
        
        # Estilo Tabla
        style_body = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue), # Header azul
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,0), (2,-1), 'LEFT'), # Shipper/Consignee a la izq
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-2), 0.5, colors.lightgrey), # Grid cuerpo
            # Estilo fila Totales
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,-1), (-1,-1), 1, colors.black),
        ])
        t_body.setStyle(style_body)
        
        elements.append(t_body)
        
        # 5. GENERAR
        doc.build(elements)
        print(f"✅ Manifiesto generado: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error generando manifiesto: {e}")
        raise e