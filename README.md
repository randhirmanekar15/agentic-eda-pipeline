# Agentic EDA Pipeline

Drop a CSV in, get analysis code, charts, and a written report out. Two agents — a **Coder** that writes and runs exploration code, and an **Analyst** that interprets the results — running fully locally on [Ollama](https://ollama.com).

## Key idea: schema, not data

The model only ever sees a compact schema snapshot (dtypes, head, describe), never the full file. A 2-million-row CSV and a 200-row CSV produce nearly the same prompt — so it works on real datasets, not just toy ones.

## Stack

| Piece | Choice |
|-------|--------|
| Runtime | Ollama (local) |
| Model | `qwen3-coder` |
| Data | pandas |
| Charts | matplotlib (headless) |

## Setup

```bash
ollama pull qwen3-coder
pip install -r requirements.txt
```

## Usage

```bash
python agent.py data.csv
```

Outputs: `charts/*.png`, `report.md`, and `generated_eda.py` (the code the Coder agent produced, kept for review).

## Test

```bash
pip install pytest
pytest
```

## Limitations

- Local models can over-read a correlation — treat the report as a fast first draft.
- It describes; it does not run statistical tests. Adding a stats agent is the obvious next layer.

---

Inspired by Aman Kharwal's tutorial, [Agentic AI Pipeline to Automate EDA](https://amanxai.com/2026/03/04/agentic-ai-pipeline-to-automate-eda/). Rebuilt and extended (schema-only prompting, headless chart saving, saved report + generated code).

MIT licensed.
