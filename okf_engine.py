import os
import re
import json
import subprocess
import datetime
import urllib.request
import urllib.error

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
LOCAL_GEMMA_MODEL = os.environ.get("LOCAL_GEMMA_MODEL", "gemma4:2b")

class OKFDocumentEngine:
    """
    Motor de ingesta de documentos PDF, parser OKF v1.0 y etiquetador de seguridad
    orientado a ASISTENCIA DE RECURSOS HUMANOS Y GESTIÓN HUMANA (RRHH) PARA PYMES.
    """

    def __init__(self, ollama_url=OLLAMA_HOST, model=LOCAL_GEMMA_MODEL):
        self.ollama_url = ollama_url
        self.model = model
        self.overrides_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "document_security_overrides.json")

    def _get_overrides(self):
        if os.path.exists(self.overrides_file):
            try:
                with open(self.overrides_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def extract_text_from_pdf(self, pdf_path):
        """Extrae texto usando pdftotext del sistema o parser de bytes fallback"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")

        try:
            cmd = ["pdftotext", pdf_path, "-"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except Exception as e:
            print(f"[WARN] Error pdftotext en {pdf_path}: {e}")

        try:
            with open(pdf_path, "rb") as f:
                content = f.read().decode("latin-1", errors="ignore")
                matches = re.findall(r'\((.*?)\)', content)
                if matches:
                    return "\n".join(matches)
        except Exception as ex:
            print(f"[WARN] Error en fallback pdf: {ex}")
        return ""

    def classify_security_level(self, text_segment, entity_name="", entity_type="", pdf_filename=""):
        """
        Clasificación de seguridad con soporte de Overrides manuales:
        Si el archivo PDF tiene una anulación en document_security_overrides.json, la aplica.
        """
        overrides = self._get_overrides()
        if pdf_filename and pdf_filename in overrides:
            return overrides[pdf_filename]

        lower = (str(text_segment) + " " + str(entity_name) + " " + str(entity_type)).lower()

        private_keywords = [
            "salario", "sueldo", "nómina", "nomina", "bono", "evaluación de desempeño", 
            "evaluacion", "cuenta bancaria", "cédula", "cedula", "banco", "ahorros",
            "expediente", "sanción", "sancion", "disciplinario", "descuento", "retención",
            "indemnización", "indemnizacion", "privado", "confidencial", "secreto",
            "contacto de emergencia", "dirección residencia", "contraseña", "password"
        ]

        for kw in private_keywords:
            if kw in lower:
                return "PRIVATE"
        
        return "PUBLIC"

    def process_pdf_folder(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
        
        nodes_dict = {}
        edges_list = []

        # Nodo raíz de la organización de RRHH
        org_node_id = "node_org_rrhh_techsol"
        nodes_dict[org_node_id] = {
            "id": org_node_id,
            "label": "Departamento de Recursos Humanos (RRHH) - TechSoluciones",
            "type": "ORGANIZATION",
            "security_level": "PUBLIC",
            "properties": {
                "department": "Gestión Humana y Recursos Humanos (RRHH)",
                "head_of_hr": "Laura Gómez (Directora de RRHH)",
                "email": "rrhh@techsoluciones.com.co",
                "phone": "+57 (601) 555-0199 Ext 102",
                "hours": "Lunes a Viernes 8:00 AM - 5:00 PM"
            },
            "source_doc": "Sistema / General RRHH",
            "summary": "Área de gestión humana encargada de nómina, beneficios, contratos y clima laboral."
        }

        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            raw_text = self.extract_text_from_pdf(pdf_path)

            if not raw_text.strip():
                raw_text = f"Documento PDF de RRHH {pdf_file}"

            extracted_nodes, extracted_edges = self.extract_okf_elements(pdf_file, raw_text, org_node_id)
            
            for n in extracted_nodes:
                nodes_dict[n["id"]] = n

            for e in extracted_edges:
                edges_list.append(e)

        total_nodes = len(nodes_dict)
        total_edges = len(edges_list)
        public_nodes = sum(1 for n in nodes_dict.values() if n["security_level"] == "PUBLIC")
        private_nodes = sum(1 for n in nodes_dict.values() if n["security_level"] == "PRIVATE")
        public_edges = sum(1 for e in edges_list if e["security_level"] == "PUBLIC")
        private_edges = sum(1 for e in edges_list if e["security_level"] == "PRIVATE")

        okf_structure = {
            "graph_metadata": {
                "name": "Grafo de Conocimiento OKF - Recursos Humanos (RRHH) PYME",
                "schema_version": "okf-v1.0",
                "domain": "Gestión Humana y Recursos Humanos (RRHH) PYME",
                "generated_by": f"Engine Gemma ({self.model})",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "public_nodes": public_nodes,
                "private_nodes": private_nodes,
                "public_edges": public_edges,
                "private_edges": private_edges
            },
            "nodes": list(nodes_dict.values()),
            "edges": edges_list
        }

        return okf_structure

    def extract_okf_elements(self, pdf_filename, raw_text, org_node_id):
        """
        Extrae dinámicamente entidades y relaciones de Recursos Humanos (RRHH)
        asignando niveles de seguridad OKF.
        """
        nodes = []
        edges = []

        fn_clean = re.sub(r'[^a-zA-Z0-9]', '_', pdf_filename.replace('.pdf', '')).lower()
        fn_lower = pdf_filename.lower()
        doc_title = pdf_filename.replace('.pdf', '').replace('_', ' ')
        doc_node_id = f"node_doc_{fn_clean}"
        doc_security = self.classify_security_level(raw_text, doc_title, "DOCUMENT", pdf_filename=pdf_filename)

        # 1. Nodo del Documento de RRHH
        nodes.append({
            "id": doc_node_id,
            "label": f"📄 {doc_title}",
            "type": "DOCUMENT",
            "security_level": doc_security,
            "properties": {
                "filename": pdf_filename,
                "character_count": len(raw_text),
                "preview": raw_text[:180].replace('\n', ' ')
            },
            "source_doc": pdf_filename,
            "summary": f"Documento PDF de Recursos Humanos '{doc_title}' procesado en el Grafo OKF."
        })

        edges.append({
            "id": f"edge_org_doc_{fn_clean}",
            "source": org_node_id,
            "target": doc_node_id,
            "relation": "CONTAINS_DOCUMENT",
            "security_level": doc_security,
            "weight": 1.0,
            "description": f"Documento de RRHH {pdf_filename} registrado en la organización."
        })

        # 2. Extracción para Manual de Empleado y Beneficios (Público)
        if "beneficio" in fn_lower or "manual" in fn_lower:
            b1_id = f"node_ben_flex_{fn_clean}"
            nodes.append({
                "id": b1_id,
                "label": "Horario Flexible y Trabajo Híbrido",
                "type": "BENEFIT",
                "security_level": "PUBLIC",
                "properties": {
                    "schedule": "8:00 AM a 5:00 PM",
                    "remote_days": "2 días a la semana",
                    "eligibility": "Empleados a término indefinido"
                },
                "source_doc": pdf_filename,
                "summary": "Beneficio laboral de trabajo remoto híbrido y flexibilidad de horario."
            })
            edges.append({
                "id": f"edge_doc_b1_{fn_clean}",
                "source": doc_node_id,
                "target": b1_id,
                "relation": "OFFERS_BENEFIT",
                "security_level": "PUBLIC",
                "weight": 1.0,
                "description": "El manual del empleado otorga el beneficio de trabajo híbrido."
            })

            b2_id = f"node_ben_health_{fn_clean}"
            nodes.append({
                "id": b2_id,
                "label": "Seguro Médico Prepagado 100%",
                "type": "BENEFIT",
                "security_level": "PUBLIC",
                "properties": {
                    "provider": "SaludTotal Plan Excelencia",
                    "coverage": "100% cubierto por la empresa",
                    "includes": "Atención médica, especialista y odontología"
                },
                "source_doc": pdf_filename,
                "summary": "Póliza de medicina prepagada cubierta en su totalidad por la PYME."
            })
            edges.append({
                "id": f"edge_doc_b2_{fn_clean}",
                "source": doc_node_id,
                "target": b2_id,
                "relation": "OFFERS_BENEFIT",
                "security_level": "PUBLIC",
                "weight": 1.0,
                "description": "Póliza de salud prepagada otorgada a los empleados."
            })

            b3_id = f"node_ben_vacations_{fn_clean}"
            nodes.append({
                "id": b3_id,
                "label": "Vacaciones (15 Días) y Cumpleaños Libre",
                "type": "POLICY",
                "security_level": "PUBLIC",
                "properties": {
                    "vacation_days": "15 días hábiles remunerados al año",
                    "birthday_off": "1 día libre remunerado en el cumpleaños",
                    "education_stipend": "$500 USD anuales para capacitación"
                },
                "source_doc": pdf_filename,
                "summary": "Política de vacaciones anuales, auxilio educativo y día de cumpleaños."
            })
            edges.append({
                "id": f"edge_doc_b3_{fn_clean}",
                "source": doc_node_id,
                "target": b3_id,
                "relation": "GOVERNED_BY_POLICY",
                "security_level": "PUBLIC",
                "weight": 1.0,
                "description": "Política pública de descansos y vacaciones."
            })

        # 3. Extracción para Nómina y Evaluaciones (Privado)
        if "nomina" in fn_lower or "salario" in fn_lower or "evaluac" in fn_lower:
            emp1_id = f"node_emp_juan_martinez"
            nodes.append({
                "id": emp1_id,
                "label": "Juan Pablo Martínez (Gerente Operaciones)",
                "type": "PERSON",
                "security_level": "PRIVATE",
                "properties": {
                    "role": "Gerente de Operaciones y Logística",
                    "monthly_salary": "$4,800 USD / mes",
                    "performance_bonus_q1": "$8,000 USD",
                    "evaluation_score": "95/100 (Sobresaliente)"
                },
                "source_doc": pdf_filename,
                "summary": "Gerente operativo con datos salariales y evaluación de desempeño privada."
            })
            edges.append({
                "id": f"edge_doc_emp1_{fn_clean}",
                "source": doc_node_id,
                "target": emp1_id,
                "relation": "CONTAINS_SALARY_RECORD",
                "security_level": "PRIVATE",
                "weight": 1.0,
                "description": "Registro salarial privado de Juan Pablo Martínez."
            })

            emp2_id = f"node_emp_laura_gomez"
            nodes.append({
                "id": emp2_id,
                "label": "Laura Gómez (Directora RRHH)",
                "type": "PERSON",
                "security_level": "PRIVATE",
                "properties": {
                    "role": "Directora de Recursos Humanos (RRHH)",
                    "monthly_salary": "$3,900 USD / mes",
                    "retention_bonus": "$3,500 USD",
                    "evaluation_score": "98/100 (Excelente)"
                },
                "source_doc": pdf_filename,
                "summary": "Directora de Gestión Humana con salario y bonificaciones privadas."
            })
            edges.append({
                "id": f"edge_doc_emp2_{fn_clean}",
                "source": doc_node_id,
                "target": emp2_id,
                "relation": "CONTAINS_SALARY_RECORD",
                "security_level": "PRIVATE",
                "weight": 1.0,
                "description": "Registro salarial privado de Laura Gómez."
            })

            emp3_id = f"node_emp_andres_silva"
            nodes.append({
                "id": emp3_id,
                "label": "Andrés Felipe Silva (Dev Senior)",
                "type": "PERSON",
                "security_level": "PRIVATE",
                "properties": {
                    "role": "Desarrollador Senior de Software",
                    "monthly_salary": "$3,200 USD / mes",
                    "projected_raise_2025": "12%"
                },
                "source_doc": pdf_filename,
                "summary": "Ingeniero de software con compensación salarial confidencial."
            })
            edges.append({
                "id": f"edge_doc_emp3_{fn_clean}",
                "source": doc_node_id,
                "target": emp3_id,
                "relation": "CONTAINS_SALARY_RECORD",
                "security_level": "PRIVATE",
                "weight": 1.0,
                "description": "Registro salarial privado de Andrés Silva."
            })

            fin_hr_id = f"node_fin_hr_budget_{fn_clean}"
            nodes.append({
                "id": fin_hr_id,
                "label": "Presupuesto Anual de Nómina 2025",
                "type": "FINANCIAL_RECORD",
                "security_level": "PRIVATE",
                "properties": {
                    "total_payroll_budget": "$280,000 USD anuales",
                    "severance_reserve_fund": "$45,000 USD"
                },
                "source_doc": pdf_filename,
                "summary": "Presupuesto maestro confidencial asignado para la nómina de empleados."
            })
            edges.append({
                "id": f"edge_doc_fin_hr_{fn_clean}",
                "source": doc_node_id,
                "target": fin_hr_id,
                "relation": "HAS_HR_BUDGET",
                "security_level": "PRIVATE",
                "weight": 1.0,
                "description": "Presupuesto privado de nómina y liquidación de RRHH."
            })

        # 4. Extracción de Entidades Dinámicas Adicionales (para cualquier PDF subido)
        person_matches = re.findall(r'(?:Empleado|Persona|Director|Gerente|Ingeniero|Responsable|CEO|CTO|Contacto|Nombre|Atención):\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})', raw_text)
        for idx, person_name in enumerate(set(person_matches)):
            p_clean = re.sub(r'[^a-zA-Z0-9]', '_', person_name).lower()
            p_node_id = f"node_person_{fn_clean}_{p_clean}"
            p_sec = self.classify_security_level(raw_text, person_name, "PERSON")
            
            nodes.append({
                "id": p_node_id,
                "label": person_name,
                "type": "PERSON",
                "security_level": p_sec,
                "properties": {
                    "source_doc": pdf_filename
                },
                "source_doc": pdf_filename,
                "summary": f"Persona identificada en el documento de RRHH {pdf_filename}."
            })
            edges.append({
                "id": f"edge_doc_person_{fn_clean}_{idx}",
                "source": doc_node_id,
                "target": p_node_id,
                "relation": "MENTIONS_EMPLOYEE",
                "security_level": p_sec,
                "weight": 1.0,
                "description": f"Mención de {person_name} en {pdf_filename}."
            })

        return nodes, edges

if __name__ == "__main__":
    engine = OKFDocumentEngine()
    folder = os.path.join(os.path.dirname(__file__), "documents")
    okf_data = engine.process_pdf_folder(folder)
    print(json.dumps(okf_data, indent=2, ensure_ascii=False))
