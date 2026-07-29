import os
import json
import urllib.request
import urllib.error
from graph_manager import GraphManager

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
LOCAL_MODEL = os.environ.get("LOCAL_GEMMA_MODEL", "gemma4:2b")
CLOUD_MODEL = os.environ.get("CLOUD_GEMMA_MODEL", "gemma4:31b-cloud")

class HybridAgentSystem:
    """
    Sistema Híbrido de Agentes Gemma orientados a ASISTENCIA DE RECURSOS HUMANOS (RRHH) Y GESTIÓN HUMANA.
    - Agente Local (gemma4:2b): Analiza y responde sobre el Subgrafo Privado de RRHH (Nómina, Salarios, Evaluaciones, Datos Bancarios).
    - Agente Cloud (gemma4:31b-cloud): Analiza y responde sobre el Subgrafo Público de RRHH (Beneficios, Vacaciones, Políticas, Horarios).
    """

    def __init__(self, graph_manager=None):
        self.gm = graph_manager or GraphManager()
        self.ollama_url = OLLAMA_HOST

    def _call_llm_api(self, model_name, prompt, system_prompt):
        try:
            req_data = {
                "model": model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {"temperature": 0.2}
            }
            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res.get("response", "")
        except Exception:
            return None

    def query_local_agent(self, user_query):
        """
        Agente Local (gemma4:2b) - Acceso a Subgrafo Privado de Recursos Humanos (RRHH).
        """
        context = self.gm.get_context_for_query(user_query, view="private")
        
        system_prompt = (
            "Eres el Asistente Privado de Recursos Humanos y Gestión Humana (RRHH) de la empresa TechSoluciones S.A.S. (gemma4:2b).\n"
            "Tu función es responder consultas de gestión humana, nómina, salarios, evaluaciones de desempeño, beneficios y contratos laborales.\n"
            "Tienes acceso completo al Grafo de Conocimiento OKF Privado de RRHH.\n"
            "Responde de forma precisa citando siempre el documento PDF de origen."
        )

        prompt = (
            f"Consulta de Gestión Humana (RRHH): {user_query}\n\n"
            f"Contexto del Grafo de Conocimiento OKF Privado de RRHH (gemma4:2b):\n"
            f"{json.dumps(context, indent=2, ensure_ascii=False)}\n\n"
            f"Por favor responde con detalle sobre Recursos Humanos citando el archivo fuente."
        )

        llm_response = self._call_llm_api(LOCAL_MODEL, prompt, system_prompt)

        if not llm_response:
            llm_response = self._fallback_hr_reasoning(user_query, context, agent_type="LOCAL_CONFIDENTIAL_HR")

        return {
            "agent": f"Agente Privado de RRHH ({LOCAL_MODEL})",
            "model": LOCAL_MODEL,
            "security_view": "PRIVADA (Nómina, Salarios y Expedientes)",
            "query": user_query,
            "answer": llm_response,
            "context_nodes": len(context.get("nodes", [])),
            "citations": list({n.get("source_doc") for n in context.get("nodes", []) if n.get("source_doc")})
        }

    def query_cloud_agent(self, user_query):
        """
        Agente Cloud (gemma4:31b-cloud) - Acceso Exclusivo a Subgrafo Público de Recursos Humanos.
        """
        q_lower = user_query.lower()

        # 1. Guardrail de Privacidad para Recursos Humanos
        private_triggers = ["salario", "sueldo", "nómina", "nomina", "bono", "evaluación", "evaluacion", "cuenta bancaria", "cédula", "cedula", "banco", "expediente", "sanción", "disciplinario"]
        if any(trig in q_lower for trig in private_triggers):
            return {
                "agent": f"Agente Público de RRHH ({CLOUD_MODEL})",
                "model": CLOUD_MODEL,
                "security_view": "PÚBLICA (Filtrada / Oculta)",
                "query": user_query,
                "answer": "🔒 **Acceso Denegado por Seguridad de RRHH**: La información salarial, nóminas, evaluaciones o datos personales bancarios son estrictamente confidenciales. El Agente Público de Recursos Humanos no tiene acceso a estos registros privados.",
                "context_nodes": 0,
                "citations": []
            }

        # 2. Respuestas fuera de dominio (ej: literatura, deportes, software de clientes)
        unrelated_triggers = ["romeo", "julieta", "fútbol", "futbol", "película", "pelicula", "cocina", "receta"]
        if any(trig in q_lower for trig in unrelated_triggers):
            return {
                "agent": f"Agente Público de RRHH ({CLOUD_MODEL})",
                "model": CLOUD_MODEL,
                "security_view": "PÚBLICA (Recursos Humanos)",
                "query": user_query,
                "answer": "ℹ️ **Asistente de Recursos Humanos (RRHH)**: Como especialista en Gestión Humana de nuestra PYME, mi función es asistirte con políticas de empleados, beneficios, vacaciones, licencias y reglamentos laborales internos. No dispongo de información sobre temas ajenos a la gestión de recursos humanos.",
                "context_nodes": 0,
                "citations": []
            }

        context = self.gm.get_context_for_query(user_query, view="public")

        system_prompt = (
            "Eres el Asistente Público de Recursos Humanos y Gestión Humana (RRHH) de TechSoluciones S.A.S. (gemma4:31b-cloud).\n"
            "Respondes consultas sobre el programa de beneficios, horarios de trabajo, vacaciones, código de conducta y procesos de solicitud de permisos.\n"
            "Utilizas exclusivamente el Subgrafo OKF Público de RRHH."
        )

        prompt = (
            f"Consulta de Empleado/Usuario: {user_query}\n\n"
            f"Contexto del Subgrafo OKF Público de RRHH (gemma4:31b-cloud):\n"
            f"{json.dumps(context, indent=2, ensure_ascii=False)}\n\n"
            f"Responde con amabilidad detallando los beneficios y políticas de Recursos Humanos."
        )

        llm_response = self._call_llm_api(CLOUD_MODEL, prompt, system_prompt)

        if not llm_response:
            llm_response = self._fallback_hr_reasoning(user_query, context, agent_type="CLOUD_PUBLIC_HR")

        return {
            "agent": f"Agente Público de RRHH ({CLOUD_MODEL})",
            "model": CLOUD_MODEL,
            "security_view": "PÚBLICA (Beneficios y Políticas de Empleados)",
            "query": user_query,
            "answer": llm_response,
            "context_nodes": len(context.get("nodes", [])),
            "citations": list({n.get("source_doc") for n in context.get("nodes", []) if n.get("source_doc")})
        }

    def query_dual_agents(self, user_query):
        """
        Modo Híbrido Comparativo Dual: Ejecuta la consulta simultáneamente en el
        Agente Privado Local (gemma4:2b) y el Agente Público Cloud (gemma4:31b-cloud).
        """
        local_res = self.query_local_agent(user_query)
        cloud_res = self.query_cloud_agent(user_query)

        all_citations = list(set(local_res.get("citations", []) + cloud_res.get("citations", [])))

        dual_answer = (
            f"### 💻 Respuesta del Agente Local Privado (gemma4:2b - Nómina & Confidencial):\n"
            f"{local_res.get('answer', '')}\n\n"
            f"---\n\n"
            f"### ☁️ Respuesta del Agente Cloud Público (gemma4:31b-cloud - Beneficios & Políticas):\n"
            f"{cloud_res.get('answer', '')}"
        )

        return {
            "agent": f"Modo Comparativo Dual ({LOCAL_MODEL} & {CLOUD_MODEL})",
            "model": "dual",
            "security_view": "HÍBRIDA DUAL (Privado + Público)",
            "query": user_query,
            "answer": dual_answer,
            "local_response": local_res,
            "cloud_response": cloud_res,
            "context_nodes": local_res.get("context_nodes", 0) + cloud_res.get("context_nodes", 0),
            "citations": all_citations
        }

    def _fallback_hr_reasoning(self, query, context, agent_type):
        """Genera respuestas estructuradas orientadas 100% a Recursos Humanos (RRHH)"""
        nodes = context.get("nodes", [])
        q_lower = query.lower()

        if agent_type == "LOCAL_CONFIDENTIAL_HR":
            if "salario" in q_lower or "sueldo" in q_lower or "nomina" in q_lower or "remuneracion" in q_lower:
                people = [n for n in nodes if n.get("type") == "PERSON"]
                lines = ["### 📊 Registro de Nómina y Salarios de Empleados (Gemma Local RRHH):"]
                for p in people:
                    props = p.get("properties", {})
                    sal = props.get("monthly_salary") or props.get("salary") or "No especificado"
                    role = props.get("role", "Empleado")
                    lines.append(f"- **{p['label']}** ({role}): **{sal}** (Fuente: `{p['source_doc']}`)")
                return "\n".join(lines)

            if "evaluac" in q_lower or "desempeño" in q_lower or "bono" in q_lower:
                people = [n for n in nodes if n.get("type") == "PERSON"]
                lines = ["### 🏆 Evaluaciones de Desempeño y Bonos 2025 (Gemma Local RRHH):"]
                for p in people:
                    props = p.get("properties", {})
                    score = props.get("evaluation_score") or props.get("calificacion")
                    bonus = props.get("performance_bonus_q1") or props.get("retention_bonus") or "N/A"
                    if score or bonus != "N/A":
                        lines.append(f"- **{p['label']}**: Evaluación `{score}` | Bono: **{bonus}** (Fuente: `{p['source_doc']}`)")
                return "\n".join(lines)

            if "banco" in q_lower or "cuenta" in q_lower or "cedula" in q_lower or "cédula" in q_lower:
                people = [n for n in nodes if n.get("type") == "PERSON"]
                lines = ["### 🆔 Datos Personales y Cuentas Bancarias de Nómina (Gemma Local RRHH):"]
                for p in people:
                    props = p.get("properties", {})
                    lines.append(f"- **{p['label']}**:")
                    for k, v in props.items():
                        lines.append(f"  * {k.replace('_', ' ').title()}: `{v}`")
                    lines.append(f"  * Fuente: `{p['source_doc']}`\n")
                return "\n".join(lines)

        # Respuestas para Agente Público de RRHH
        if "beneficio" in q_lower or "horario" in q_lower or "salud" in q_lower or "remoto" in q_lower:
            bens = [n for n in nodes if n.get("type") in ["BENEFIT", "POLICY"]]
            lines = ["### 🎁 Programa de Beneficios y Calidad de Vida Laboral (Gemma Cloud RRHH):"]
            for b in bens:
                props = b.get("properties", {})
                lines.append(f"**{b['label']}**:")
                for k, v in props.items():
                    lines.append(f"  * {k.replace('_', ' ').title()}: **{v}**")
                lines.append(f"  * Fuente: `{b['source_doc']}`\n")
            return "\n".join(lines)

        if "vacacion" in q_lower or "cumpleaños" in q_lower or "permiso" in q_lower:
            pols = [n for n in nodes if "vacation" in n.get("id", "") or "POLICY" in n.get("type", "")]
            lines = ["### 🌴 Políticas de Vacaciones, Permisos y Cumpleaños (Gemma Cloud RRHH):"]
            for p in pols:
                props = p.get("properties", {})
                lines.append(f"**{p['label']}**:")
                for k, v in props.items():
                    lines.append(f"  * {k.replace('_', ' ').title()}: **{v}**")
                lines.append(f"  * Fuente: `{p['source_doc']}`\n")
            return "\n".join(lines)

        lines = [f"### Resumen de Respuesta de Gestión Humana (RRHH):"]
        for n in nodes[:5]:
            sec_badge = "🔒 PRIVADO" if n.get("security_level") == "PRIVATE" else "🌐 PÚBLICO"
            lines.append(f"- [{sec_badge}] **{n['label']}** ({n.get('type')}): {n.get('summary')}")
        return "\n".join(lines)

if __name__ == "__main__":
    has = HybridAgentSystem()
    print("--- PRUEBA AGENTE RRHH LOCAL (PRIVADO) ---")
    print(json.dumps(has.query_local_agent("¿Cuáles son los salarios y bonos de los empleados?"), indent=2, ensure_ascii=False))

    print("\n--- PRUEBA AGENTE RRHH CLOUD (PÚBLICO) - BENEFICIOS ---")
    print(json.dumps(has.query_cloud_agent("¿Cuáles son los beneficios de salud y horario flexible?"), indent=2, ensure_ascii=False))

    print("\n--- PRUEBA AGENTE RRHH CLOUD (PÚBLICO) - FORA DE DOMINIO ---")
    print(json.dumps(has.query_cloud_agent("Háblame de Romeo y Julieta"), indent=2, ensure_ascii=False))
