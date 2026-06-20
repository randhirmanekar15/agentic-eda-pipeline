# Drop a CSV, Get a Data Analysis — I Built an Agentic EDA Pipeline

*Two AI agents — a Coder and an Analyst — that turn a raw CSV into analysis code, charts, and a written report. Running locally, no API keys. Here's how I built it and where multi-agent design actually earns its keep.*

---

## Why two agents instead of one

The defining shift in agentic AI right now isn't smarter single models — it's **orchestrated teams of specialized agents replacing the one all-purpose agent.** Gartner reported a **1,445% surge in multi-agent system inquiries** between early 2024 and mid-2025, and the framework world has organized around it: LangGraph for stateful, auditable workflows; CrewAI for fast role-based crews.

Exploratory data analysis is a clean place to feel why this matters. EDA is genuinely two jobs:

1. **Writing and running analysis code** (a coder's job).
2. **Interpreting what the numbers mean** (an analyst's job).

Cram both into one prompt and you get mush — code half-explained, insight half-computed. Split them into two agents with one job each, and the output gets sharper. That's the single-prompt-to-multi-agent lesson in miniature.

## What it does

Point it at a CSV. The pipeline:

1. Extracts a **schema snapshot** (dtypes, head, describe) — not the whole file.
2. The **Coder agent** writes Python to explore the data and save 3–4 charts.
3. That code runs against the real DataFrame; charts land in `./charts/`.
4. The **Analyst agent** reads the output and writes a markdown EDA report with findings and next steps.

## The stack

| Piece | Choice | Why |
|-------|--------|-----|
| Runtime | Ollama (local) | Free, private, no keys |
| Model | `qwen3-coder` | Strong at both code-gen and summarizing |
| Data | pandas | Standard |
| Charts | matplotlib (headless) | Saves PNGs, no GUI needed |

## The one design decision that matters: schema, not data

The biggest mistake in LLM-over-data projects is dumping the whole CSV into the prompt. You blow the context window and pay for tokens that teach the model nothing. Instead I send a compact snapshot:

```python
def schema_snapshot(df: pd.DataFrame) -> str:
    buf = io.StringIO()
    df.info(buf=buf)
    return (
        f"COLUMNS/DTYPES:\n{buf.getvalue()}\n"
        f"HEAD:\n{df.head().to_string()}\n"
        f"DESCRIBE:\n{df.describe(include='all').to_string()}"
    )
```

The model sees the *shape* of the data — column names, types, ranges, a few rows — which is all it needs to write good analysis code. A 2-million-row file and a 200-row file produce nearly the same prompt. This is the difference between a pipeline that works on toy CSVs and one that works on real ones.

## The two agents

**Coder agent** — gets the schema, writes exploration code, saves charts. It never reads the file itself; the DataFrame already exists in its execution environment:

```python
def coder_agent(schema: str) -> str:
    prompt = (
        "You are a senior data scientist. A pandas DataFrame named `df` already exists.\n"
        "Write Python that explores `df`: print key stats and create 3-4 useful charts.\n"
        "Save EVERY chart with plt.savefig(CHART_DIR / 'name.png'); plt.close() after each.\n"
        "Do NOT read any file, do NOT call plt.show(). Return ONLY code.\n\n"
        f"Here is the schema:\n{schema}"
    )
    ...
```

**Analyst agent** — gets the schema plus whatever the code printed, and writes the human-facing report:

```python
def analyst_agent(schema: str, exec_output: str) -> str:
    prompt = (
        "You are a lead data analyst. Given the schema and the analysis output, "
        "write a concise markdown EDA report: key findings, data quality notes, "
        "and 3 suggested next steps. Be specific to the numbers.\n\n"
        f"SCHEMA:\n{schema}\n\nANALYSIS OUTPUT:\n{exec_output}"
    )
    ...
```

The handoff between them — code output becoming the analyst's input — is the whole multi-agent pattern in two function calls.

## What I changed from the original tutorial

Inspired by Aman Kharwal's **["Agentic AI Pipeline to Automate EDA"](https://amanxai.com/2026/03/04/agentic-ai-pipeline-to-automate-eda/)**. My rebuild:

- **Wired to `qwen3-coder` locally** instead of the original model.
- **Schema-only prompting** so large CSVs never overflow the context window.
- **In-process execution against the real DataFrame**, with charts saved to disk instead of shown — so it runs headless and the output is portable.
- **The Analyst writes `report.md`** (a sharable artifact) rather than console-only text, and **the generated code is saved to `generated_eda.py`** so every run is reproducible and reviewable.

## Where it breaks

- **Local models hallucinate insights.** The Analyst can confidently over-read a correlation. Treat its report as a fast first draft, not a conclusion.
- **Generated code can still error.** I catch execution failures and fold them into the report instead of crashing, but a failed chart is a failed chart.
- **No statistical rigor by default.** It describes; it doesn't test hypotheses. Adding a stats agent (significance tests, not just `describe()`) is the obvious next layer.

## Takeaway

EDA was the right first multi-agent project because the role split is real, not forced — coding and interpreting genuinely are two skills. When you're deciding whether to reach for a multi-agent design, that's the test: **are there actually distinct jobs here, or am I splitting one job to look sophisticated?** If it's the former, the output gets better. If it's the latter, you've just added latency.

**Code:** [github.com/randhirmanekar15/agentic-eda-pipeline](https://github.com/randhirmanekar15/agentic-eda-pipeline)

---

*Inspired by Aman Kharwal's tutorial, ["Agentic AI Pipeline to Automate EDA"](https://amanxai.com/2026/03/04/agentic-ai-pipeline-to-automate-eda/). Rebuilt and extended as described.*

### Sources
- [AI agent trends 2026 — Google Cloud](https://cloud.google.com/resources/content/ai-agent-trends-2026)
- [Best Multi-Agent Frameworks in 2026: LangGraph, CrewAI — Gurusup](https://gurusup.com/blog/best-multi-agent-frameworks-2026)
- [The best AI agent frameworks in 2026 — LangChain](https://www.langchain.com/resources/ai-agent-frameworks)
