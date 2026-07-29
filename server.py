import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from graph_manager import GraphManager
from hybrid_agents import HybridAgentSystem
from samples_generator import create_sample_documents
from typst_generator import TypstReportGenerator

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

gm = GraphManager()
agents = HybridAgentSystem(gm)
typst_engine = TypstReportGenerator()

class OKFServerHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # 1. API Status
        if path == "/api/status":
            master = gm.get_graph("private")
            meta = master.get("graph_metadata", {})
            data = {
                "status": "online",
                "system": "Agente Híbrido OKF Gemma PYME",
                "local_model": "gemma4:2b (Ollama / Local Engine)",
                "cloud_model": "gemma4:31b-cloud (Google Cloud AI)",
                "schema_version": meta.get("schema_version", "okf-v1.0"),
                "total_nodes": meta.get("total_nodes", 0),
                "total_edges": meta.get("total_edges", 0),
                "public_nodes": meta.get("public_nodes", 0),
                "private_nodes": meta.get("private_nodes", 0),
                "documents_processed": len([f for f in os.listdir(os.path.join(BASE_DIR, "documents")) if f.endswith(".pdf")])
            }
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        # 2. API Graph (view=public vs view=private)
        if path == "/api/graph":
            view = query_params.get("view", ["private"])[0]
            graph_data = gm.get_graph(view)
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(graph_data, ensure_ascii=False).encode("utf-8"))
            return

        # 2b. API Graphify Native JSON (graphify.net)
        if path == "/api/graphify":
            view = query_params.get("view", ["private"])[0]
            graphify_data = gm.get_graphify_json(view)
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(graphify_data, ensure_ascii=False).encode("utf-8"))
            return

        # 2c. API Graphify Report (GRAPH_REPORT.md)
        if path == "/api/report":
            report_md = gm.generate_graph_report_md()
            self._set_headers(200, "text/markdown; charset=utf-8")
            self.wfile.write(report_md.encode("utf-8"))
            return

        # 2d. API Google Cloud OKF Native Schema (okf_master_graph.json)
        if path == "/api/okf":
            view = query_params.get("view", ["private"])[0]
            okf_data = gm.get_graph(view)
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(okf_data, ensure_ascii=False).encode("utf-8"))
            return

        # 2e. API Typst PDF Export (/api/export-pdf)
        if path == "/api/export-pdf":
            view = query_params.get("view", ["private"])[0]
            okf_data = gm.get_graph(view)
            success, typ_path, pdf_path = typst_engine.generate_pdf_report(okf_data, view=view)

            if success and pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_f:
                    pdf_bytes = pdf_f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", "attachment; filename=Informe_Ejecutivo_RRHH_Typst.pdf")
                self.send_header("Content-Length", str(len(pdf_bytes)))
                self.end_headers()
                self.wfile.write(pdf_bytes)
            else:
                # Servir el código fuente Typst (.typ) si la compilación aún se está preparando
                with open(typ_path, "r", encoding="utf-8") as typ_f:
                    typ_content = typ_f.read()
                self._set_headers(200, "text/plain; charset=utf-8")
                self.wfile.write(f"// Código Fuente Typst (.typ) generado:\n{typ_content}".encode("utf-8"))
            return

        # 3. API Documents List
        if path == "/api/documents":
            doc_dir = os.path.join(BASE_DIR, "documents")
            overrides_file = os.path.join(BASE_DIR, "document_security_overrides.json")
            overrides = {}
            if os.path.exists(overrides_file):
                try:
                    with open(overrides_file, "r", encoding="utf-8") as f:
                        overrides = json.load(f)
                except Exception:
                    pass

            docs = []
            if os.path.exists(doc_dir):
                for f in os.listdir(doc_dir):
                    if f.endswith(".pdf"):
                        fp = os.path.join(doc_dir, f)
                        stat = os.stat(fp)
                        
                        if f in overrides:
                            sec_level = overrides[f]
                        else:
                            is_private = "finanza" in f.lower() or "salario" in f.lower() or "contrato" in f.lower() or "credencial" in f.lower() or "nomina" in f.lower()
                            sec_level = "PRIVATE" if is_private else "PUBLIC"

                        docs.append({
                            "name": f,
                            "size_bytes": stat.st_size,
                            "classification": "PRIVADO (Uso Interno)" if sec_level == "PRIVATE" else "PÚBLICO (Exponible)",
                            "security_level": sec_level
                        })
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({"documents": docs}, ensure_ascii=False).encode("utf-8"))
            return

        # 3b. API Document Download (/api/documents/download?file=filename.pdf)
        if path == "/api/documents/download":
            filename = query_params.get("file", [""])[0]
            if not filename or ".." in filename or "/" in filename:
                self._set_headers(400, "application/json")
                self.wfile.write(json.dumps({"error": "Nombre de archivo no válido"}).encode("utf-8"))
                return

            file_path = os.path.join(BASE_DIR, "documents", filename)
            if os.path.exists(file_path):
                with open(file_path, "rb") as pdf_f:
                    pdf_bytes = pdf_f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", f"attachment; filename={filename}")
                self.send_header("Content-Length", str(len(pdf_bytes)))
                self.end_headers()
                self.wfile.write(pdf_bytes)
            else:
                self._set_headers(404, "application/json")
                self.wfile.write(json.dumps({"error": "Archivo PDF no encontrado"}).encode("utf-8"))
            return

        # 4. Archivos Estáticos (Frontend UI)
        if path == "/" or path == "/index.html":
            file_path = os.path.join(STATIC_DIR, "index.html")
            self._serve_file(file_path, "text/html; charset=utf-8")
            return
        elif path.startswith("/static/"):
            rel_path = path.replace("/static/", "")
            file_path = os.path.join(STATIC_DIR, rel_path)
            content_type = "text/plain"
            if file_path.endswith(".html"):
                content_type = "text/html; charset=utf-8"
            elif file_path.endswith(".css"):
                content_type = "text/css; charset=utf-8"
            elif file_path.endswith(".js"):
                content_type = "application/javascript; charset=utf-8"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            elif file_path.endswith(".svg"):
                content_type = "image/svg+xml"
            self._serve_file(file_path, content_type)
            return

        self._set_headers(404, "application/json")
        self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode("utf-8"))

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        # 1. API Chat
        if path == "/api/chat":
            query = payload.get("query", "").strip()
            agent_mode = payload.get("agent", "cloud").lower()

            if not query:
                self._set_headers(400, "application/json")
                self.wfile.write(json.dumps({"error": "El campo query es requerido"}).encode("utf-8"))
                return

            if agent_mode == "dual" or agent_mode == "hybrid" or agent_mode == "compare":
                response_data = agents.query_dual_agents(query)
            elif agent_mode == "local" or agent_mode == "private" or agent_mode == "gemma4:2b":
                response_data = agents.query_local_agent(query)
            else:
                response_data = agents.query_cloud_agent(query)

            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        # 2. API Upload (subir archivos PDF en base64 con visibilidad pública/privada)
        if path == "/api/upload":
            files = payload.get("files", [])
            if not files and payload.get("filename"):
                files = [payload]

            default_sec = payload.get("security_level", "PRIVATE").upper()

            saved_count = 0
            doc_dir = os.path.join(BASE_DIR, "documents")
            os.makedirs(doc_dir, exist_ok=True)

            overrides_file = os.path.join(BASE_DIR, "document_security_overrides.json")
            overrides = {}
            if os.path.exists(overrides_file):
                try:
                    with open(overrides_file, "r", encoding="utf-8") as f_ov:
                        overrides = json.load(f_ov)
                except Exception:
                    pass

            import base64
            for f in files:
                fname = f.get("filename", "").strip()
                b64 = f.get("base64", "") or f.get("content", "")
                sec_level = f.get("security_level", default_sec).upper()

                if fname and b64:
                    if not fname.lower().endswith(".pdf"):
                        fname += ".pdf"
                    dest_path = os.path.join(doc_dir, fname)
                    try:
                        file_bytes = base64.b64decode(b64.split(",")[-1])
                        with open(dest_path, "wb") as pdf_out:
                            pdf_out.write(file_bytes)
                        overrides[fname] = sec_level
                        saved_count += 1
                    except Exception as ex:
                        print(f"[WARN] Error al guardar {fname}: {ex}")

            with open(overrides_file, "w", encoding="utf-8") as f_ov_out:
                json.dump(overrides, f_ov_out, indent=2, ensure_ascii=False)

            new_graph = gm.rebuild_from_documents()
            sec_badge = "🔒 Privado" if default_sec == "PRIVATE" else "🌐 Público"
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({
                "message": f"Se subieron y procesaron {saved_count} archivo(s) PDF exitosamente con visibilidad {sec_badge} en formato OKF.",
                "saved_count": saved_count,
                "security_level": default_sec,
                "total_nodes": new_graph.get("graph_metadata", {}).get("total_nodes", 0)
            }, ensure_ascii=False).encode("utf-8"))
            return

        # 2. API Ingest (re-procesar PDFs)
        if path == "/api/ingest":
            new_graph = gm.rebuild_from_documents()
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({
                "message": "Carpeta de documentos procesada exitosamente en formato OKF.",
                "total_nodes": new_graph.get("graph_metadata", {}).get("total_nodes", 0),
                "total_edges": new_graph.get("graph_metadata", {}).get("total_edges", 0)
            }, ensure_ascii=False).encode("utf-8"))
            return

        # 3. API Toggle Document Security (/api/documents/toggle-security)
        if path == "/api/documents/toggle-security":
            filename = payload.get("filename", "").strip()
            target_level = payload.get("security_level", "PUBLIC").upper()

            if not filename:
                self._set_headers(400, "application/json")
                self.wfile.write(json.dumps({"error": "Nombre de archivo no especificado"}).encode("utf-8"))
                return

            new_graph = gm.set_document_security(filename, target_level)
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({
                "message": f"Estado de seguridad de '{filename}' actualizado a {target_level}.",
                "filename": filename,
                "security_level": target_level,
                "total_nodes": new_graph.get("graph_metadata", {}).get("total_nodes", 0)
            }, ensure_ascii=False).encode("utf-8"))
            return

        # 3. API Generate Samples
        if path == "/api/generate-samples":
            created_files = create_sample_documents()
            new_graph = gm.rebuild_from_documents()
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({
                "message": f"Se generaron {len(created_files)} documentos de prueba PYME y se actualizó el grafo OKF.",
                "created_files": [os.path.basename(f) for f in created_files]
            }, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "application/json")
        self.wfile.write(json.dumps({"error": "Endpoint POST no encontrado"}).encode("utf-8"))

    def _serve_file(self, file_path, content_type):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, content_type)
            self.wfile.write(content)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"404 Not Found")

def run_server():
    os.makedirs(STATIC_DIR, exist_ok=True)
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, OKFServerHandler)
    print(f"🚀 Servidor Agente Híbrido OKF Gemma escuchando en http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido por el usuario.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
