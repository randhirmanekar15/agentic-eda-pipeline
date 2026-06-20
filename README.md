# Agentic EDA Pipeline

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-green) ![Runs 100% Local](https://img.shields.io/badge/runs-100%25%20local-orange)

**Drop a CSV in, get analysis code, charts, and a written report out — powered by two local AI agents that never see your raw data.**

## Overview

Most "AI does your data analysis" demos break the moment you feed them a real file. They paste the whole CSV into the prompt, blow past the context window, and either crash or hallucinate. This pipeline does the opposite: the model only ever sees a compact schema snapshot — dtypes, the first few rows, and `describe()` output — never the full file. That one design choice is the difference between a toy that works on 50 rows and a tool that works on 500,000.

Under the hood it runs two agents with distinct jobs. A **Coder** writes and executes pandas/matplotlib exploration code against your actual dataset. An **Analyst** reads the results and writes the interpretation. Splitting these into real roles — rather than asking one model to do everything in a single prompt — is now the 2026 norm for agentic systems, and for good reason: a focused agent with a narrow contract produces tighter, more debuggable output than a generalist trying to code and reason at once.

Everything runs locally through Ollama with `qwen3-coder`. No API keys, no data leaving your machine, no per-token bill. You point it at a CSV and you get back runnable code, saved charts, and a markdown report you can hand to a teammate.

## Features

- **Schema-only prompting** — the model sees dtypes, head, and describe; never the full file, so it scales to real datasets without context overflow.
- **Two-agent design** — a Coder that writes and runs exploration code, an Analyst that interprets the results.
- **Headless chart generation** — matplotlib saves PNGs directly to disk, no display server required.
- **Reproducible output** — the generated exploration code is saved to disk, so you can rerun or audit exactly what ran.
- **Written report** — produces a `report.md` summary, not just raw plots.
- **100% local** — runs entirely on Ollama; no cloud, no API keys, no data egress.

## How it works

You give the pipeline a CSV path. It builds a compact schema snapshot and hands it to the Coder, which writes exploration code. That code is executed locally to produce charts and result tables. Those results — not the raw data — go to the Analyst, which writes the report.

```
   data.csv
      │
      ▼
 ┌──────────┐   schema snapshot
 │  Schema  │   (dtypes, head, describe)
 │ Snapshot │
 └────┬─────┘
      ▼
 ┌──────────┐
 │  CODER   │  writes exploration code
 └────┬─────┘
      ▼
 ┌──────────┐
 │  EXEC    │  runs code → charts/*.png + result tables
 └────┬─────┘
      ▼
 ┌──────────┐
 │ ANALYST  │  interprets results
 └────┬─────┘
      ▼
   report.md  +  generated_eda.py  +  charts/*.png
```

## Tech stack

| Component | Choice | Why |
|-----------|--------|-----|
| LLM runtime | [Ollama](https://ollama.com) | Local, no API keys, no data egress |
| Model | `qwen3-coder` | Strong code generation, runs locally |
| Data | [pandas](https://pandas.pydata.org) | Standard for tabular EDA |
| Charts | [matplotlib](https://matplotlib.org) (headless) | Saves PNGs without a display server |
| Tests | [pytest](https://pytest.org) | Tests pure helpers, no model required |

## Project structure

```
agentic-eda-pipeline/
├── agent.py            # the pipeline: schema snapshot, Coder, exec, Analyst
├── test_agent.py       # tests for pure helper functions
├── ARTICLE.md          # credit + notes on what changed vs the source tutorial
├── requirements.txt
├── LICENSE             # MIT
└── README.md
```

Running the pipeline also produces:

```
charts/*.png            # generated visualizations
generated_eda.py        # the exploration code the Coder wrote
report.md               # the Analyst's written report
```

## Installation

You need [Ollama](https://ollama.com) installed and running first.

```bash
# 1. Pull the model
ollama pull qwen3-coder

# 2. Install Python dependencies
pip install -r requirements.txt

# (optional) for running tests
pip install pytest
```

## Usage

Point it at any CSV:

```bash
python agent.py data.csv
```

What you get back:

- `charts/*.png` — the generated visualizations
- `generated_eda.py` — the exploration code the Coder wrote and ran
- `report.md` — the Analyst's written interpretation of the results

## Configuration

Constants live at the top of `agent.py`:

| Constant | Default | What it controls |
|----------|---------|------------------|
| `MODEL` | `qwen3-coder` | The Ollama model the agents use |
| `CHART_DIR` | `charts` | Where generated PNGs are saved |

## Testing

The tests cover the pure helper functions — schema snapshotting, fence stripping — so they run **without a model or Ollama instance**.

```bash
pip install pytest
pytest
```

## Limitations

- **Local models can over-read correlations.** The Analyst sometimes states relationships more confidently than the data warrants. Treat `report.md` as a first draft, not a conclusion.
- **It describes, it doesn't test.** The pipeline summarizes patterns; it does not run formal statistical tests (no p-values, no significance checks). Bring your own rigor before acting on findings.
- **Output quality tracks the local model.** Results depend on `qwen3-coder`; a stronger model will produce sharper code and tighter analysis.

## Roadmap

- [ ] Optional statistical-test agent (correlation significance, normality checks)
- [ ] Support for multiple file formats (Parquet, Excel)
- [ ] Configurable model selection via CLI flag
- [ ] HTML report export alongside markdown
- [ ] Retry loop when generated code fails to execute

## Credits

📖 Full write-up: [ARTICLE.md](ARTICLE.md).

Based on the tutorial by **Aman Kharwal** — ["Agentic AI Pipeline to Automate EDA"](https://amanxai.com/2026/03/04/agentic-ai-pipeline-to-automate-eda/).

**What I changed vs the source tutorial:**

- **Schema-only prompting** — the model sees dtypes/head/describe instead of the full file, eliminating context overflow on real datasets.
- **Headless chart saving** — matplotlib writes PNGs to disk with no display server.
- **Persisted artifacts** — saves the generated exploration code (`generated_eda.py`) and a written markdown report (`report.md`), not just charts.

## Author

Built by **Randhir Manekar** — [randhirmanekar.com](https://randhirmanekar.com) · [github.com/randhirmanekar15](https://github.com/randhirmanekar15)

## License

MIT — see [LICENSE](LICENSE).
