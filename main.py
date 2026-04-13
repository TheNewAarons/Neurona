# main.py
import sys
import math
import random
import pygame
from collections import deque

from neurona_lif import LIFNeuron
from memory import Memory
from brain import NeuronBrain
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, LEFT_PANEL_WIDTH, RIGHT_PANEL_WIDTH,
    BLACK, WHITE, GRAY_DARK, GRAY_MID, GRAY_LIGHT, GRAY_VERY_LIGHT,
    NEURON_BASE_PARAMS, MAX_CHAT_HISTORY, INPUT_MAX_LENGTH, RESPONSE_CHUNK_SIZE,
    ANTHROPIC_API_KEY
)

# === INICIALIZACIÓN PYGAME ===
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Neurona IA Cognitiva - Aprendizaje en Informática")
clock = pygame.time.Clock()
FPS = 60

# === NEURONA BIOLÓGICA ===
neuron = LIFNeuron(**NEURON_BASE_PARAMS)

# === CEREBRO IA ===
try:
    memory = Memory()
    brain = NeuronBrain(memory=memory)
except ValueError as e:
    print(f"Error: {e}")
    print("Por favor configura ANTHROPIC_API_KEY en las variables de entorno.")
    sys.exit(1)

# === ESTADO DE UI ===
chat_history = deque(maxlen=MAX_CHAT_HISTORY)
input_text = ""
is_waiting = False
current_status = "LISTO"
current_thought = ""
visible_response = ""
response_accumulator = ""

# Para animación del streaming
response_buffer_queue = []
response_char_index = 0
response_char_delay = 0

# Dendritas y anatomía neuronal
num_dendrites = 8
dendrites = []
soma_center = (250, 250)

for i in range(num_dendrites):
    angle = (i / num_dendrites) * math.pi * 2
    length = random.randint(80, 120)
    end_x = soma_center[0] + math.cos(angle) * length
    end_y = soma_center[1] + math.sin(angle) * length
    dendrites.append(((end_x, end_y), angle))

axon_end = (soma_center[0] + 150, soma_center[1])

# Partículas visuales
signals = []
spikes = []
spike_flashes = []

# === FUNCIONES DE DIBUJO ===

def draw_left_panel():
    """Dibuja la zona neuronal: red de memoria + neurona LIF."""
    pygame.draw.line(screen, GRAY_MID, (LEFT_PANEL_WIDTH, 0), (LEFT_PANEL_WIDTH, WINDOW_HEIGHT), 1)

    # === Red de nodos de memoria ===
    layout = brain.get_layout()

    # Líneas de conexión entre nodos
    if len(layout) > 1:
        nodes_list = list(layout.values())
        for i in range(len(nodes_list)):
            for j in range(i + 1, min(i + 3, len(nodes_list))):  # Conectar cada nodo con los 2 siguientes
                n1 = nodes_list[i]
                n2 = nodes_list[j]
                pygame.draw.line(screen, GRAY_DARK, (int(n1["x"]), int(n1["y"])), (int(n2["x"]), int(n2["y"])), 1)

    # Nodos visuales
    for node_id, node_data in layout.items():
        color = (node_data["brightness"], node_data["brightness"], node_data["brightness"])
        pygame.draw.circle(screen, color, (int(node_data["x"]), int(node_data["y"])), int(node_data["size"]))

    # === Neurona LIF ===
    # Soma
    voltage = neuron.get_voltage()
    voltage_norm = max(0, min(1, (voltage - neuron.v_reset) / (neuron.v_thresh - neuron.v_reset)))
    base_radius = 18
    halo_intensity = int(100 + 155 * voltage_norm)

    # Halos
    for ring in range(3, 0, -1):
        ring_color = (halo_intensity // (ring + 1), halo_intensity // (ring + 1), halo_intensity // (ring + 1))
        ring_radius = base_radius + ring * 3
        pygame.draw.circle(screen, ring_color, soma_center, ring_radius, 1)

    # Soma base
    pygame.draw.circle(screen, BLACK, soma_center, base_radius)
    pygame.draw.circle(screen, WHITE, soma_center, base_radius, 2)

    # Flash de spike
    if len(spike_flashes) > 0:
        flash_radius = base_radius + 8
        pygame.draw.circle(screen, WHITE, soma_center, flash_radius, 2)

    # Axón
    pygame.draw.line(screen, WHITE, soma_center, axon_end, 2)

    # Spikes en axón
    for sp in spikes:
        sx = soma_center[0] + (axon_end[0] - soma_center[0]) * sp
        pygame.draw.circle(screen, WHITE, (int(sx), int(soma_center[1])), 4)

    # Dendritas
    for (start_pos, angle) in dendrites:
        pygame.draw.line(screen, WHITE, start_pos, soma_center, 1)
        pygame.draw.circle(screen, WHITE, (int(start_pos[0]), int(start_pos[1])), 2)

    # Señales en dendritas
    for s in signals:
        d = dendrites[s['idx']]
        start_pos = d[0]
        px = start_pos[0] + (soma_center[0] - start_pos[0]) * s['progress']
        py = start_pos[1] + (soma_center[1] - start_pos[1]) * s['progress']
        size = 2 + 2 * (1 - s['progress'])
        gray_val = int(200 * (1 - s['progress'] * 0.5))
        pygame.draw.circle(screen, (gray_val, gray_val, gray_val), (int(px), int(py)), int(size))

    # === Osciloscopio ===
    hist_x = 50
    hist_y = 400
    hist_width = 200
    hist_height = 150

    pygame.draw.rect(screen, GRAY_DARK, (hist_x, hist_y, hist_width, hist_height), 1)

    if len(neuron.membrane_history) >= 2:
        points = []
        for i, val in enumerate(neuron.membrane_history):
            px = hist_x + (i / 400) * hist_width
            py = hist_y + hist_height - 20 - (val + 0.2) * 100
            points.append((px, py))

        pygame.draw.lines(screen, WHITE, False, points, 1)

        # Línea de umbral
        th_y = hist_y + hist_height - 20 - (neuron.v_thresh + 0.2) * 100
        pygame.draw.line(screen, GRAY_LIGHT, (hist_x, int(th_y)), (hist_x + hist_width, int(th_y)), 1)


def draw_right_panel():
    """Dibuja la zona cognitiva: estado + chat + input."""

    # === Panel de Estado ===
    status_box = pygame.Rect(RIGHT_PANEL_WIDTH + 20, 20, RIGHT_PANEL_WIDTH - 40, 80)
    pygame.draw.rect(screen, GRAY_DARK, status_box, 1)

    font_label = pygame.font.SysFont("Courier New", 10, bold=True)
    font_text = pygame.font.SysFont("Courier New", 9)

    # Status
    status_text = font_label.render(f"STATUS: {current_status}", True, WHITE)
    screen.blit(status_text, (RIGHT_PANEL_WIDTH + 30, 30))

    # Thought
    thought_text = font_text.render(current_thought[:60], True, GRAY_LIGHT)
    screen.blit(thought_text, (RIGHT_PANEL_WIDTH + 30, 50))

    # Stats
    stats = brain.get_stats()
    stats_text = font_text.render(
        f"NODOS: {stats['total_nodes']} | RATE: {neuron.firing_rate:.1f}Hz",
        True, GRAY_LIGHT
    )
    screen.blit(stats_text, (RIGHT_PANEL_WIDTH + 30, 70))

    # === Chat History ===
    chat_box_y = 120
    chat_box_height = WINDOW_HEIGHT - chat_box_y - 100

    pygame.draw.rect(screen, GRAY_DARK, (RIGHT_PANEL_WIDTH + 20, chat_box_y, RIGHT_PANEL_WIDTH - 40, chat_box_height), 1)

    font_chat = pygame.font.SysFont("Courier New", 8)
    y = chat_box_y + 10

    for message in chat_history:
        color = WHITE if message["role"] == "user" else GRAY_VERY_LIGHT
        prefix = ">" if message["role"] == "user" else "NEURONA:"
        text = font_chat.render(f"{prefix} {message['content'][:70]}", True, color)
        screen.blit(text, (RIGHT_PANEL_WIDTH + 30, y))
        y += 18

        if y > chat_box_y + chat_box_height - 30:
            break

    # === Input Box ===
    input_box_y = WINDOW_HEIGHT - 70
    pygame.draw.rect(screen, GRAY_MID, (RIGHT_PANEL_WIDTH + 20, input_box_y, RIGHT_PANEL_WIDTH - 40, 50), 1)

    input_display = input_text + ("_" if not is_waiting else "")
    input_render = font_chat.render("> " + input_display[:50], True, WHITE)
    screen.blit(input_render, (RIGHT_PANEL_WIDTH + 30, input_box_y + 10))

    help_text = font_chat.render("[ENTER: enviar] [BACKSPACE: borrar] [ESC: salir]", True, GRAY_LIGHT)
    screen.blit(help_text, (RIGHT_PANEL_WIDTH + 30, input_box_y + 28))


def update_neuron(is_thinking):
    """Actualiza el estado de la neurona LIF basado en actividad."""
    # Entrada basada en el estado del cerebro
    input_current = 1.0 if is_thinking else 0.1

    # Ruido basal
    if random.random() < 0.05:
        d_idx = random.randint(0, len(dendrites) - 1)
        signals.append({'idx': d_idx, 'progress': 0.0})

    # Actualizar señales
    for s in signals[:]:
        s['progress'] += 0.02
        if s['progress'] >= 1.0:
            signals.remove(s)
            input_current += 3.0

    # Actualizar neurona
    neuron.update(input_current)

    # Spikes
    if neuron.has_spiked:
        spikes.append(0.0)
        spike_flashes.append(5)

    for i in range(len(spikes) - 1, -1, -1):
        spikes[i] += 0.03
        if spikes[i] > 1.0:
            spikes.pop(i)

    for i in range(len(spike_flashes) - 1, -1, -1):
        spike_flashes[i] -= 1
        if spike_flashes[i] <= 0:
            spike_flashes.pop(i)


def process_brain_output():
    """Procesa los eventos del brain en el output queue."""
    global current_status, current_thought, visible_response, is_waiting, response_accumulator

    event = brain.get_output()
    if event is None:
        return

    event_type = event["type"]
    data = event["data"]

    if event_type == "state":
        states_map = {
            "idle": "LISTO",
            "searching": "BUSCANDO...",
            "processing": "PROCESANDO...",
            "responding": "RESPONDIENDO...",
            "learning": "APRENDIENDO...",
        }
        current_status = states_map.get(data, data)

    elif event_type == "thought":
        current_thought = data

    elif event_type == "chunk":
        # Agregar carácter a la respuesta
        response_accumulator += data

    elif event_type == "complete":
        # Agregar respuesta completa al historial
        if response_accumulator:
            chat_history.append({
                "role": "assistant",
                "content": response_accumulator[:200]  # Mostrar primeros 200 chars
            })
            visible_response = ""
            response_accumulator = ""
        is_waiting = False
        current_status = "LISTO"

    elif event_type == "error":
        chat_history.append({"role": "assistant", "content": f"Error: {data}"})
        is_waiting = False

    elif event_type == "new_node":
        current_thought = f"Nodo guardado en memoria: {data[:8]}..."


def handle_input():
    """Maneja eventos de entrada del usuario."""
    global input_text, is_waiting, current_status, current_thought

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]

            elif event.key == pygame.K_RETURN:
                if input_text.strip() and not is_waiting:
                    # Enviar pregunta
                    chat_history.append({"role": "user", "content": input_text})
                    brain.ask(input_text)
                    is_waiting = True
                    current_status = "BUSCANDO..."
                    current_thought = "Iniciando búsqueda..."
                    input_text = ""

            elif event.unicode.isprintable() and len(input_text) < INPUT_MAX_LENGTH:
                input_text += event.unicode

    return True


def run():
    """Loop principal."""
    running = True

    while running:
        running = handle_input()

        # Limpiar pantalla
        screen.fill(BLACK)

        # Procesar salida del brain
        for _ in range(10):  # Procesar múltiples eventos
            process_brain_output()

        # Actualizar neurona
        update_neuron(is_waiting)

        # Dibujar
        draw_left_panel()
        draw_right_panel()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()
