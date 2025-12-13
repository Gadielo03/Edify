from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO


def generate_certificate(user, course):
    """
    Genera un certificado de finalización de curso en PDF
    
    Args:
        user: Usuario que completó el curso
        course: Curso completado
    
    Returns:
        BytesIO: Buffer con el PDF generado
    """
    buffer = BytesIO()
    
    # Crear PDF en formato horizontal
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Fondo decorativo azul oscuro
    c.setFillColor(colors.HexColor('#1a237e'))
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    # Borde decorativo blanco
    c.setStrokeColor(colors.white)
    c.setLineWidth(10)
    c.rect(20, 20, width-40, height-40, fill=False, stroke=True)
    
    # Borde decorativo dorado
    c.setStrokeColor(colors.HexColor('#ffd700'))
    c.setLineWidth(5)
    c.rect(30, 30, width-60, height-60, fill=False, stroke=True)
    
    # Fondo blanco interior
    c.setFillColor(colors.white)
    c.rect(45, 45, width-90, height-90, fill=True, stroke=False)
    
    # Título "CERTIFICADO"
    c.setFillColor(colors.HexColor('#1a237e'))
    c.setFont("Helvetica-Bold", 48)
    title_text = "CERTIFICADO"
    title_width = c.stringWidth(title_text, "Helvetica-Bold", 48)
    c.drawString((width - title_width) / 2, height - 120, title_text)
    
    # Línea decorativa bajo el título
    c.setStrokeColor(colors.HexColor('#ffd700'))
    c.setLineWidth(3)
    c.line(150, height - 135, width - 150, height - 135)
    
    # Texto "Se otorga a"
    c.setFillColor(colors.HexColor('#424242'))
    c.setFont("Helvetica", 20)
    text = "Se otorga a:"
    text_width = c.stringWidth(text, "Helvetica", 20)
    c.drawString((width - text_width) / 2, height - 180, text)
    
    # Nombre del usuario
    c.setFillColor(colors.HexColor('#1a237e'))
    c.setFont("Helvetica-Bold", 36)
    user_name = user.get_full_name() or user.username
    name_width = c.stringWidth(user_name, "Helvetica-Bold", 36)
    c.drawString((width - name_width) / 2, height - 230, user_name)
    
    # Línea bajo el nombre
    c.setStrokeColor(colors.HexColor('#1a237e'))
    c.setLineWidth(2)
    c.line(150, height - 240, width - 150, height - 240)
    
    # Texto "Por completar exitosamente"
    c.setFillColor(colors.HexColor('#424242'))
    c.setFont("Helvetica", 18)
    text = "Por completar exitosamente el curso:"
    text_width = c.stringWidth(text, "Helvetica", 18)
    c.drawString((width - text_width) / 2, height - 280, text)
    
    # Nombre del curso
    c.setFillColor(colors.HexColor('#1a237e'))
    c.setFont("Helvetica-Bold", 28)
    course_title = course.title
    
    # Dividir el título si es muy largo
    max_width = width - 200
    if c.stringWidth(course_title, "Helvetica-Bold", 28) > max_width:
        words = course_title.split()
        line1 = []
        line2 = []
        for word in words:
            test_line = ' '.join(line1 + [word])
            if c.stringWidth(test_line, "Helvetica-Bold", 28) <= max_width:
                line1.append(word)
            else:
                line2.append(word)
        
        line1_text = ' '.join(line1)
        line2_text = ' '.join(line2)
        line1_width = c.stringWidth(line1_text, "Helvetica-Bold", 28)
        line2_width = c.stringWidth(line2_text, "Helvetica-Bold", 28)
        
        c.drawString((width - line1_width) / 2, height - 330, line1_text)
        c.drawString((width - line2_width) / 2, height - 365, line2_text)
    else:
        course_width = c.stringWidth(course_title, "Helvetica-Bold", 28)
        c.drawString((width - course_width) / 2, height - 330, course_title)
    
    # Fecha de finalización
    c.setFillColor(colors.HexColor('#424242'))
    c.setFont("Helvetica", 16)
    
    # Convertir fecha a español
    months_es = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo',
        'April': 'abril', 'May': 'mayo', 'June': 'junio',
        'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
        'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    
    now = datetime.now()
    month_en = now.strftime('%B')
    month_es = months_es.get(month_en, month_en)
    date_str = f"{now.day} de {month_es} de {now.year}"
    
    date_text = f"Fecha de finalización: {date_str}"
    date_width = c.stringWidth(date_text, "Helvetica", 16)
    c.drawString((width - date_width) / 2, height - 420, date_text)
    
    # Sello/Logo Edify
    c.setFillColor(colors.HexColor('#ffd700'))
    c.circle(width / 2, 120, 50, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#1a237e'))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, 115, "EDIFY")
    
    # Firma del instructor
    c.setStrokeColor(colors.HexColor('#1a237e'))
    c.setLineWidth(1)
    c.line(100, 80, 250, 80)
    c.setFillColor(colors.HexColor('#424242'))
    c.setFont("Helvetica", 12)
    instructor_name = course.owner.get_full_name() or course.owner.username
    instructor_text = f"Instructor: {instructor_name}"
    c.drawCentredString(175, 65, instructor_text)
    
    # ID único del certificado
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor('#9e9e9e'))
    cert_id = f"Certificado ID: {course.id}-{user.id}-{now.strftime('%Y%m%d')}"
    c.drawRightString(width - 60, 30, cert_id)
    
    # Finalizar PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
