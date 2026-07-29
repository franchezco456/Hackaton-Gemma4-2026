// ============================================================================
// CONFIGURACIÓN DE NORMAS APA 7MA EDICIÓN (TYPST 0.11)
// ============================================================================
#set page(
  paper: "a4",
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.54cm, right: 2.54cm),
  header: context {
    if counter(page).get().first() > 1 {
      grid(
        columns: (1fr, 1fr),
        align(left)[#text(size: 8.5pt, fill: rgb("#64748B"))[INFORME EJECUTIVO DE RRHH (GOOGLE OKF)]],
        align(right)[#text(size: 8.5pt, fill: rgb("#64748B"))[Página #counter(page).display()]]
      )
    }
  }
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
    Subgrafo PRIVATE: Integración con Gemma AI Local y Cloud
  ]
  
  #v(4.5cm)
  #text(size: 11pt, weight: "bold")[Departamento de Gestión Humana & Recursos Humanos]   #text(size: 10.5pt)[TechSoluciones S.A.S.]
  
  #v(1.5cm)
  #text(size: 10pt, fill: rgb("#64748B"))[
    Compilado por Agente Híbrido Gemma (OKF Engine v1.0)     Fecha: 29 de julio de 2026
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
  #text(size: 9.5pt, weight: "bold")[Tabla 1]   #text(size: 9.5pt, style: "italic")[Resumen Ejecutivo de Métricas del Grafo de Conocimientos OKF]
]

#align(center)[
  #table(
    columns: (2.5fr, 1.2fr, 2fr),
    align: (left, center, left),
    stroke: none,
    table.hline(stroke: 1.2pt + rgb("#0F172A")),
    [*Métrica de Red*], [*Valor*], [*Descripción Técnica*],
    table.hline(stroke: 0.6pt + rgb("#64748B")),
    [Total de Nodos Extraídos], [22], [Entidades identificadas en documentos PDF],
    [Total de Relaciones (Edges)], [21], [Conexiones semánticas validadas],
    [Nodos Públicos Exponibles], [11], [Visibles para Agente Público (gemma4:31b)],
    [Nodos Privados Confidenciales], [11], [Restringidos a Agente Local (gemma4:2b)],
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
  #text(size: 9.5pt, weight: "bold")[Figura 1]   #text(size: 9.5pt, style: "italic")[Visualización del Subgrafo OKF de Recursos Humanos]   #v(0.5cm)
  #image("okf_graph_diagram.png", width: 85%)   #v(0.5cm)
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
  #text(size: 9.5pt, weight: "bold")[Tabla 2]   #text(size: 9.5pt, style: "italic")[Inventario de Archivos PDF Procesados y Nivel de Seguridad Assigned]
]

#align(center)[
  #table(
    columns: (2fr, 2.5fr, 1.2fr),
    align: (left, left, center),
    stroke: none,
    table.hline(stroke: 1.2pt + rgb("#0F172A")),
    [*Nombre del Documento*], [*Archivo PDF Origen*], [*Clasificación*],
    table.hline(stroke: 0.6pt + rgb("#64748B")),
  [📄 Nomina Salarios y Evaluaciones 2025], [Nomina\_Salarios\_y\_Evaluaciones\_2025.pdf], [Privado],
  [📄 William Shakespeare Romeo y Julieta], [William Shakespeare Romeo y Julieta.pdf], [Privado],
  [📄 Nuevo Plan Mascota 2026], [Nuevo\_Plan\_Mascota\_2026.pdf], [Público],
  [📄 Politica Acoso y Codigo Conducta], [Politica\_Acoso\_y\_Codigo\_Conducta.pdf], [Público],
  [📄 Manual Empleado y Beneficios PYME], [Manual\_Empleado\_y\_Beneficios\_PYME.pdf], [Público],
  [📄 Contratos Laborales y Datos Personales], [Contratos\_Laborales\_y\_Datos\_Personales.pdf], [Privado],
  [📄 Politica Vacaciones Publica Test], [Politica\_Vacaciones\_Publica\_Test.pdf], [Público],
  [📄 Politica de Vacaciones], [Politica\_de\_Vacaciones.pdf], [Privado],
  [📄 Manual-del-Empleado], [Manual-del-Empleado.pdf], [Privado],
    table.hline(stroke: 1.2pt + rgb("#0F172A"))
  )
]

#v(1.5em)

== Datos de Personal y Asignación Salarial (Acceso Restringido)

#align(center)[
  #text(size: 9.5pt, weight: "bold")[Tabla 3]   #text(size: 9.5pt, style: "italic")[Registro de Colaboradores y Estructura Salarial (Subgrafo Privado)]
]

#align(center)[
  #table(
    columns: (2fr, 2fr, 1.5fr, 1.2fr),
    align: (left, left, right, center),
    stroke: none,
    table.hline(stroke: 1.2pt + rgb("#0F172A")),
    [*Empleado / Nombre*], [*Cargo*], [*Asignación Salarial*], [*Nivel OKF*],
    table.hline(stroke: 0.6pt + rgb("#64748B")),
  [Juan Pablo Martínez (Gerente Operaciones)], [Gerente de Operaciones y Logística], [\$4,800 USD / mes], [Privado],
  [Laura Gómez (Directora RRHH)], [Directora de Recursos Humanos (RRHH)], [\$3,900 USD / mes], [Privado],
  [Andrés Felipe Silva (Dev Senior)], [Desarrollador Senior de Software], [\$3,200 USD / mes], [Privado],
  [Juan Pablo Mart], [Empleado], [\$3.800.000 COP], [Privado],
  [Juan Pablo Mart], [Empleado], [\$3.800.000 COP], [Privado],
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
