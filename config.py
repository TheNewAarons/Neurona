# config.py
import os

# === API Configuration ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # Fast + cost-effective

# === Memory Configuration ===
MEMORY_FILE = "memory.json"
MAX_MEMORY_NODES = 500
SEARCH_TOP_K = 5
MIN_LOCAL_SCORE = 0.3  # Si el score local es menor, buscar en internet

# === Web Crawler Configuration ===
SEARCH_TIMEOUT = 10  # segundos
CRAWLER_SOURCES = ["stackoverflow", "wikipedia", "github", "hackernews", "devto"]

# === Visualization Configuration ===
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LEFT_PANEL_WIDTH = 750  # Zona neuronal
RIGHT_PANEL_WIDTH = 850  # Zona cognitiva

# === Colors (B/W + Grays) ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_DARK = (30, 30, 30)
GRAY_MID = (80, 80, 80)
GRAY_LIGHT = (160, 160, 160)
GRAY_VERY_LIGHT = (200, 200, 200)

# === LIF Neuron Parameters ===
NEURON_BASE_PARAMS = {
    "dt": 1.0,
    "v_rest": 0.0,
    "v_thresh": 1.0,
    "v_reset": -0.2,
    "tau_m": 25.0,
    "r_m": 1.0,
    "tau_adap": 150.0,
    "delta_adap": 0.25,
    "t_ref": 8.0
}

# === Chat Configuration ===
MAX_CHAT_HISTORY = 30  # líneas visibles
INPUT_MAX_LENGTH = 200
RESPONSE_CHUNK_SIZE = 50  # caracteres por frame en streaming

# === System Prompt for Brain ===
SYSTEM_PROMPT = """Eres una neurona cognitiva especializada en informática, programación, redes, bases de datos, algoritmos, ciberseguridad y tecnologías modernas.

Tus características:
- Respondes con precisión técnica y ejemplos de código cuando sea relevante
- Citas las fuentes de donde aprendiste (Stack Overflow, Wikipedia, GitHub, etc.)
- Mantienes un tono profesional pero accesible
- Explicas conceptos complejos de forma progresiva
- Eres conciso pero completo en tus respuestas
- Usas formato markdown para código

Cuando se te proporciona contexto de memoria local, úsalo como base. Si hay información de web scraping,
intégrala naturalmente. Siempre da crédito a las fuentes."""
