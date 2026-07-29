import os
import subprocess

DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")

HR_SAMPLE_DOCS = {
    "Manual_Empleado_y_Beneficios_PYME.pdf": """
================================================================================
MANUAL DEL EMPLEADO Y PROGRAMA DE BENEFICIOS DE RECURSOS HUMANOS (RRHH) 2025
================================================================================
Clasificación de Documento: PÚBLICO / USO GENERAL
Empresa: TechSoluciones S.A.S. - Departamento de Gestión Humana
Contacto de RRHH: rrhh@techsoluciones.com.co | Tel: +57 (601) 555-0199 Ext 102
Directora de Gestión Humana: Laura Gómez

PROGRAMA DE BENEFICIOS PARA EMPLEADOS:
--------------------------------------------------------------------------------
1. Beneficio: Horario Flexible y Teletrabajo Híbrido
   - Descripción: Jornada laboral de 8:00 AM a 5:00 PM con 2 días de trabajo remoto a la semana.
   - Aplicabilidad: Todos los empleados contratados a término indefinido.

2. Beneficio: Seguro Médico Prepagado y Odontología
   - Descripción: Cobertura del 100% de la póliza de salud prepagada para el empleado.
   - Plan: Seguro Médico SaludTotal Plan Excelencia.

3. Beneficio: Día de Cumpleaños Libre y Vacaciones
   - Descripción: Día libre remunerado en la fecha del cumpleaños.
   - Vacaciones: 15 días hábiles remunerados de vacaciones al año tras cumplir 1 año de antigüedad.
   - Auxilio Educativo: Hasta $500 USD anuales para cursos de capacitación profesional.

PROCEDIMIENTO DE SOLICITUD DE VACACIONES Y PERMISOS:
- Solicitar con mínimo 15 días de anticipación mediante el Portal de Recursos Humanos.
- Aprobación por parte del jefe directo y confirmación del equipo de RRHH en 48 horas.
================================================================================
""",

    "Nomina_Salarios_y_Evaluaciones_2025.pdf": """
================================================================================
NÓMINA SALARIAL, BONOS Y EVALUACIONES DE DESEMPEÑO CONFIDENCIALES 2025
================================================================================
Clasificación de Documento: PRIVADO / ESTRICTAMENTE CONFIDENCIAL
Uso Exclusivo: Dirección de Recursos Humanos y Gerencia General
PROHIBIDA SU DIVULGACIÓN A EXTERNOS O EMPLEADOS NO AUTORIZADOS.

REGISTRO DE NÓMINA Y SALARIOS MENSUALES (CONFIDENCIAL):
--------------------------------------------------------------------------------
1. Empleado: Juan Pablo Martínez
   - Cargo: Gerente de Operaciones y Logística
   - Salario Mensual Neto: $4,800 USD / mes
   - Bono por Rendimiento Q1: $8,000 USD
   - Calificación Evaluación de Desempeño: 95/100 (Sobresaliente)

2. Empleada: Laura Gómez
   - Cargo: Directora de Recursos Humanos (RRHH)
   - Salario Mensual Neto: $3,900 USD / mes
   - Bono por Retención de Talento: $3,500 USD
   - Calificación Evaluación de Desempeño: 98/100 (Excelente)

3. Empleado: Andrés Felipe Silva
   - Cargo: Desarrollador Senior de Software
   - Salario Mensual Neto: $3,200 USD / mes
   - Aumento Salarial Proyectado 2025: 12%

4. Empleada: Sofía Morales
   - Cargo: Analista de Recursos Humanos y Nómina
   - Salario Mensual Neto: $1,800 USD / mes
   - Calificación Evaluación de Desempeño: 90/100 (Cumple Objetivos)

MARGENES DE AUMENTO PRESUPUESTARIO PARA RECURSOS HUMANOS:
- Presupuesto Total Anual para Nómina 2025: $280,000 USD.
- Fondo de Reserva para Indemnizaciones y Retiro: $45,000 USD.
================================================================================
""",

    "Politica_Acoso_y_Codigo_Conducta.pdf": """
================================================================================
CÓDIGO DE CONDUCTA LABORAL Y POLÍTICA DE PREVENCIÓN DE ACOSO (RRHH)
================================================================================
Clasificación de Documento: PÚBLICO / GENERAL
Vigencia: Año 2025 - 2026

CÓDIGO DE CONVIVENCIA Y ÉTICA LABORAL:
--------------------------------------------------------------------------------
- Comité de Convivencia Laboral: Encargado de recibir y gestionar quejas de convivencia o clima laboral.
- Canal Anónimo de Denuncias: etica@techsoluciones.com.co
- Principios Fundamentales: Respeto mutuo, no discriminación, equidad de género y trabajo en equipo.
- Protocolo de Resolución de Conflictos: Mediación en 3 etapas en un plazo máximo de 5 días hábiles.
================================================================================
""",

    "Contratos_Laborales_y_Datos_Personales.pdf": """
================================================================================
EXPEDIENTES DE CONTRATACIÓN Y DATOS PERSONALES DE EMPLEADOS (CONFIDENCIAL)
================================================================================
Clasificación de Documento: PRIVADO / SECRETO DE EMPRESA
Acceso Restringido: Equipo de Gestión Humana y RRHH.

DATOS PERSONALES Y BANCARIOS DE EMPLEADOS:
--------------------------------------------------------------------------------
- Empleado: Juan Pablo Martínez | Cédula: 1.018.452.890
  - Dirección Residencia: Carrera 15 # 104-20, Apt 302, Bogotá
  - Cuenta Bancaria Nómina: Bancolombia Ahorros N° 458-901234-89
  - Contacto de Emergencia: Claudia Martínez (Esposa) - Tel: +57 311 455-8900

- Empleada: Laura Gómez | Cédula: 52.890.123
  - Dirección Residencia: Calle 127 # 45-12, Bogotá
  - Cuenta Bancaria Nómina: Davivienda Ahorros N° 005-123489-01
  - Contacto de Emergencia: Roberto Gómez (Padre) - Tel: +57 300 211-9988

PROCESO DISCIPLINARIO Y REGLAMENTO INTERNO DE TRABAJO:
- Faltas Graves: Divulgación de datos personales de nómina, falsificación de justificantes médicos o ausencia injustificada por más de 3 días consecutivos.
- Sanción: Terminación del contrato laboral con justa causa sin indemnización.
================================================================================
"""
}

def generate_pdf_from_text(text, output_pdf_path):
    """Genera un archivo PDF a partir de texto usando groff/ps2pdf o escritura limpia."""
    try:
        p1 = subprocess.Popen(["groff", "-Tps"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ps_data, err = p1.communicate(input=text.encode("utf-8"))
        
        if p1.returncode == 0 and ps_data:
            p2 = subprocess.Popen(["ps2pdf", "-", output_pdf_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err2 = p2.communicate(input=ps_data)
            if p2.returncode == 0:
                print(f"[OK] Generado PDF RRHH: {output_pdf_path}")
                return True
    except Exception:
        pass

    return generate_fallback_pdf(text, output_pdf_path)

def generate_fallback_pdf(text, output_pdf_path):
    lines = text.strip().split("\n")
    cleaned_lines = [l.replace("(", "\\(").replace(")", "\\)") for l in lines]
    
    content_stream = "BT /F1 10 Tf 12 TL 40 750 Td\n"
    for line in cleaned_lines[:50]:
        content_stream += f"({line[:90]}) '\n"
    content_stream += "ET"

    content_bytes = content_stream.encode("latin-1", errors="replace")
    stream_len = len(content_bytes)

    pdf_body = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>
endobj
5 0 obj
<< /Length {stream_len} >>
stream
{content_stream}
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000315 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
{400 + stream_len}
%%EOF
"""
    with open(output_pdf_path, "wb") as f:
        f.write(pdf_body.encode("latin-1", errors="replace"))
    print(f"[OK] Generado PDF RRHH (Fallback): {output_pdf_path}")
    return True

def create_sample_documents():
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    
    # Limpiar documentos viejos de software
    for f in os.listdir(DOCUMENTS_DIR):
        if f.endswith(".pdf"):
            try:
                os.remove(os.path.join(DOCUMENTS_DIR, f))
            except Exception:
                pass

    created = []
    for filename, text in HR_SAMPLE_DOCS.items():
        pdf_path = os.path.join(DOCUMENTS_DIR, filename)
        generate_pdf_from_text(text, pdf_path)
        created.append(pdf_path)
    return created

if __name__ == "__main__":
    create_sample_documents()
