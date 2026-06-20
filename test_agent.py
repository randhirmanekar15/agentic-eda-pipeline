"""Tests for pure helpers (no Ollama model required)."""

import pandas as pd

from agent import schema_snapshot, strip_fences


def test_strip_fences():
    assert strip_fences("```python\nx = 1\n```") == "x = 1"


def test_schema_snapshot_mentions_columns():
    df = pd.DataFrame({"age": [20, 30], "city": ["a", "b"]})
    snap = schema_snapshot(df)
    assert "age" in snap
    assert "city" in snap
    assert "HEAD" in snap
