#!/usr/bin/env python3
import json
import sys
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Skill Review</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; line-height: 1.5; }}
    h1, h2 {{ margin-top: 1.2em; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 16px 0; }}
    .ok {{ color: green; }}
    .bad {{ color: #b00020; }}
    pre {{ white-space: pre-wrap; background: #f7f7f7; padding: 12px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>Skill Review</h1>
  <div class="card">
    <h2>Benchmark Summary</h2>
    <pre>{benchmark_json}</pre>
  </div>
</body>
</html>
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: generate_static_review.py <benchmark.json>")
        sys.exit(1)

    benchmark_path = Path(sys.argv[1])
    if not benchmark_path.exists():
        print(f"Not found: {benchmark_path}")
        sys.exit(1)

    data = json.loads(benchmark_path.read_text(encoding="utf-8"))
    html = HTML_TEMPLATE.format(benchmark_json=json.dumps(data, indent=2, ensure_ascii=False))

    out_path = benchmark_path.with_suffix(".html")
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()