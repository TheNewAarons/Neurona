# ⚡ Setup Rápido - Neurona v3.0

## 1️⃣ Obtener API Key

Visita: https://console.anthropic.com/

- Crea una cuenta (gratis)
- Copia tu API key (formato: `sk-ant-...`)

## 2️⃣ Instalar Dependencias

```bash
cd Neurona
pip install -r requirements.txt
```

Espera ~30 segundos. Si hay errores, verifica:
- Python 3.8+ instalado: `python --version`
- pip actualizado: `pip install --upgrade pip`

## 3️⃣ Configurar API Key

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

**Windows (cmd):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-...
```

## 4️⃣ ¡Ejecutar!

```bash
python main.py
```

## ✅ Debería ver

- Ventana de 1600×900 píxeles
- Panel izquierdo: red de memoria (vacía al inicio)
- Centro: neurona biológica
- Panel derecho: chat interactivo
- Texto: "STATUS: LISTO"

## 🤖 Tu Primera Pregunta

Escribe en el input box:

```
¿Qué es una función recursiva?
```

Presiona ENTER.

**Verás:**
1. STATUS: "BUSCANDO..." → la neurona busca en internet
2. STATUS: "PROCESANDO..." → Claude procesa
3. STATUS: "RESPONDIENDO..." → respuesta en streaming (letra por letra)
4. Nodo nuevo aparece en la red (panel izquierdo)

## 🎯 Segunda Pregunta

```
Dame un ejemplo de recursión en Python
```

Presiona ENTER.

**Diferencia:**
- Más RÁPIDA (1-2 seg vs 3-5 seg)
- STATUS: "BUSCANDO..." es breve
- Usa memoria local (TF-IDF)

## 🛑 Para Salir

Presiona ESC

## 🐛 Solución de Problemas

**Error: "ANTHROPIC_API_KEY no configurada"**
- ✗ Olvidaste `export ANTHROPIC_API_KEY`
- ✓ Verifica: `echo $ANTHROPIC_API_KEY`

**Error: "ModuleNotFoundError: No module named 'pygame'"**
- ✗ Dependencias no instaladas
- ✓ Ejecuta: `pip install -r requirements.txt`

**La neurona no busca en internet**
- Verifica conexión a internet
- Las APIs (Stack Overflow, Wikipedia) a veces caen
- Intenta otra pregunta

**Respuesta vacía o incompleta**
- Verifica tu API key tiene créditos
- Intenta una pregunta más corta y específica

## 📚 Ejemplos de Preguntas

```
¿Qué es machine learning?
¿Cómo funciona un puntero en C?
Explica el patrón MVC
¿Diferencia entre var, let y const en JavaScript?
¿Cómo funcionan las cookies del navegador?
¿Qué es la complejidad algorítmica Big O?
Explica el concepto de closure en programación
¿Cómo se optimiza una base de datos SQL?
```

## 💡 Tips

1. **Primera pregunta es lenta** — es normal, está buscando en internet
2. **Preguntas similares son rápidas** — usa memoria local
3. **La neurona aprende** — `memory.json` crece automáticamente
4. **No hay límite de preguntas** — el archivo crece pero es eficiente hasta 500+ nodos
5. **Borra memory.json para reset** — la neurona "olvida" todo

## 🎓 Ver Qué Aprendió

Abre `memory.json` en un editor de texto:

```json
{
  "nodes": [
    {
      "topic": "Respuesta: ¿Qué es recursión?",
      "content": "...",
      "source": "claude-response",
      "weight": 0.85,
      "access_count": 1
    }
  ]
}
```

Cada pregunta = nuevo nodo guardado

## ⏱️ Tiempo Típico

| Acción | Tiempo |
|--------|--------|
| Startup | <1 seg |
| Primera pregunta | 3-5 seg |
| Preguntas siguientes | 1-2 seg |
| Guardar en memoria | <100 ms |
| Buscar en memoria | <100 ms |

## 🔑 Variables de Entorno

Si quieres hacerlo permanente (macOS/Linux):

```bash
# Edita tu ~/.bash_profile o ~/.zshrc
export ANTHROPIC_API_KEY="sk-ant-..."

# Recarga
source ~/.bash_profile
```

## 📱 Paneles de la Interfaz

```
┌────────────────────────────────────────────────────────────────────┐
│ ZONA NEURONAL (izq)         │ ZONA COGNITIVA (der)               │
│                             │                                    │
│ Red de nodos de memoria     │ STATUS: [LISTO]                    │
│ (crece con aprendizaje)     │ PENSANDO: [mensaje de proceso]     │
│                             │ NODOS: X | RATE: X Hz             │
│ Neurona LIF (soma+dendritas)│                                    │
│ (pulsante según actividad)  │ [HISTORIAL CHAT]                   │
│                             │ > Tu pregunta aquí                │
│ Osciloscopio de voltaje     │ NEURONA: Respuesta aquí...       │
│ (voltaje en tiempo real)    │                                    │
│                             │ > [INPUT]                        │
└────────────────────────────────────────────────────────────────────┘
```

## 🎉 ¡Listo!

Ya tienes una **neurona biológica inteligente** que:
- ✅ Aprende del internet en tiempo real
- ✅ Guarda conocimiento en memoria
- ✅ Responde cada vez más rápido
- ✅ Visualiza su proceso de aprendizaje

**¡Felicidades! 🚀**
