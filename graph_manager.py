import os
import re
import json
import datetime
from okf_engine import OKFDocumentEngine

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_GRAPH_FILE = os.path.join(DATA_DIR, "okf_master_graph.json")
PUBLIC_GRAPH_FILE = os.path.join(DATA_DIR, "okf_public_graph.json")
PRIVATE_GRAPH_FILE = os.path.join(DATA_DIR, "okf_private_graph.json")
GRAPHIFY_GRAPH_FILE = os.path.join(DATA_DIR, "graph.json")
GRAPHIFY_REPORT_FILE = os.path.join(DATA_DIR, "GRAPH_REPORT.md")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")

class GraphManager:
    """
    Gestor centralizado del Grafo de Conocimiento OKF de Google Cloud e Integración Graphify (graphify.net).
    Mantiene la separación estricta entre el Subgrafo Público y el Subgrafo Privado.
    """

    def __init__(self):
        self.engine = OKFDocumentEngine()
        self.master_graph = None
        self.public_graph = None
        self.private_graph = None
        self.load_or_rebuild_graphs()

    def load_or_rebuild_graphs(self):
        """Carga los grafos desde disco o los procesa si no existen"""
        if os.path.exists(MASTER_GRAPH_FILE):
            try:
                with open(MASTER_GRAPH_FILE, "r", encoding="utf-8") as f:
                    self.master_graph = json.load(f)
                self._generate_subgraphs()
                print("[OK] Grafo OKF/Graphify cargado exitosamente desde disco.")
                return
            except Exception as e:
                print(f"[WARN] Error al cargar grafo desde disco: {e}")

        self.rebuild_from_documents()

    def rebuild_from_documents(self):
        """Procesa nuevamente la carpeta de documentos PDF y regenera los archivos OKF y Graphify"""
        print("[INFO] Procesando carpeta de documentos PDF...")
        self.master_graph = self.engine.process_pdf_folder(DOCUMENTS_DIR)
        self._save_graph_file(MASTER_GRAPH_FILE, self.master_graph)
        self._generate_subgraphs()
        self._export_graphify_files()
        return self.master_graph

    def set_document_security(self, filename, security_level):
        """Cambia el estado de seguridad (PUBLIC / PRIVATE) de un documento y reconstruye el grafo OKF"""
        overrides_file = os.path.join(DATA_DIR, "document_security_overrides.json")
        overrides = {}
        if os.path.exists(overrides_file):
            try:
                with open(overrides_file, "r", encoding="utf-8") as f:
                    overrides = json.load(f)
            except Exception:
                pass
        
        overrides[filename] = security_level.upper()
        with open(overrides_file, "w", encoding="utf-8") as f:
            json.dump(overrides, f, indent=2, ensure_ascii=False)

        return self.rebuild_from_documents()

    def _generate_subgraphs(self):
        """Genera y guarda el Subgrafo Público (filtrado) y el Subgrafo Privado (completo)"""
        # 1. Subgrafo Privado (Acceso completo interno)
        self.private_graph = dict(self.master_graph)

        # 2. Subgrafo Público (Filtrado estricto - excluye nodos/aristas PRIVATE)
        public_nodes = [n for n in self.master_graph.get("nodes", []) if n.get("security_level") == "PUBLIC"]
        public_node_ids = {n["id"] for n in public_nodes}

        public_edges = [
            e for e in self.master_graph.get("edges", [])
            if e.get("security_level") == "PUBLIC" and e["source"] in public_node_ids and e["target"] in public_node_ids
        ]

        metadata = dict(self.master_graph.get("graph_metadata", {}))
        metadata["view_type"] = "PUBLIC_CLIENT_ONLY"
        metadata["total_nodes"] = len(public_nodes)
        metadata["total_edges"] = len(public_edges)
        metadata["note"] = "Nodos y aristas confidenciales ocultados por estricta seguridad OKF/Graphify."

        self.public_graph = {
            "graph_metadata": metadata,
            "nodes": public_nodes,
            "edges": public_edges
        }

        self._save_graph_file(PRIVATE_GRAPH_FILE, self.private_graph)
        self._save_graph_file(PUBLIC_GRAPH_FILE, self.public_graph)

    def _export_graphify_files(self):
        """Exporta los archivos en formato nativo Graphify (graph.json y GRAPH_REPORT.md)"""
        graphify_data = self.get_graphify_json(view="private")
        self._save_graph_file(GRAPHIFY_GRAPH_FILE, graphify_data)
        
        report_md = self.generate_graph_report_md()
        with open(GRAPHIFY_REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report_md)
        print("[OK] Exportados archivos estándar de Graphify: graph.json y GRAPH_REPORT.md")

    def get_graphify_json(self, view="private"):
        """
        Transforma el grafo OKF al formato JSON nativo de Graphify (graphify.net).
        Incluye clusters de comunidades, grado de nodos y enlaces.
        """
        raw_graph = self.get_graph(view)
        okf_nodes = raw_graph.get("nodes", [])
        okf_edges = raw_graph.get("edges", [])

        # Calcular grado de cada nodo (número de conexiones)
        degree_map = {}
        for e in okf_edges:
            degree_map[e["source"]] = degree_map.get(e["source"], 0) + 1
            degree_map[e["target"]] = degree_map.get(e["target"], 0) + 1

        # Mapeo de clusters de comunidades Graphify
        cluster_map = {
            "ORGANIZATION": 0,       # Cluster 0: Empresa / Raíz
            "SERVICE": 1,            # Cluster 1: Servicios Comercial Públicos
            "PERSON": 2,             # Cluster 2: Nómina y Personal
            "FINANCIAL_RECORD": 3,   # Cluster 3: Registros Financieros Privados
            "CREDENTIAL": 4,         # Cluster 4: Credenciales de Infraestructura
            "DOCUMENT": 5,           # Cluster 5: Documentos Ingeridos
            "POLICY": 6,             # Cluster 6: Políticas y Garantías
            "STRATEGY": 7            # Cluster 7: Estrategias Internas
        }

        graphify_nodes = []
        for n in okf_nodes:
            ntype = n.get("type", "RECORD")
            is_priv = n.get("security_level") == "PRIVATE"
            
            graphify_nodes.append({
                "id": n["id"],
                "label": n["label"],
                "type": ntype,
                "security_level": n.get("security_level", "PUBLIC"),
                "community": cluster_map.get(ntype, 8),
                "degree": degree_map.get(n["id"], 1),
                "source_doc": n.get("source_doc", "Desconocido"),
                "properties": n.get("properties", {}),
                "summary": n.get("summary", ""),
                "badge": "🔒 PRIVADO" if is_priv else "🌐 PÚBLICO"
            })

        graphify_links = []
        for e in okf_edges:
            graphify_links.append({
                "id": e.get("id", f"{e['source']}_{e['target']}"),
                "source": e["source"],
                "target": e["target"],
                "relation": e.get("relation", "CONNECTED_TO"),
                "security_level": e.get("security_level", "PUBLIC"),
                "weight": e.get("weight", 1.0),
                "description": e.get("description", "")
            })

        return {
            "graphify_meta": {
                "generator": "Graphify Engine (graphify.net v1.2)",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "view": view.upper(),
                "total_nodes": len(graphify_nodes),
                "total_links": len(graphify_links),
                "communities_count": len(set(n["community"] for n in graphify_nodes))
            },
            "nodes": graphify_nodes,
            "links": graphify_links
        }

    def generate_graph_report_md(self):
        """Genera el reporte ejecutivo GRAPH_REPORT.md siguiendo el estándar de Graphify"""
        master = self.master_graph or {}
        meta = master.get("graph_metadata", {})
        nodes = master.get("nodes", [])
        edges = master.get("edges", [])

        pub_nodes = [n for n in nodes if n.get("security_level") == "PUBLIC"]
        priv_nodes = [n for n in nodes if n.get("security_level") == "PRIVATE"]

        lines = [
            "# 🕸️ Graphify Knowledge Graph Report (GRAPH_REPORT.md)",
            f"**Generado por:** Graphify Engine (graphify.net) | **Fecha:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 Métricas Generales del Grafo de Conocimiento",
            f"- **Total de Nodos Identificados:** `{len(nodes)}`",
            f"- **Total de Enlaces (Relaciones):** `{len(edges)}`",
            f"- **Nodos Públicos Exponibles (🌐):** `{len(pub_nodes)}`",
            f"- **Nodos Privados Confidenciales (🔒):** `{len(priv_nodes)}`",
            "",
            "## 🏢 Comunidades de Conocimiento (Graphify Clusters)",
            "1. **Cluster 0 (Organización Raíz):** TechSoluciones S.A.S.",
            "2. **Cluster 1 (Servicios y Tarifas Públicas):** Desarrollo Web, GCP Cloud y Agentes IA.",
            "3. **Cluster 2 (Personal y Nóminas):** Empleados, Salarios y Bono Anual (Estrictamente Privado).",
            "4. **Cluster 3 (Registros Financieros):** Ganancias Q1, Costos Operativos y Márgenes Netos.",
            "5. **Cluster 4 (Infraestructura y Credenciales):** IPs de Servidores, Passwords y API Keys.",
            "6. **Cluster 5 (Documentos Ingeridos):** Archivos PDF de origen procesados.",
            "",
            "## 🔒 Clasificación de Seguridad y Separación Híbrida",
            "El sistema aplica aislamiento estricto entre el subgrafo público y privado:",
            "- El **Agente Cloud (`gemma4:31b-cloud`)** opera únicamente sobre el Subgrafo Público y no recibe contexto de salarios ni credenciales.",
            "- El **Agente Local (`gemma4:2b`)** resuelve consultas estratégicas internas sobre el Subgrafo Privado.",
            "",
            "## 📑 Nodos Destacados en el Grafo Graphify",
        ]

        for n in nodes[:15]:
            sec = "🔒 PRIVADO" if n.get("security_level") == "PRIVATE" else "🌐 PÚBLICO"
            lines.append(f"- **{n['label']}** (`{n.get('type')}`) - [{sec}] | Fuente: `{n.get('source_doc')}`")

        return "\n".join(lines)

    def _save_graph_file(self, filepath, data):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_graph(self, view="private"):
        """Retorna el grafo según la vista requerida (public vs private)"""
        if view.lower() == "public":
            return self.public_graph
        return self.private_graph

    def get_context_for_query(self, query, view="private"):
        """
        Extrae los nodos y relaciones relevantes del subgrafo para enriquecer el prompt del LLM.
        """
        graph = self.get_graph(view)
        query_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2]

        relevant_nodes = []
        for n in graph.get("nodes", []):
            searchable_str = (n.get("label", "") + " " + n.get("summary", "") + " " + json.dumps(n.get("properties", {}))).lower()
            if any(qw in searchable_str for qw in query_words) or len(query_words) == 0:
                relevant_nodes.append(n)

        if not relevant_nodes:
            relevant_nodes = graph.get("nodes", [])[:8]

        relevant_node_ids = {n["id"] for n in relevant_nodes}
        relevant_edges = [
            e for e in graph.get("edges", [])
            if e["source"] in relevant_node_ids or e["target"] in relevant_node_ids
        ]

        return {
            "view": view.upper(),
            "nodes": relevant_nodes,
            "edges": relevant_edges
        }

if __name__ == "__main__":
    gm = GraphManager()
    g_json = gm.get_graphify_json("private")
    print(f"Graphify JSON generado: {g_json['graphify_meta']['total_nodes']} nodos, {g_json['graphify_meta']['communities_count']} comunidades.")
