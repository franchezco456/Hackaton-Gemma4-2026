
// ============================================================================
// CONFIGURACIÓN DE FORMATO SEGÚN NORMAS APA 7MA EDICIÓN
// ============================================================================
#set page(
  paper: "a4",
  margin: (top: 2.54cm, bottom: 2.54cm, left: 2.54cm, right: 2.54cm),
  header: locate(loc => {
    if loc.page() > 1 {
      grid(
        columns: (1fr, 1fr),
        align(left)[#text(size: 8.5pt, fill: rgb("#475569"))[GRAFO DE CONOCIMIENTOS DE RRHH (GOOGLE OKF)]],
        align(right)[#text(size: 8.5pt, fill: rgb("#475569"))[#counter(page).display()]]
      )
    }
  })
)

#set text(font: "DejaVu Sans", lang: "es", size: 10.5pt)
#set par(justify: true, leading: 0.7em, first-line-indent: 1.27cm)

// ============================================================================
// PORTADA FORMAL SEGÚN NORMAS APA 7
// ============================================================================
#align(center)[
  #v(3cm)
  #text(size: 16pt, weight: "bold")[
    INFORME EJECUTIVO DE GESTIÓN HUMANA Y RECURSOS HUMANOS (RRHH)
  ]   #v(0.5cm)
  #text(size: 12pt, style: "italic")[
    Estructura de Grafo de Conocimientos Interconectado según el Estándar Google Cloud Open Knowledge Graph Format (v1.0) y Motor Graphify
  ]   #v(4cm)
  #text(size: 11pt, weight: "bold")[
    Departamento de Gestión Humana y Recursos Humanos (RRHH)
  ]   #text(size: 10.5pt)[
    TechSoluciones S.A.S.
  ]   #v(1cm)
  #text(size: 10.5pt)[
    Agente Híbrido de Inteligencia Artificial Gemma (gemma4:2b / gemma4:31b-cloud)
  ]   #v(0.5cm)
  #text(size: 10.5pt)[
    29 de julio de 2026
  ]
]

#pagebreak()

// ============================================================================
// CONTENIDO DEL INFORME (ESTILO APA 7)
// ============================================================================

= Resumen Ejecutivo

El presente informe expone la organización del conocimiento institucional del Departamento de Recursos Humanos (RRHH) de la empresa TechSoluciones S.A.S. La arquitectura técnica implementada ingested la carpeta de documentos en formato PDF y los transforma al estándar *Google Cloud Open Knowledge Graph Format (OKF v1.0)*. Mediante un sistema de doble agente de inteligencia artificial (Gemma Local `gemma4:2b` para consultas privadas y Gemma Cloud `gemma4:31b-cloud` para consultas públicas), se garantiza el aislamiento estricto de los datos confidenciales de nómina y contratos laborales.

#v(1em)

*Tabla 1* _Métricas Generales del Grafo de Conocimientos OKF de Recursos Humanos_
#table(
  columns: (2.5fr, 1.5fr, 1.5fr),
  stroke: (x, y) => if y == 0 { (top: 1pt + black, bottom: 0.5pt + black) } else if y == 4 { (bottom: 1pt + black) } else { none },
  fill: none,
  [ *Métrica de Infraestructura* ], [ *Valor Registrado* ], [ *Nivel de Seguridad* ],
  [ Nodos Totales Ingeridos ], [ 21 ], [ Estándar Google OKF ],
  [ Aristas (Relaciones Interconectadas) ], [ 20 ], [ Grafo Graphify ],
  [ Nodos Confidenciales de Nómina ], [ 11 ], [ 🔒 Privado (`gemma4:2b`) ],
  [ Nodos Públicos de Beneficios ], [ 10 ], [ 🌐 Público (`gemma4:31b-cloud`) ]
)
#text(size: 8.5pt, style: "italic")[Nota. Adaptado del estándar oficial Google Cloud Open Knowledge Graph Format (v1.0).]

#v(1.5em)

= Diagrama del Grafo de Conocimientos (OKF & Graphify)

Para cumplir con la representación gráfica exigida en los informes técnicos APA 7, la Figura 1 ilustra el grafo interconectado de entidades, personas, beneficios y documentos.

#v(1em)

*Figura 1* _Grafo Interconectado de Conocimientos de Recursos Humanos y Seguridad de Nodos_

#align(center)[
  #image("okf_graph_diagram.png", width: 92%)
]
#text(size: 8.5pt, style: "italic")[Nota. Nodos rojos (🔒 Privados) representan registros salariales de acceso restringido al agente local. Nodos verdes (🌐 Públicos) representan beneficios corporativos procesados por el agente cloud.]

#pagebreak()

= Índice de Documentos Fuentes e Registro Salarial

*Tabla 2* _Índice de Documentos PDF Ingeridos y Clasificación de Seguridad_
#table(
  columns: (2.5fr, 2.5fr, 1.2fr),
  stroke: (x, y) => if y == 0 { (top: 1pt + black, bottom: 0.5pt + black) } else { none },
  [ *Título del Documento* ], [ *Archivo PDF de Origen* ], [ *Clasificación* ],
  [📄 Nomina Salarios y Evaluaciones 2025], [Nomina_Salarios_y_Evaluaciones_2025.pdf], [🔒 Privado],  [📄 William Shakespeare Romeo y Julieta], [William Shakespeare Romeo y Julieta.pdf], [🔒 Privado],  [📄 Nuevo Plan Mascota 2026], [Nuevo_Plan_Mascota_2026.pdf], [🌐 Público],  [📄 Politica Acoso y Codigo Conducta], [Politica_Acoso_y_Codigo_Conducta.pdf], [🌐 Público],  [📄 Manual Empleado y Beneficios PYME], [Manual_Empleado_y_Beneficios_PYME.pdf], [🌐 Público],  [📄 Contratos Laborales y Datos Personales], [Contratos_Laborales_y_Datos_Personales.pdf], [🔒 Privado],  [📄 Politica de Vacaciones], [Politica_de_Vacaciones.pdf], [🔒 Privado],  [📄 Manual-del-Empleado], [Manual-del-Empleado.pdf], [🔒 Privado],
)

#v(1.5em)

*Tabla 3* _Registro Salarial y Evaluaciones de Desempeño del Personal (Confidencial)_
#table(
  columns: (2fr, 2fr, 1.5fr, 1.2fr),
  stroke: (x, y) => if y == 0 { (top: 1pt + black, bottom: 0.5pt + black) } else { none },
  [ *Nombre del Empleado* ], [ *Cargo Institucional* ], [ *Salario / Compensación* ], [ *Acceso OKF* ],
  [Juan Pablo Martínez (Gerente Operaciones)], [Gerente de Operaciones y Logística], [\$4,800 USD / mes], [🔒 Privado],  [Laura Gómez (Directora RRHH)], [Directora de Recursos Humanos (RRHH)], [\$3,900 USD / mes], [🔒 Privado],  [Andrés Felipe Silva (Dev Senior)], [Desarrollador Senior de Software], [\$3,200 USD / mes], [🔒 Privado],  [Juan Pablo Mart], [Empleado], [Confidencial], [🔒 Privado],  [Juan Pablo Mart], [Empleado], [Confidencial], [🔒 Privado],
)

#v(1.5em)

= Referencias (Formato APA 7)

#set par(first-line-indent: -1.27cm)
#v(0.5em)

Google Cloud. (2024). *Open Knowledge Graph Format (OKF) Specification (v1.0)*. Google Cloud Documentation. https://cloud.google.com/knowledge-graph

TechSoluciones S.A.S. (2025a). *Manual del Empleado y Programa de Beneficios de Recursos Humanos (RRHH)*. Departamento de Gestión Humana.

TechSoluciones S.A.S. (2025b). *Nómina Salarial, Bonos y Evaluaciones de Desempeño Confidenciales 2025*. Dirección de Recursos Humanos.
