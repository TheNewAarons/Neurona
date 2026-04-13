# brain.py
import threading
import queue
from anthropic import Anthropic
from memory import Memory
from crawler import WebCrawler
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT, MIN_LOCAL_SCORE

class NeuronBrain:
    """
    Motor cognitivo: orquesta búsqueda local → web → Claude API.
    """

    def __init__(self, memory=None):
        self.state = "idle"  # idle | searching | processing | responding | learning
        self.current_thought = ""
        self.sources_found = []
        self.response_buffer = ""
        self.memory = memory or Memory()

        # Claude API client
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY no configurada en env vars")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Thread-safe queue para comunicar con pygame
        self.output_queue = queue.Queue()
        self.is_thinking = False

    def ask(self, question, callback=None):
        """
        Procesa una pregunta: busca local → web → Claude → memoria.
        Ejecuta en thread separado para no bloquear pygame.

        Args:
            question: Texto de la pregunta
            callback: Función opcional que se llama con updates de estado
        """
        if self.is_thinking:
            return

        self.is_thinking = True
        thread = threading.Thread(target=self._think, args=(question, callback))
        thread.daemon = True
        thread.start()

    def _think(self, question, callback=None):
        """Ejecuta el proceso de pensamiento en background."""
        try:
            # 1. BUSCAR EN MEMORIA LOCAL
            self.state = "searching"
            self._emit("state", "searching")
            self._emit("thought", "Buscando en memoria local...")

            local_results = self.memory.search(question, top_k=3)
            local_score = local_results[0]["score"] if local_results else 0.0

            context = ""
            sources_text = ""

            if local_score > MIN_LOCAL_SCORE:
                # Usamos memoria local
                self._emit("thought", f"Memoria encontrada (score: {local_score:.2f})")
                for result in local_results:
                    context += f"\n[{result['node']['source']}] {result['node']['topic']}\n{result['node']['content']}\n"
                    self.memory.strengthen(result["node"]["id"])
            else:
                # 2. BUSCAR EN INTERNET
                self._emit("thought", "Buscando en Stack Overflow, Wikipedia, GitHub...")
                self.state = "searching"

                web_results = WebCrawler.search_topic(question)
                self.sources_found = web_results

                if web_results:
                    self._emit("thought", f"Encontradas {len(web_results)} fuentes")
                    self.state = "learning"
                    self._emit("state", "learning")

                    for i, result in enumerate(web_results[:5]):
                        context += f"\n[{result['source']}] {result['title']}\n{result['content']}\n"
                        sources_text += f"• {result['source']}: {result['title']}\n"

                    # 3. GUARDAR EN MEMORIA
                    node_id = self.memory.add_node(
                        topic=f"{question[:50]}...",
                        content=context,
                        source="web-search",
                        keywords=question.split()
                    )
                    self._emit("new_node", node_id)

            # 4. PROCESAR CON CLAUDE
            self.state = "processing"
            self._emit("state", "processing")
            self._emit("thought", "Procesando con Claude...")

            user_message = f"""Pregunta: {question}

Contexto de memoria:
{context if context else "(Sin contexto local disponible)"}

Fuentes consultadas:
{sources_text if sources_text else "(Sin búsqueda web)"}

Por favor, responde la pregunta de forma clara y técnica, citando las fuentes."""

            # Llamar Claude con streaming
            self.state = "responding"
            self._emit("state", "responding")
            self._emit("thought", "Generando respuesta...")

            self.response_buffer = ""
            full_response = ""

            with self.client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            ) as stream:
                for text in stream.text_stream:
                    self.response_buffer += text
                    full_response += text
                    self._emit("chunk", text)

            # 5. GUARDAR RESPUESTA EN MEMORIA
            if full_response:
                self.memory.add_node(
                    topic=f"Respuesta: {question[:40]}",
                    content=full_response,
                    source="claude-response",
                    keywords=["respuesta", "usuario"] + question.split()[:5]
                )

            self.state = "idle"
            self._emit("state", "idle")
            self._emit("complete", True)

        except Exception as e:
            self._emit("error", str(e))
            self.state = "idle"
            self._emit("state", "idle")

        finally:
            self.is_thinking = False

    def _emit(self, event_type, data):
        """Emite un evento al queue para pygame."""
        self.output_queue.put({"type": event_type, "data": data})

    def get_output(self):
        """Obtiene el siguiente evento del queue (no-blocking)."""
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None

    def get_stats(self):
        """Retorna estadísticas para el panel."""
        return self.memory.get_stats()

    def get_layout(self):
        """Retorna layout de nodos de memoria para visualizar."""
        return self.memory.get_visual_layout()
