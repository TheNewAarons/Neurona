# memory.py
import json
import os
import uuid
from datetime import datetime
from collections import defaultdict
import math

class Memory:
    """
    Vector store local con JSON + TF-IDF manual para búsqueda semántica.
    Simula la memoria a largo plazo de la neurona.
    """

    def __init__(self, filename="memory.json"):
        self.filename = filename
        self.data = {"nodes": [], "connections": []}
        self.load()

    def load(self):
        """Carga la memoria desde JSON si existe."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error cargando memoria: {e}")
                self.data = {"nodes": [], "connections": []}
        else:
            self.data = {"nodes": [], "connections": []}

    def save(self):
        """Guarda la memoria en JSON."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando memoria: {e}")

    def add_node(self, topic, content, source, keywords=None):
        """
        Agrega un nuevo nodo de conocimiento.

        Args:
            topic: Tema o título (str)
            content: Contenido completo (str)
            source: Fuente (e.g., "stackoverflow.com")
            keywords: Lista de palabras clave (list)

        Returns:
            node_id (str)
        """
        if keywords is None:
            keywords = []

        node_id = str(uuid.uuid4())
        node = {
            "id": node_id,
            "topic": topic,
            "content": content,
            "source": source,
            "keywords": keywords,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "weight": 0.5,
        }
        self.data["nodes"].append(node)
        self.save()
        return node_id

    def search(self, query, top_k=5):
        """
        Busca nodos similares usando TF-IDF cosine similarity manual.

        Args:
            query: Texto de búsqueda
            top_k: Número de resultados

        Returns:
            list de dicts: [{"node": {...}, "score": 0.85}, ...]
        """
        if not self.data["nodes"]:
            return []

        # Tokenizar query
        query_tokens = self._tokenize(query.lower())
        query_tf = self._tf(query_tokens)

        results = []
        for node in self.data["nodes"]:
            # Combinar contenido + keywords para el cálculo
            node_text = (node["topic"] + " " + node["content"] + " " + " ".join(node["keywords"])).lower()
            node_tokens = self._tokenize(node_text)
            node_tf = self._tf(node_tokens)

            # Cosine similarity entre query_tf y node_tf
            similarity = self._cosine_similarity(query_tf, node_tf)

            # Boost de weight (nodos más accedidos/recientes)
            similarity *= (0.5 + 0.5 * node["weight"])

            results.append({"node": node, "score": similarity})

        # Ordenar por score y retornar top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def strengthen(self, node_id):
        """Incrementa el weight de un nodo al ser accedido."""
        for node in self.data["nodes"]:
            if node["id"] == node_id:
                node["access_count"] += 1
                node["weight"] = min(1.0, node["weight"] + 0.05)
                break
        self.save()

    def get_visual_layout(self, max_nodes=80):
        """
        Calcula posiciones x,y para visualizar nodos con spring-layout simple.

        Returns:
            dict: {node_id: {"x": 0.0, "y": 0.0, "size": 5, "brightness": 200}}
        """
        nodes_to_show = sorted(
            self.data["nodes"],
            key=lambda n: n["weight"],
            reverse=True
        )[:max_nodes]

        layout = {}
        num_nodes = len(nodes_to_show)

        if num_nodes == 0:
            return layout

        # Distribuir en círculo simple
        for i, node in enumerate(nodes_to_show):
            angle = (2 * math.pi * i) / max(1, num_nodes)
            radius = 100 + 30 * (node["weight"] * 2)

            x = 375 + radius * math.cos(angle)
            y = 350 + radius * math.sin(angle)

            # Tamaño proporcional al weight
            size = 3 + node["weight"] * 5

            # Brillo proporcional a recency (más reciente = más brillante)
            brightness = int(100 + 155 * node["weight"])

            layout[node["id"]] = {
                "x": x,
                "y": y,
                "size": size,
                "brightness": brightness,
                "topic": node["topic"]
            }

        return layout

    def get_stats(self):
        """Retorna estadísticas de la memoria."""
        topics = set(n["topic"] for n in self.data["nodes"])
        sources = set(n["source"] for n in self.data["nodes"])

        return {
            "total_nodes": len(self.data["nodes"]),
            "unique_topics": len(topics),
            "sources": list(sources),
            "avg_weight": sum(n["weight"] for n in self.data["nodes"]) / max(1, len(self.data["nodes"])),
            "total_accesses": sum(n["access_count"] for n in self.data["nodes"]),
        }

    # === Funciones auxiliares privadas ===

    def _tokenize(self, text):
        """Tokeniza texto simple (split + lowercase)."""
        return [word.strip(".,!?;:\"'") for word in text.split() if len(word) > 2]

    def _tf(self, tokens):
        """Calcula term frequency (diccionario)."""
        tf = defaultdict(int)
        for token in tokens:
            tf[token] += 1
        return dict(tf)

    def _cosine_similarity(self, tf1, tf2):
        """Calcula cosine similarity entre dos dicts TF."""
        all_keys = set(tf1.keys()) | set(tf2.keys())

        if not all_keys:
            return 0.0

        dot_product = sum(tf1.get(key, 0) * tf2.get(key, 0) for key in all_keys)
        mag1 = math.sqrt(sum(v ** 2 for v in tf1.values())) or 1
        mag2 = math.sqrt(sum(v ** 2 for v in tf2.values())) or 1

        return dot_product / (mag1 * mag2)
