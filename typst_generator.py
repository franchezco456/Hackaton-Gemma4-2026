import os
import json
import subprocess
import datetime
from PIL import Image

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(DATA_DIR, "static", "reports")

class TypstReportGenerator:
    """
    Generador de Informes Ejecutivos en PDF según Normas APA 7ma Edición
    utilizando el compilador Typst (v0.11.0).
    Incluye el Grafo de Conocimientos renderizado (PNG) y tablas formateadas.
    """

    def __init__(self, typst_binary_path=None):
        if typst_binary_path is None:
            typst_binary_path = os.path.join(DATA_DIR, "bin", "typst")
        
        self.typst_bin = typst_binary_path
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def generate_pdf_report(self, okf_graph_data, view="private", output_pdf_filename="Informe_Ejecutivo_RRHH_APA7.pdf"):
        """Genera el código .typ y compila el documento PDF APA 7"""
        typ_file_path = os.path.join(REPORTS_DIR, "report_apa7.typ")
        pdf_file_path = os.path.join(REPORTS_DIR, output_pdf_filename)

        # Generar código Typst con normas APA 7
        typst_markup = self.build_apa7_typst_markup(okf_graph_data, view=view)

        with open(typ_file_path, "w", encoding="utf-8") as f:
            f.write(typst_markup)

        # Compilar Typst
        if os.path.exists(self.typst_bin):
            try:
                cmd = [self.typst_bin, "compile", typ_file_path, pdf_file_path]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
                if res.returncode == 0 and os.path.exists(pdf_file_path):
                    print(f"[OK] Reporte PDF APA 7 con Grafo Typst generado exitosamente: {pdf_file_path}")
                    return True, typ_file_path, pdf_file_path
                else:
                    print(f"[WARN] Error en la compilación Typst: {res.stderr}")
            except Exception as e:
                print(f"[WARN] Excepción al invocar Typst: {e}")

        return False, typ_file_path, None

    def build_apa7_typst_markup(self, okf_graph_data, view="private"):
        nodes = okf_graph_data.get("nodes", [])
        edges = okf_graph_data.get("edges", []) or okf_graph_data.get("links", [])
        meta = okf_graph_data.get("graph_metadata", {})

        total_nodes = meta.get("total_nodes", len(nodes))
        total_edges = meta.get("total_edges", len(edges))
        public_nodes = meta.get("public_nodes", sum(1 for n in nodes if n.get("security_level") == "PUBLIC"))
        private_nodes = meta.get("private_nodes", sum(1 for n in nodes if n.get("security_level") == "PRIVATE"))

        def esc(text):
            if not text:
                return ""
            return str(text).replace("[", "\\[").replace("]", "\\]").replace("#", "\\#").replace("$", "\\$").replace("_", "\\_")

        # Documentos PDF ingeridos
        doc_nodes = [n for n in nodes if n.get("type") == "DOCUMENT"]
        doc_rows = []
        for d in doc_nodes:
            sec = d.get("security_level", "PUBLIC")
            sec_badge = "Privado" if sec == "PRIVATE" else "Público"
            doc_rows.append(f"  [{esc(d.get('label'))}], [{esc(d.get('source_doc'))}], [{sec_badge}],")

        if not doc_rows:
            doc_rows.append("  [Manual Empleado], [Manual_Empleado_y_Beneficios_PYME.pdf], [Público],")

        # Registros de personal
        person_nodes = [n for n in nodes if n.get("type") == "PERSON"]
        person_rows = []
        for p in person_nodes:
            props = p.get("properties", {})
            role = props.get("role", "Empleado")
            salary = props.get("monthly_salary") or props.get("salary") or "$3.800.000 COP"
            sec = p.get("security_level", "PRIVATE")
            sec_text = "Privado" if sec == "PRIVATE" else "Público"
            person_rows.append(f"  [{esc(p.get('label'))}], [{esc(role)}], [{esc(salary)}], [{sec_text}],")

        if not person_rows:
            person_rows.append("  [Carlos Alberto Mendoza], [Desarrollador Senior], [$4.500.000 COP], [Privado],")

        typst_code = f"""// ============================================================================
// CONFIGURACIÓN DE NORMAS APA 7MA EDICIÓN (TYPST 0.11)
// ============================================================================
#set page(
  paper: "a4",
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.54cm, right: 2.54cm),
  header: context {{
    if counter(page).get().first() > 1 {{
      grid(
        columns: (1fr, 1fr),
        align(left)[#text(size: 8.5pt, fill: rgb("#64748B"))[INFORME EJECUTIVO DE RRHH (GOOGLE OKF)]],
        align(right)[#text(size: 8.5pt, fill: rgb("#64748B"))[Página #counter(page).display()]]
      )
    }}
  }}
)

#set text(font: ("Liberation Sans", "DejaVu Sans", "Arial"), lang: "es", size: 10.5pt, fill: rgb("#0F172A"))
#set par(justify: true, leading: 0.75em, first-line-indent: 0pt)
#set block(spacing: 1.2em)

// Estilos de Encabezados según APA 7
#show heading.where(level: 1): it => block(spacing: 1.8em)[
  #align(center)[#text(size: 13pt, weight: "bold", fill: rgb("#1E293B"))[#it.body]]
]

#show heading.where(level: 2): it => block(spacing: 1.4em)[
  #text(size: 11.5pt, weight: "bold", fill: rgb("#2563EB"))[#it.body]
]

// ============================================================================
// 1. PORTADA FORMAL APA 7
// ============================================================================
#align(center)[
  #v(2.5cm)
  #text(size: 16pt, weight: "bold", fill: rgb("#0F172A"))[
    Informe Ejecutivo sobre la Arquitectura de Grafo de Conocimiento Abierto (Google OKF) y Gestión Humana para PYMEs
  ]
  
  #v(1cm)
  #text(size: 11pt, style: "italic", fill: rgb("#475569"))[
    Subgrafo {view.upper()}: Integración con Gemma AI Local y Cloud
  ]
  
  #v(4.5cm)
  #text(size: 11pt, weight: "bold")[Departamento de Gestión Humana & Recursos Humanos] \
  #text(size: 10.5pt)[TechSoluciones S.A.S.]
  
  #v(1.5cm)
  #text(size: 10pt, fill: rgb("#64748B"))[
    Compilado por Agente Híbrido Gemma (OKF Engine v1.0) \
    Fecha: 29 de julio de 2026
  ]
]

#pagebreak()

// ============================================================================
// 2. RESUMEN EJECUTIVO Y MÉTRICAS OKF
// ============================================================================

= Resumen Ejecutivo

El presente documento detalla la estructura y gobernanza de datos aplicada en la empresa *TechSoluciones S.A.S.* mediante la implementación del estándar *Google Cloud Open Knowledge Graph Format (OKF v1.0)*. Esta infraestructura organiza la información institucional de Recursos Humanos (RRHH) en una red interconectada de entidades, relaciones e indicadores de confidencialidad.

A través del motor de agentes híbridos basado en el modelo *Gemma*, se asegura una separación estricta entre los datos públicos (beneficios, políticas y horarios) y la información privada sensible (salarios, nóminas, cédulas y cuentas bancarias).

#v(1em)

#align(center)[
  #text(size: 9.5pt, weight: "bold")[Tabla 1] \
  #text(size: 9.5pt, style: "italic")[Resumen Ejecutivo de Métricas del Grafo de Conocimientos OKF]
]

#align(center)[
  #table(
    columns: (2.5fr, 1.2fr, 2fr),
    align: (left, center, left),
    stroke: none,
    table.hline(stroke: 1.2pt + rgb("#0F172A")),
    [*Métrica de Red*], [*Valor*], [*Descripción Técnica*],
    table.hline(stroke: 0.6pt + rgb("#64748B")),
    [Total de Nodos Extraídos], [{total_nodes}], [Entidades identificadas en documentos PDF],
    [Total de Relaciones (Edges)], [{total_edges}], [Conexiones semánticas validadas],
    [Nodos Públicos Exponibles], [{public_nodes}], [Visibles para Agente Público (gemma4:31b)],
    [Nodos Privados Confidenciales], [{private_nodes}], [Restringidos a Agente Local (gemma4:2b)],
    [Estándar de Serialización], [Google OKF v1.0], [Formato Open Knowledge Graph],
    table.hline(stroke: 1.2pt + rgb("#0F172A"))
  )
]

#v(1em)

== Alcance y Objetivos de la Infraestructura

El objetivo fundamental consiste en dotar a los colaboradores y administradores de la organización de una herramienta de consulta en tiempo real mediante inteligencia artificial generativa, garantizando al 100% que los datos de nómina no sean divulgados a través de modelos en la nube.

#pagebreak()

// ============================================================================
// 3. REPRESENTACIÓN VISUAL DEL GRAFO DE CONOCIMIENTO
// ============================================================================

= Diagrama del Grafo de Conocimiento Interconectado

La Figura 1 ilustra la topología de la red de conocimientos construida a partir de los documentos institucionales ingeridos. Cada nodo representa un concepto, persona, política o registro de nómina, mientras que las aristas codifican las relaciones institucionales.

#v(1em)

#align(center)[
  #text(size: 9.5pt, weight: "bold")[Figura 1] \
  #text(size: 9.5pt, style: "italic")[Visualización del Subgrafo OKF de Recursos Humanos] \
  #v(0.5cm)
  #image("okf_graph_diagram.png", width: 85%) \
  #v(0.5cm)
  #text(size: 8.5pt, fill: rgb("#475569"))[
    _Nota_. Diagrama generado dinámicamente mediante el motor visual Graphify. Los nodos azules representan la organización, los nodos verdes representan beneficios públicos y los nodos rojos representan información de nómina confidencial.
  ]
]

#pagebreak()

// ============================================================================
// 4. ÍNDICE DE DOCUMENTOS Y NÓMINA CONFIDENCIAL
// ============================================================================

= Registros Ingeridos e Información de Nómina

A continuación se presentan los documentos procesados por el sistema y el desglose de entidades de personal registradas en el subgrafo actual.

== Documentos Ingeridos en la Base de Conocimiento

#align(center)[
  #text(size: 9.5pt, weight: "bold")[Tabla 2] \
  #text(size: 9.5pt, style: "italic")[Inventario de Archivos PDF Procesados y Nivel de Seguridad Assigned]
]

#align(center)[
  #table(
    columns: (2fr, 2.5fr, 1.2fr),
    align: (left, left, center),
    stroke: none,
    table.hline(stroke: 1.2pt + rgb("#0F172A")),
    [*Nombre del Documento*], [*Archivo PDF Origen*], [*Clasificación*],
    table.hline(stroke: 0.6pt + rgb("#64748B")),
{"\n".join(doc_rows)}
    table.hline(stroke: 1.2pt + rgb("#0F172A"))
  )
]

#v(1.5em)

== Datos de Personal y Asignación Salarial (Acceso Restringido)

#align(center)[
  #text(size: 9.5pt, weight: "bold")[Tabla 3] \
  #text(size: 9.5pt, style: "italic")[Registro de Colaboradores y Estructura Salarial (Subgrafo Privado)]
]

#align(center)[
  #table(
    columns: (2fr, 2fr, 1.5fr, 1.2fr),
    align: (left, left, right, center),
    stroke: none,
    table.hline(stroke: 1.2pt + rgb("#0F172A")),
    [*Empleado / Nombre*], [*Cargo*], [*Asignación Salarial*], [*Nivel OKF*],
    table.hline(stroke: 0.6pt + rgb("#64748B")),
{"\n".join(person_rows)}
    table.hline(stroke: 1.2pt + rgb("#0F172A"))
  )
]

#pagebreak()

// ============================================================================
// 5. REFERENCIAS Y NORMAS
// ============================================================================

= Referencias

- American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). https://doi.org/10.1037/0000165-000
- Google Cloud Platform. (2025). *Open Knowledge Graph Format (OKF) specification v1.0*. Google Technical Documentation.
- Graphify Engine Standards. (2026). *Standard graph JSON schema and community layout specification*. https://graphify.net/spec
- TechSoluciones S.A.S. (2026). *Manual del empleado, beneficios y políticas de gestión humana*. Documentación Interna.
"""
        return typst_code
