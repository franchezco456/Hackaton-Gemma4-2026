
#set page(
  paper: "a4",
  margin: (x: 1.8cm, top: 2.2cm, bottom: 2.2cm),
  header: align(right, text(fill: rgb("#64748B"), size: 8pt)[
    *TechSoluciones S.A.S.* | Sistema Híbrido de Gestión Humana OKF
  ]),
  footer: [
    #set text(fill: rgb("#64748B"), size: 8pt)
    #grid(
      columns: (1fr, 1fr),
      align(left)[Documento Generado vía *Typst PDF Engine*],
      align(right)[Página #counter(page).display()],
    )
  ]
)

#set text(font: "DejaVu Sans", lang: "es", size: 9.5pt)

// Banner de Cabecera Corporativo
#rect(width: 100%, fill: rgb("#0F172A"), inset: 14pt, radius: 6pt)[
  #grid(
    columns: (1fr, auto),
    align(left)[
      #text(fill: rgb("#3B82F6"), weight: "bold", size: 15pt)[
        INFORME EJECUTIVO DE RECURSOS HUMANOS (RRHH)
      ]       #v(2pt)
      #text(fill: rgb("#F8FAFC"), size: 10pt, weight: "medium")[
        Grafo de Conocimiento Google Cloud OKF v1.0 & Graphify Engine
      ]       #v(3pt)
      #text(fill: rgb("#94A3B8"), size: 8.5pt)[
        Nivel de Acceso: *VISTA COMPLETA INTERNA (PRIVADA)* | Fecha: 29/07/2026
      ]
    ],
    align(right + horizon)[
      #rect(fill: rgb("#1E293B"), stroke: rgb("#334155"), inset: 8pt, radius: 4pt)[
        #text(fill: rgb("#38BDF8"), size: 9pt, weight: "bold")[Gemma AI]
      ]
    ]
  )
]

#v(8pt)

// Métricas Principales en Cuadrícula Typst
#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  gutter: 8pt,
  rect(width: 100%, fill: rgb("#F8FAFC"), stroke: rgb("#E2E8F0"), inset: 8pt, radius: 4pt)[
    #align(center)[
      #text(fill: rgb("#2563EB"), size: 13pt, weight: "bold")[18]       #text(fill: rgb("#64748B"), size: 7.5pt)[Nodos Totales OKF]
    ]
  ],
  rect(width: 100%, fill: rgb("#F8FAFC"), stroke: rgb("#E2E8F0"), inset: 8pt, radius: 4pt)[
    #align(center)[
      #text(fill: rgb("#2563EB"), size: 13pt, weight: "bold")[17]       #text(fill: rgb("#64748B"), size: 7.5pt)[Relaciones OKF]
    ]
  ],
  rect(width: 100%, fill: rgb("#FFF1F2"), stroke: rgb("#FECDD3"), inset: 8pt, radius: 4pt)[
    #align(center)[
      #text(fill: rgb("#E11D48"), size: 13pt, weight: "bold")[9]       #text(fill: rgb("#9F1239"), size: 7.5pt)[🔒 Nodos Privados]
    ]
  ],
  rect(width: 100%, fill: rgb("#ECFDF5"), stroke: rgb("#A7F3D0"), inset: 8pt, radius: 4pt)[
    #align(center)[
      #text(fill: rgb("#059669"), size: 13pt, weight: "bold")[9]       #text(fill: rgb("#065F46"), size: 7.5pt)[🌐 Nodos Públicos]
    ]
  ]
)

#v(10pt)

== 📄 Índice de Documentos de RRHH Ingeridos

#table(
  columns: (2fr, 2fr, 1fr),
  fill: (x, y) => if y == 0 { rgb("#F1F5F9") } else { none },
  stroke: rgb("#E2E8F0"),
  [ *Título del Documento* ], [ *Archivo PDF Fuente* ], [ *Seguridad* ],
  [📄 Nomina Salarios y Evaluaciones 2025], [Nomina_Salarios_y_Evaluaciones_2025.pdf], [[🔒 Privado]],  [📄 Politica Acoso y Codigo Conducta], [Politica_Acoso_y_Codigo_Conducta.pdf], [[🌐 Público]],  [📄 Manual Empleado y Beneficios PYME], [Manual_Empleado_y_Beneficios_PYME.pdf], [[🌐 Público]],  [📄 Contratos Laborales y Datos Personales], [Contratos_Laborales_y_Datos_Personales.pdf], [[🔒 Privado]],  [📄 Manual-del-Empleado], [Manual-del-Empleado.pdf], [[🔒 Privado]],
)

#v(10pt)

== 👥 Registro de Personal y Nómina Salarial (Estructura OKF)

#table(
  columns: (2fr, 2fr, 1.5fr, 1fr),
  fill: (x, y) => if y == 0 { rgb("#F1F5F9") } else { none },
  stroke: rgb("#E2E8F0"),
  [ *Nombre del Empleado* ], [ *Cargo / Función* ], [ *Remuneración Mensual* ], [ *Acceso* ],
  [Juan Pablo Martínez (Gerente Operaciones)], [Gerente de Operaciones y Logística], [\$4,800 USD / mes], [🔒 Privado],  [Laura Gómez (Directora RRHH)], [Directora de Recursos Humanos (RRHH)], [\$3,900 USD / mes], [🔒 Privado],  [Andrés Felipe Silva (Dev Senior)], [Desarrollador Senior de Software], [\$3,200 USD / mes], [🔒 Privado],  [Juan Pablo Mart], [Empleado], [Confidencial], [🔒 Privado],  [Juan Pablo Mart], [Empleado], [Confidencial], [🔒 Privado],
)

#v(10pt)

== 🎁 Programa de Beneficios y Políticas Generales de Personal

#table(
  columns: (2fr, 3fr, 1fr),
  fill: (x, y) => if y == 0 { rgb("#F1F5F9") } else { none },
  stroke: rgb("#E2E8F0"),
  [ *Programa de Beneficio* ], [ *Descripción y Alcance* ], [ *Acceso* ],
  [Horario Flexible y Trabajo Híbrido], [Beneficio laboral de trabajo remoto híbrido y flexibilidad de horario.], [🌐 Público],  [Seguro Médico Prepagado 100%], [Póliza de medicina prepagada cubierta en su totalidad por la PYME.], [🌐 Público],  [Vacaciones (15 Días) y Cumpleaños Libre], [Política de vacaciones anuales, auxilio educativo y día de cumpleaños.], [🌐 Público],  [Horario Flexible y Trabajo Híbrido], [Beneficio laboral de trabajo remoto híbrido y flexibilidad de horario.], [🌐 Público],  [Seguro Médico Prepagado 100%], [Póliza de medicina prepagada cubierta en su totalidad por la PYME.], [🌐 Público],  [Vacaciones (15 Días) y Cumpleaños Libre], [Política de vacaciones anuales, auxilio educativo y día de cumpleaños.], [🌐 Público],
)

#v(14pt)

#line(length: 100%, stroke: 0.5pt + rgb("#CBD5E1"))

#v(4pt)
#text(fill: rgb("#94A3B8"), size: 7.5pt)[
  *Nota de Confidencialidad*: Este informe ha sido compilado utilizando la arquitectura híbrida Gemma AI. Los nodos marcados como 🔒 Privado sólo son accesibles para la Dirección de Gestión Humana.
]
