"""Output formatters for MCP tool responses: JSON, CSV, and Markdown."""

import csv
import io
import json
from typing import Any


def format_output(
    rows: list[dict[str, Any]],
    columns: list[str] | None = None,
    fmt: str = "json",
) -> str:
    """Format query results as JSON, CSV, or Markdown table.

    Args:
        rows: List of dictionaries (each dict is one row).
        columns: Column names to include (default: all keys from first row).
        fmt: Output format — "json", "csv", or "markdown".

    Returns:
        Formatted string.
    """
    if not rows:
        if fmt == "json":
            return json.dumps({"results": [], "count": 0}, indent=2)
        if fmt == "csv":
            return ""
        return "_No results._"

    if columns is None:
        columns = list(rows[0].keys())

    filtered = [{col: row.get(col) for col in columns} for row in rows]

    if fmt == "csv":
        return _to_csv(filtered, columns)
    if fmt == "markdown":
        return _to_markdown(filtered, columns)
    return _to_json(filtered)


def _to_json(rows: list[dict]) -> str:
    return json.dumps({"results": rows, "count": len(rows)}, indent=2, default=str)


def _to_csv(rows: list[dict], columns: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _to_markdown(rows: list[dict], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, separator]
    for row in rows:
        vals = [str(row.get(col, "")) for col in columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)
