import os
import json
import math
from PIL import Image, ImageDraw, ImageFont

class GraphVisualizer:
    """
    Renderiza un diagrama visual de alta resolución del Grafo de Conocimiento (Nodes & Edges)
    y lo guarda en un archivo PNG para ser insertado en el informe APA 7 de Typst.
    """

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "static", "reports")
        os.makedirs(self.output_dir, exist_ok=True)

    def render_graph_png(self, okf_graph_data, output_filename="okf_graph_diagram.png"):
        nodes = okf_graph_data.get("nodes", [])
        edges = okf_graph_data.get("edges", [])

        width, height = 1400, 900
        img = Image.new("RGB", (width, height), "#0F172A")
        draw = ImageDraw.Draw(img)

        # Fondos y rejilla sutil
        for x in range(0, width, 50):
            draw.line([(x, 0), (x, height)], fill="#1E293B", width=1)
        for y in range(0, height, 50):
            draw.line([(0, y), (width, y)], fill="#1E293B", width=1)

        # Calcular posiciones circulares/comunitarias para los nodos
        node_pos = {}
        total_n = max(1, len(nodes))
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2.5

        # Colocar nodo organización en el centro
        org_id = None
        for n in nodes:
            if n.get("type") == "ORGANIZATION":
                org_id = n.get("id")
                node_pos[org_id] = (center_x, center_y)
                break

        other_nodes = [n for n in nodes if n.get("id") != org_id]
        num_others = len(other_nodes)

        for i, n in enumerate(other_nodes):
            angle = (2 * math.pi * i) / max(1, num_others)
            # Variar radio alternado para dar profundidad
            r_var = radius * (0.85 if i % 2 == 0 else 0.65)
            nx = int(center_x + r_var * math.cos(angle))
            ny = int(center_y + r_var * math.sin(angle))
            node_pos[n["id"]] = (nx, ny)

        # 1. Dibujar Edges (Aristas)
        for e in edges:
            src = e.get("source")
            tgt = e.get("target")
            if src in node_pos and tgt in node_pos:
                p1 = node_pos[src]
                p2 = node_pos[tgt]
                sec = e.get("security_level", "PUBLIC")
                edge_color = "#F43F5E" if sec == "PRIVATE" else "#10B981"
                draw.line([p1, p2], fill=edge_color, width=2)

        # 2. Dibujar Nodos
        for n in nodes:
            nid = n.get("id")
            if nid not in node_pos:
                continue
            x, y = node_pos[nid]
            sec = n.get("security_level", "PUBLIC")
            ntype = n.get("type", "RECORD")

            if ntype == "ORGANIZATION":
                color = "#2563EB"
                size = 36
            elif sec == "PRIVATE":
                color = "#F43F5E"
                size = 26
            else:
                color = "#10B981"
                size = 24

            # Círculo exterior con resplandor
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color, outline="#FFFFFF", width=2)

            # Etiqueta corta del nodo
            label = n.get("label", nid)
            clean_label = label[:22] + "..." if len(label) > 22 else label
            
            # Fondo para etiqueta de texto
            text_x = x - (len(clean_label) * 3)
            text_y = y + size + 6
            draw.rectangle([text_x - 4, text_y - 2, text_x + (len(clean_label) * 7), text_y + 14], fill="#0F172A", outline="#334155")
            draw.text((text_x, text_y), clean_label, fill="#F8FAFC")

        # 3. Leyenda APA 7 en la esquina superior izquierda
        draw.rectangle([20, 20, 360, 110], fill="#1E293B", outline="#475569", width=1)
        draw.text((32, 30), "Leyenda del Grafo Google OKF:", fill="#F8FAFC")
        
        # Bolita roja (Privado)
        draw.ellipse([32, 55, 44, 67], fill="#F43F5E")
        draw.text((52, 53), "🔒 Nodo Privado (Confidencial / Nómina)", fill="#CBD5E1")
        
        # Bolita verde (Público)
        draw.ellipse([32, 78, 44, 90], fill="#10B981")
        draw.text((52, 76), "🌐 Nodo Público (Beneficios / Políticas)", fill="#CBD5E1")

        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path, "PNG")
        print(f"[OK] Diagrama PNG del Grafo renderizado exitosamente: {output_path}")
        return output_path

if __name__ == "__main__":
    from graph_manager import GraphManager
    gm = GraphManager()
    gv = GraphVisualizer()
    gv.render_graph_png(gm.get_graph("private"))
