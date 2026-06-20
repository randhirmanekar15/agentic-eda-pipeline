"""Agentic EDA pipeline.

Two roles: a Coder agent writes exploration code that runs against the real
DataFrame, and an Analyst agent turns the output into a markdown report. Only a
compact schema snapshot is sent to the model, so large CSVs never overflow the
context window.

Inspired by Aman Kharwal's tutorial:
https://amanxai.com/2026/03/04/agentic-ai-pipeline-to-automate-eda/
"""

from __future__ import annotations

import argparse
import io
import re
from contextlib import redirect_stdout
from pathlib import Path

import ollama
import pandas as pd

MODEL = "qwen3-coder:latest"
CHART_DIR = Path("charts")


def strip_fences(text: str) -> str:
    """Remove ```python ... ``` wrappers the model sometimes adds."""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return (match.group(1) if match else text).strip()


def schema_snapshot(df: pd.DataFrame) -> str:
    """Build a compact schema description instead of sending the whole frame."""
    buf = io.StringIO()
    df.info(buf=buf)
    return (
        f"COLUMNS/DTYPES:\n{buf.getvalue()}\n"
        f"HEAD:\n{df.head().to_string()}\n"
        f"DESCRIBE:\n{df.describe(include='all').to_string()}"
    )


def coder_agent(schema: str) -> str:
    """Ask the model for analysis code that saves charts to CHART_DIR."""
    prompt = (
        "You are a senior data scientist. A pandas DataFrame named `df` already exists.\n"
        "matplotlib.pyplot is imported as `plt`. A Path `CHART_DIR` exists for saving figures.\n"
        "Write Python that explores `df`: print key stats and create 3-4 useful charts.\n"
        "Save EVERY chart with plt.savefig(CHART_DIR / 'name.png'); plt.close() after each.\n"
        "Do NOT read any file, do NOT call plt.show(). Return ONLY code, no fences.\n\n"
        f"Here is the schema:\n{schema}"
    )
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return strip_fences(response["message"]["content"])


def analyst_agent(schema: str, exec_output: str) -> str:
    """Ask the model to write a markdown EDA report from the analysis output."""
    prompt = (
        "You are a lead data analyst. Given the dataset schema and the output produced "
        "by the analysis code, write a concise markdown EDA report: key findings, "
        "data quality notes, and 3 suggested next steps. Be specific to the numbers.\n\n"
        f"SCHEMA:\n{schema}\n\nANALYSIS OUTPUT:\n{exec_output}"
    )
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


def run(csv_path: str) -> None:
    """End-to-end: load CSV, generate + run analysis code, write a report."""
    import matplotlib

    matplotlib.use("Agg")  # headless: save figures, never open a window
    import matplotlib.pyplot as plt

    df = pd.read_csv(csv_path)
    CHART_DIR.mkdir(exist_ok=True)
    schema = schema_snapshot(df)

    print("Coder agent: generating analysis code...")
    code = coder_agent(schema)
    Path("generated_eda.py").write_text(code, encoding="utf-8")

    print("Executing generated code...")
    captured = io.StringIO()
    sandbox = {"df": df, "plt": plt, "pd": pd, "CHART_DIR": CHART_DIR}
    try:
        with redirect_stdout(captured):
            exec(code, sandbox)  # noqa: S102  generated code saved to generated_eda.py for review
        exec_output = captured.getvalue()
    except Exception as exc:  # noqa: BLE001  surface errors into the report, don't crash
        exec_output = captured.getvalue() + f"\n[execution error] {exc}"

    print("Analyst agent: writing report...")
    report = analyst_agent(schema, exec_output)
    Path("report.md").write_text(report, encoding="utf-8")

    charts = sorted(p.name for p in CHART_DIR.glob("*.png"))
    print(f"\nDone. Charts: {charts}\nReport: report.md  Code: generated_eda.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic EDA pipeline")
    parser.add_argument("csv", help="Path to a CSV file")
    run(parser.parse_args().csv)


if __name__ == "__main__":
    main()
