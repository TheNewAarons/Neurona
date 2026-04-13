# Neurona v3.0 — Cognitive Neuron Simulator with Real-Time AI Learning

A biologically-accurate interactive neuron simulator that combines the Leaky Integrate-and-Fire (LIF) mathematical model with real-time cognitive learning powered by Claude AI. The system integrates local knowledge management through TF-IDF similarity search with dynamic web scraping from multiple technical sources, creating an educational platform that demonstrates how biological neural dynamics interact with artificial intelligence.

## Overview

Neurona v3.0 represents the third iteration of an educational neuron simulation framework:

- **v1.0**: Single LIF neuron with oscilloscope visualization
- **v2.0**: Dual-neuron network with synaptic plasticity and spike-frequency adaptation
- **v3.0**: Cognitive neuron with Claude API integration, local vector store, and multi-source web learning

This version combines neuroscience, information retrieval, and conversational AI into a unified educational system that learns computer science concepts in real-time through interaction.

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.8+ | Core implementation |
| Rendering | Pygame 2.5.0+ | Real-time visualization at 60 FPS (1600×900) |
| AI Engine | Anthropic Claude API | Streaming response generation and reasoning |
| Memory Store | JSON + Manual TF-IDF | Local knowledge storage and retrieval |
| Web Scraping | requests + BeautifulSoup4 | Technical content aggregation |
| Data Sources | Stack Overflow, Wikipedia, GitHub, HackerNews, DEV.to | Free API-based information sources |
| Visual Design | Grayscale (black/white/gray) | Minimalist aesthetic |

## Core Architecture

The system is organized into six specialized modules that work together in a cohesive pipeline:

```
User Input
    ↓
Brain.ask() — Orchestration Thread
    ├─ Search local memory (TF-IDF)
    │   └─ If score < 0.3: Web scraping
    │       ├─ Stack Overflow
    │       ├─ Wikipedia
    │       ├─ GitHub
    │       ├─ HackerNews
    │       └─ DEV.to
    ├─ Build context with sources
    ├─ Claude API (streaming)
    └─ Save to memory.json
        ↓
    Main UI Loop (60 FPS)
    ├─ Render neuron visualization
    ├─ Display memory network
    ├─ Stream response text
    └─ Update statistics
```

## Module Specifications

### 1. neurona_lif.py — Biological Neuron Model

Implements the Leaky Integrate-and-Fire model with Spike-Frequency Adaptation (SFA):

**Physical Parameters:**
- `v_rest = 0.0` — Resting membrane potential (mV)
- `v_thresh = 1.0` — Firing threshold (mV)
- `v_reset = -0.2` — Post-spike hyperpolarization (mV)
- `tau_m = 25.0` — Membrane time constant (ms)
- `tau_adap = 150.0` — Adaptation time constant (ms)
- `delta_adap = 0.25` — Adaptation increment per spike
- `t_ref = 8.0` — Absolute refractory period (ms)

**Differential Equations:**
```
dI_adap/dt = -I_adap / tau_adap
dv/dt = (-(v - v_rest) + R_m * (I_excit - I_inhib - I_adap)) / tau_m

On spike:
  I_adap ← I_adap + delta_adap
  v ← v_reset
  spike ← True
```

**Methods:**
- `update(I_excit, I_inhib=0.0)` → Returns boolean spike flag
- `get_voltage()` → Current membrane potential
- `get_stats()` → Dictionary containing voltage, firing_rate (Hz), spike_count, refractory percentage, adaptation
- `reset()` → Full state reset to baseline

**Features:**
- Separate excitatory and inhibitory input channels
- Frequency adaptation that causes "neural fatigue" (realistic spike trains)
- 400-sample voltage history buffer for visualization
- Real-time firing rate calculation with exponential smoothing

### 2. memory.py — Local Vector Store with TF-IDF Search

Implements a manual vector store for knowledge management without external ML libraries:

**Data Structure (memory.json):**
```json
{
  "nodes": [
    {
      "id": "uuid-string",
      "topic": "Python recursion",
      "content": "Recursion is a technique where a function calls itself...",
      "source": "stackoverflow.com",
      "keywords": ["recursion", "function", "python"],
      "timestamp": "2026-04-10T14:30:00Z",
      "access_count": 3,
      "weight": 0.85
    }
  ],
  "connections": [
    {
      "from": "uuid-1",
      "to": "uuid-2",
      "strength": 0.72
    }
  ]
}
```

**Search Algorithm (TF-IDF with Cosine Similarity):**
1. Tokenize query string → Term frequency dictionary
2. For each stored node: tokenize content → TF dictionary
3. Compute cosine similarity: `dot_product / (magnitude1 * magnitude2)`
4. Apply weight boost: `similarity * (0.5 + 0.5 * node_weight)`
5. Return top-k results sorted by final score

**Methods:**
- `add_node(topic, content, source, keywords)` → Adds knowledge, returns node_id
- `search(query, top_k=5)` → Returns list of dicts: `[{"node": {...}, "score": 0.82}, ...]`
- `strengthen(node_id)` → Increments weight when accessed (boosts future ranking)
- `get_visual_layout(max_nodes=80)` → Spring-force layout positions for network visualization
- `get_stats()` → Returns stats: total_nodes, unique_topics, sources, avg_weight, total_accesses

**Characteristics:**
- No external ML dependencies (pure Python)
- Persistent JSON storage (human-readable)
- Automatic weight decay for stale knowledge
- O(n*m) search complexity (n nodes, m query terms)

### 3. crawler.py — Multi-Source Web Scraper

Fetches real-time technical content from five free public APIs without authentication:

**Data Sources:**

| Source | API | Primary Content |
|--------|-----|-----------------|
| Stack Overflow | StackExchange API | Q&A by relevance |
| Wikipedia | MediaWiki API | Article summaries and sections |
| GitHub | GitHub Search API | Trending repositories, code examples |
| HackerNews | Official API | Top stories and discussion threads |
| DEV.to | Community API | Technical articles and tutorials |

**Return Format (Standardized):**
```python
{
    "source": "stackoverflow.com",
    "title": "How to write recursive functions",
    "content": "Full text content extracted and cleaned",
    "url": "https://stackoverflow.com/questions/..."
}
```

**Methods:**
- `search_topic(query, sources=None)` → Multi-source search, returns list of results
- `fetch_stackoverflow(query, max_results=3)` → Top Q&A results
- `fetch_wikipedia(query)` → Article summary
- `fetch_github(query, max_results=3)` → Repository listings
- `fetch_hackernews(query, max_results=3)` → Top stories
- `fetch_devto(query, max_results=3)` → Recent articles

**Error Handling:**
- Timeouts: 10 seconds per request
- Rate limiting: Built-in delays between requests
- Graceful fallback: Returns empty list on API failure
- Content cleaning: HTML tags removed, whitespace normalized

### 4. brain.py — Claude API Orchestration Engine

Manages the complete learning pipeline with thread-safe non-blocking architecture:

**State Machine:**
```
IDLE → SEARCHING → PROCESSING → RESPONDING → LEARNING → IDLE
```

**System Prompt Strategy:**
The brain constructs dynamic prompts that include:
1. Core system instructions (from config.SYSTEM_PROMPT)
2. Retrieved memory context (if local score > threshold)
3. Web search results (if score ≤ threshold)
4. Request for source attribution
5. Instruction to format response for educational clarity

**Processing Pipeline:**
```
ask(question)
  ├─ Search memory: TF-IDF.search(question)
  ├─ If score < MIN_LOCAL_SCORE (0.3):
  │   └─ Crawl web: search_topic(question)
  ├─ Build prompt with context
  ├─ Stream Claude response character-by-character
  │   └─ Each chunk → output_queue (non-blocking)
  ├─ Save to memory: add_node(topic, response, source)
  └─ Emit event: COMPLETE
```

**Methods:**
- `ask(question, callback=None)` → Starts background thread, returns immediately
- `get_output()` → Non-blocking queue check, returns next event or None
- `get_stats()` → Returns memory statistics
- `get_layout()` → Returns node positions for visualization

**Threading Model:**
- Main thread: Pygame loop maintains 60 FPS
- Background thread: Brain.ask() runs independently
- Communication: Thread-safe `queue.Queue` prevents UI freezing
- Synchronization: No locks—queue guarantees atomic operations

**API Configuration:**
- Model: `claude-haiku-4-5-20251001` (fast, cost-effective for education)
- Max tokens: 1024 (balance between quality and latency)
- Temperature: Inherited from Claude API defaults
- Streaming: Enabled for character-by-character response

### 5. main.py — Pygame Visualization and User Interface

Renders a dual-panel interactive interface at 60 FPS:

**Layout (1600×900 px):**

```
LEFT PANEL (750px)              RIGHT PANEL (850px)
├─ Memory Network Graph          ├─ Status Panel
│  ├─ Spring-force layout         │  ├─ Status text (IDLE/SEARCHING/etc)
│  ├─ Size ∝ weight              │  ├─ Node count
│  ├─ Brightness ∝ recency       │  └─ Firing rate (Hz)
│  └─ Lines show connections     │
│                                ├─ Chat History
├─ LIF Neuron Visualization      │  ├─ Scrollable (last 30 messages)
│  ├─ Soma (circular pulsing)    │  ├─ User input (">") in white
│  ├─ Dendrites (branching)      │  └─ Neurona output in gray
│  ├─ Axon (spike transmission)  │
│  └─ Halos indicating state     ├─ Input Box
│                                │  ├─ Text input field
├─ Oscilloscope                  │  ├─ Cursor animation
│  ├─ Voltage trace (400 samples)│  └─ Character counter
│  ├─ Grid overlay               │
│  └─ Real-time update           └─ Help Text
└─                                  └─ Control hints
```

**Visual States:**

| State | Neuron Behavior | Dendritic Display | Purpose |
|-------|-----------------|-------------------|---------|
| IDLE | Slow oscillation, dim soma | Slow, sparse signals | Waiting for input |
| SEARCHING | Fast soma pulsing | Rapid branching signals | Querying web APIs |
| PROCESSING | Maximum frequency pulsing | Intense dendritic activity | Claude API processing |
| RESPONDING | Axon illuminated bright white | Stable high firing | Streaming response text |
| LEARNING | New nodes fade in progressively | Network reorganizes | Saving to memory |

**Rendering Pipeline (60 FPS):**
1. Clear screen with black background
2. Update neuron state (via LIF model)
3. Draw left panel: memory network + neuron + oscilloscope
4. Draw right panel: status + chat + input box
5. Poll brain.get_output() for new events
6. Update text buffer on CHUNK event
7. Display frame

**Interaction Model:**
- ENTER: Submit question to brain
- BACKSPACE: Delete last character from input
- ESC: Graceful shutdown
- Auto-scroll chat history when new messages arrive

### 6. config.py — Centralized Configuration

Single source of truth for all system parameters:

```python
# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# Memory Configuration
MEMORY_FILE = "memory.json"
MAX_MEMORY_NODES = 500
MIN_LOCAL_SCORE = 0.3  # Threshold to trigger web search

# Search Configuration
TF_IDF_TOP_K = 5  # Results per search
WEB_SEARCH_TIMEOUT = 10  # seconds

# UI Configuration
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LEFT_PANEL_WIDTH = 750
FPS = 60

# Neuron Parameters
V_REST = 0.0
V_THRESH = 1.0
V_RESET = -0.2
TAU_M = 25.0
TAU_ADAP = 150.0
DELTA_ADAP = 0.25
T_REF = 8.0

# System Prompt for Claude
SYSTEM_PROMPT = """You are Neurona, an educational cognitive neuron that learns..."""
```

## Installation and Setup

### Prerequisites

- Python 3.8 or later
- pip package manager
- Active internet connection (for web scraping)
- Anthropic API key (free tier available)

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/Neurona.git
cd Neurona

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"

# 5. Run the simulator
python main.py
```

**Dependencies** (requirements.txt):
```
pygame>=2.5.0
anthropic>=0.7.0
requests>=2.28.0
beautifulsoup4>=4.11.0
```

## Usage Guide

### Launching the Application

```bash
python main.py
```

The application will initialize with:
1. Empty memory (if memory.json does not exist)
2. Neural oscillator at rest
3. Ready to accept questions

### User Interface Controls

| Key | Action |
|-----|--------|
| ENTER | Submit question to Neurona |
| BACKSPACE | Delete last character |
| ESC | Graceful exit |

### Interactive Example

```
> What is tail recursion?

[STATUS: BUSCANDO... - Web APIs being queried]

NEURONA: Tail recursion is a special form of recursion where the
recursive call is the last operation in the function. It allows
compiler optimization...

[New node "tail recursion" added to memory]
[Network visualization updates]

> Show me a Python example

[STATUS: SEARCHING (local memory)]

NEURONA: def factorial(n, acc=1):
         if n <= 1: return acc
         return factorial(n-1, n*acc)

[Retrieved from local memory - no web search needed]
```

## Learning Flow and Algorithm

### First Query: Cold Start (Empty Memory)

1. User enters question: "What is recursion?"
2. Brain searches memory: score = 0.0 (empty database)
3. Threshold check: 0.0 < 0.3 → trigger web search
4. Crawler initiates parallel requests to 5 sources
5. Results aggregated and cleaned
6. Claude processes with full context and sources
7. Response streams character-by-character to UI
8. New node saved: `{"topic": "recursion", "content": "...", "source": "web-search"}`
9. Node appears in network visualization with initial weight 0.5

**Latency: 2-5 seconds** (dominated by web scraping + first token latency)

### Second Query: Warm Start (Memory Hit)

1. User enters similar question: "Show me recursion in Python"
2. Brain searches memory: score = 0.78 (FOUND)
3. Threshold check: 0.78 > 0.3 → use local context only
4. No web search triggered
5. Claude processes with local context (instant)
6. Response streams immediately
7. Node weight increases: 0.5 → 0.52
8. Node access_count incremented: 1 → 2

**Latency: 100-300ms** (API-only, no web scraping)

### Third Query: Partial Match (Augmented Search)

1. User enters: "Why is recursion slow?"
2. Brain searches memory: score = 0.42 (partial match)
3. Threshold check: 0.42 > 0.3 → use local context + augment with web
4. Web search for "recursion performance" supplements local knowledge
5. Claude combines local context with fresh sources
6. Response quality improves due to hybrid approach
7. New node for performance aspect created

**Latency: 800-2000ms** (balanced approach)

### Accumulated Learning

After 20+ questions, the neuron exhibits:
- Faster responses for repeated topics (local memory)
- Richer context from accumulated knowledge
- Visual growth of the memory network
- Reduced API costs (fewer web searches)
- Improved answer quality through diverse source integration

## Performance Characteristics

### Time Complexity
- Local search (TF-IDF): O(n·m) where n = nodes, m = query terms
- Web scraping: O(1) per source (parallel execution)
- Claude streaming: O(1) per token
- Visualization: O(n) for n nodes in network

### Space Complexity
- Memory.json (500 nodes): 5-10 MB
- Chat history buffer: ~1 MB
- Voltage history (400 samples): ~8 KB
- Total runtime: ~200 MB

### Rendering
- Frame rate: Constant 60 FPS (maintained by non-blocking architecture)
- Neuron update rate: 1 ms per timestep (biological accuracy)
- Network layout: Recomputed every 500 ms (spring forces)
- Text rendering: Cached glyph surfaces (efficient Pygame)

### Network
- Web scraping timeout: 10 seconds total
- Claude first token latency: 100-500 ms
- Token streaming rate: 50-100 ms per token
- Total response time: 2-5 seconds (cold), 100-300 ms (warm)

## Architecture Design Decisions

### Why Manual TF-IDF Instead of Embeddings?
- Educational transparency: users can understand the algorithm
- No external dependencies (scikit-learn, transformers)
- Fast startup and minimal memory overhead
- Deterministic results (no model variability)
- Easy to debug and visualize

### Why Separate Web Search Threshold?
- Balance between local speed and knowledge freshness
- Avoids costly API calls for well-known topics
- User configurable via `MIN_LOCAL_SCORE` parameter
- Encourages organic memory growth

### Why Non-Blocking Threading?
- 60 FPS visualization never blocked by network I/O
- User interaction remains responsive during learning
- Queue-based communication prevents race conditions
- Simple synchronization without locks

### Why Multiple Web Sources?
- Diverse perspectives on technical topics
- Redundancy if one API is temporarily unavailable
- Source attribution in responses
- Reduces bias from single information source

## Troubleshooting

### Issue: ANTHROPIC_API_KEY Not Configured

**Error Message:**
```
RuntimeError: ANTHROPIC_API_KEY environment variable not set
```

**Solution:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-actual-api-key"
python main.py
```

Verify with:
```bash
echo $ANTHROPIC_API_KEY
```

### Issue: Web Scraping Returns Empty Results

**Possible Causes:**
1. Network connectivity issue
2. API rate limiting (Stack Overflow has strict limits)
3. Query terms too specific or too vague
4. One or more API endpoints temporarily offline

**Solutions:**
- Check internet connection: `ping google.com`
- Simplify query: "recursion" instead of "what is tail call optimization in functional programming"
- Increase `MIN_LOCAL_SCORE` in config.py to rely more on local memory
- Wait 30 minutes (Stack Overflow API has 30-request/second limit)

### Issue: Responses Are Slow or Incomplete

**Possible Causes:**
1. Cold start (first query always triggers web search)
2. API quota exceeded (Anthropic free tier limits)
3. Large memory.json file (search becomes O(n) slow)
4. Network latency

**Solutions:**
- First query is expected to be slow (2-5 seconds)
- Verify Anthropic API quota: https://console.anthropic.com/
- Reduce `MAX_MEMORY_NODES` or delete memory.json to reset
- Check network speed: `curl -w "@curl-format.txt" -o /dev/null -s https://www.google.com`

### Issue: Pygame Window Won't Open

**Error Message:**
```
pygame.error: No video mode set
```

**Solution:**
- Ensure display is available (not headless server)
- Check X11 forwarding if over SSH
- Verify pygame installation: `python -c "import pygame; print(pygame.display.get_init())"`

### Issue: Memory.json Grows Too Large

**Symptoms:**
- Slow searches over time
- Large file size (>50 MB)
- Application sluggishness

**Solution:**
```bash
# Option 1: Delete and restart (memory resets)
rm memory.json
python main.py

# Option 2: Reduce MAX_MEMORY_NODES in config.py
# Change MAX_MEMORY_NODES = 500 to 250
# Edit config.py and restart

# Option 3: Manual cleanup
# Edit memory.json and remove low-weight nodes (weight < 0.2)
```

## Development and Testing

### Running Unit Tests

```bash
python -m pytest test_lif.py -v
```

### Testing Individual Modules

**Test Memory Search:**
```python
from memory import Memory

m = Memory()
m.add_node("Python", "Functions are reusable blocks...", "wikipedia", ["python", "function"])
results = m.search("Python functions")
print(results)  # [{"node": {...}, "score": 0.85}, ...]
```

**Test Web Scraper:**
```python
from crawler import WebCrawler

results = WebCrawler.search_topic("recursion")
for r in results:
    print(f"{r['source']}: {r['title']}")
```

**Test Brain Orchestration:**
```python
from brain import NeuronBrain

brain = NeuronBrain()
brain.ask("What is big O notation?")

while True:
    event = brain.get_output()
    if event:
        print(event)
    if event.get('type') == 'complete':
        break
```

## Educational Value

This project demonstrates:

1. **Neuroscience**: Spike-Frequency Adaptation (SFA) creates realistic neural behavior
2. **Information Retrieval**: TF-IDF and cosine similarity for relevance ranking
3. **API Integration**: Real-time data aggregation from multiple sources
4. **Conversational AI**: Claude API with context-aware prompt engineering
5. **Real-time Graphics**: Pygame for 60 FPS simulation visualization
6. **Concurrent Programming**: Thread-safe queue communication patterns
7. **System Design**: Modular architecture with clean separation of concerns

Students can modify parameters in config.py to observe how learning speed, memory size, and response quality change.

## References and Citations

- **Leaky Integrate-and-Fire Model**: https://en.wikipedia.org/wiki/Leaky_integrate-and-fire
- **Spike-Frequency Adaptation**: Lundstrom et al., "Biophysical basis of burst firing in neocortical pyramidal neurons" (Journal of Neuroscience, 2008)
- **TF-IDF and Information Retrieval**: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- **Claude API Documentation**: https://docs.anthropic.com/
- **Pygame Documentation**: https://www.pygame.org/docs/
- **Stack Overflow API**: https://api.stackexchange.com/docs/
- **Spring-Force Graph Layout**: https://en.wikipedia.org/wiki/Force-directed_graph_drawing

## License

This project is provided for educational purposes. No restrictive license applied.

## Acknowledgments

Developed as an educational exploration of the intersection between biological neuroscience, artificial intelligence, and human-computer interaction. Inspired by computational neuroscience research and modern conversational AI capabilities.

---

For issues, questions, or contributions, please open a GitHub issue.
