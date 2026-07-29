# 🏢 Plataforma Híbrida de Recursos Humanos: Google Cloud OKF & Agentes Gemma

> **Asistente Inteligente de Recursos Humanos y Gestión Humana (RRHH) para PYMEs** impulsado por el estándar **Google Cloud Open Knowledge Graph Format (OKF v1.0)**, **Graphify**, y un motor híbrido de modelos **Gemma AI** (`gemma4:2b` Local y `gemma4:31b-cloud` Público).

---

## 🌟 Características Principales

1. **🎨 Grafo de Conocimiento Interactivo (Google OKF & Graphify)**:
   - Visualización topológica en tiempo real mediante **Vis.js** y especificación **Graphify** (`graphify.net`).
   - Filtrado dinámico de subgrafos: **`🔒 Subgrafo Privado`** (Nómina, salarios, cédulas y datos confidenciales) vs **`🌐 Subgrafo Público`** (Beneficios, políticas de acoso, horarios y vacantes).
   - Inspección profunda de esquemas JSON estructurados en los visores **Google Cloud OKF (v1.0)** y **`graph.json`**.

2. **💬 Centro de Inteligencia IA Chatbot & Evaluación Dual**:
   - Espacio amplio de conversación con flujo Markdown de alto contraste y citas de documentos PDF originales.
   - **Modos de Agente**:
     - **`☁️ gemma4:31b-cloud (Público)`**: Consultas abiertas de reglamentos y beneficios sin acceso a datos sensibles.
     - **`💻 gemma4:2b (Privado Local)`**: Consultas confidenciales de salarios, aumentos y expedientes.
     - **`⚡ Modo Comparativo Dual (Híbrido)`**: Evaluación simultánea de ambos modelos mostrando cómo el agente Cloud aplica guardrails mientras el agente Local procesa la consulta con autorización.
   - Retardo fluido ajustado (500ms) para una experiencia conversacional natural.

3. **📁 Gestor de Documentos e Ingesta con Clasificación al Subir**:
   - Selector de **Visibilidad al Subir**: Clasifica archivos PDF como `🔒 Privado` o `🌐 Público` en el momento de la carga.
   - **Alternador de Seguridad (Toggle)**: Cambia la confidencialidad de cualquier PDF ingerido con un solo clic y reconstruye automáticamente el grafo OKF.
   - **Descarga Directa de PDFs**: Botón para descargar una copia exacta de cualquier archivo de la base de datos.

4. **📄 Generador de Informes Ejecutivos Typst (Normas APA 7)**:
   - Motor de compilación en tiempo real basado en **Typst v0.11.0**.
   - Produce un PDF ejecutivo de 5 páginas con portada formal, tablas de 3 líneas APA 7, gráfico del mapa semántico (`okf_graph_diagram.png`) y bibliografía.

---

## 📋 Requisitos del Sistema y Prerrequisitos

### 1. Sistema Operativo y Binarios del Sistema
- **Linux** (Ubuntu/Debian recomendado)
- **Python 3.10+**
- **Poppler Utilities** (`pdftotext` para extracción de texto PDF):
  ```bash
  sudo apt-get update && sudo apt-get install -y poppler-utils
  ```

### 2. Typst (Compilador de Reportes PDF)
La plataforma incluye el ejecutable de **Typst v0.11.0** ubicado en `./bin/typst`. Si deseas compilarlo o usar el del sistema:
```bash
typst --version # v0.11.0 o superior
```

### 3. Modelo Local Gemma (Ollama)
Para ejecutar el agente privado local `gemma4:2b`:
1. Instala Ollama: [https://ollama.com](https://ollama.com)
2. Descarga el modelo Gemma:
   ```bash
   ollama pull gemma4:2b
   ```

---

## 🚀 Guía de Instalación y Ejecución Rápida

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/franchezco456/Hackaton-Gemma4-2026.git
cd Hackaton-Gemma4-2026
```

### Paso 2: Instalar Dependencias de Python
Asegúrate de contar con la librería Pillow para el renderizado gráfico del mapa de nodos:
```bash
python3 -m pip install Pillow
```

### Paso 3: Iniciar el Servidor Principal
Ejecuta el servidor web y motor de grafos en Python:
```bash
python3 server.py
```

Al iniciar correctamente verás en la consola:
```text
[OK] Grafo OKF/Graphify cargado exitosamente desde disco.
🚀 Servidor Agente Híbrido OKF Gemma escuchando en http://localhost:8080
```

### Paso 4: Abrir la Aplicación en el Navegador
Abre tu navegador de preferencia en:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 📡 Referencia de la API REST

La plataforma expone los siguientes endpoints REST:

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/status` | Métricas totales de nodos, aristas y división público/privada. |
| `GET` | `/api/documents` | Lista de archivos PDF ingeridos con su clasificación de seguridad. |
| `GET` | `/api/documents/download?file=...` | Descarga el archivo PDF solicitado desde la carpeta `/documents`. |
| `POST` | `/api/documents/toggle-security` | Cambia el estado (`PUBLIC` / `PRIVATE`) de un PDF y reconstruye el grafo OKF. |
| `POST` | `/api/upload` | Sube nuevos archivos PDF en Base64 con clasificación asignada. |
| `POST` | `/api/ingest` | Re-procesa los documentos de la carpeta `/documents` y reconstruye el grafo OKF. |
| `GET` | `/api/graphify?view=public\|private` | Retorna el JSON estándar de Graphify (`graph.json`). |
| `GET` | `/api/okf?view=public\|private` | Retorna la estructura oficial Google Cloud OKF (v1.0). |
| `POST` | `/api/chat` | Consulta a los agentes Gemma (`agent`: `"cloud"`, `"local"`, `"dual"`). |
| `GET` | `/api/export-pdf?view=...` | Compila y descarga el reporte en formato PDF Typst (Normas APA 7). |

---

## 🛠️ Estructura del Proyecto

```text
Hackaton-Gemma4-2026/
├── server.py                        # Servidor HTTP principal y rutas REST
├── graph_manager.py                 # Gestor central de subgrafos OKF y Graphify
├── okf_engine.py                    # Motor de ingesta PDF y serializador Google OKF (v1.0)
├── hybrid_agents.py                 # Orquestador de agentes híbridos Gemma (Local / Cloud / Dual)
├── typst_generator.py               # Generador de reportes en PDF con Typst (APA 7)
├── graph_visualizer.py              # Renderizador de diagramas PNG del grafo (Pillow)
├── samples_generator.py             # Generador de documentos PDF de prueba de RRHH
├── okf_master_graph.json            # Grafo maestro de conocimiento en formato JSON
├── document_security_overrides.json # Anulaciones personalizadas de visibilidad
├── bin/
│   └── typst                        # Binario ejecutable de Typst v0.11.0
├── documents/                       # Carpeta de almacenamiento de PDFs ingeridos
└── static/
    ├── index.html                   # Interfaz de usuario (HTML5, Sidebar Layout)
    ├── styles.css                   # Sistema de estilos (CSS3 Vanilla, Light Corporate)
    ├── app.js                       # Lógica frontend y visualizador Vis.js
    └── reports/                     # Reportes y diagramas PDF / PNG generados
```

---

## 📄 Licencia y Créditos

Desarrollado para la **Hackathon Gemma 4**.  
Implementa las especificaciones de **Google Cloud Open Knowledge Graph Format (OKF v1.0)** y las herramientas de visualización **Graphify**.
