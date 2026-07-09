# Render FastMCP Healthcheck

Backlink: [Troubleshooting-CoT](../../SKILL.md)

Use this playbook when a hosted FastMCP service builds and starts but Render marks the deploy unhealthy because `/health` does not return a successful response.

## Problem Definition

Typical symptom:

- Build succeeds.
- Start command runs.
- Uvicorn reports a listening port.
- Render health check times out.
- Logs repeatedly show `GET /health HTTP/1.1` with `421 Misdirected Request`.

Working definition:

- Do not collapse this into "server failed to start."
- Treat "process did not bind", "route does not exist", and "route exists but a guard rejects the request" as separate failures.
- `421 Misdirected Request` usually means FastMCP host/origin protection rejected the request before the custom route handler ran.

## Repeated Issue Pattern

- First attempts often focus on `PORT`, `startCommand`, direct `uvicorn`, or route precedence.
- `mcp.custom_route("/health")` can still sit behind FastMCP HTTP middleware.
- Local and hosted FastMCP versions may differ; inspect the exact version and public API before patching.
- A previous successful deploy is the best Good Case. Compare its `render.yaml`, server entrypoint, and dependency pins against the Bad Case.

## Evidence Checklist

Collect these before patching:

- `git log -5 --stat`
- `git diff <good>..<bad> -- render.yaml files/server.py files/requirements.txt files/pyproject.toml`
- Render start line, for example `Running 'python server.py'`
- FastMCP startup line showing transport path and port
- Health check log lines with exact status code
- Local FastMCP version
- `FastMCP.run_http_async` or `FastMCP.http_app` signature for the installed version

## Diagnosis Commands

```bash
git show --stat --oneline HEAD
git diff <good>..<bad> -- render.yaml files/server.py files/requirements.txt files/pyproject.toml
python -c "import inspect, fastmcp; from fastmcp import FastMCP; print(fastmcp.__version__); print(inspect.signature(FastMCP.run_http_async))"
```

If the service can run locally:

```bash
MCP_TRANSPORT=http PORT=8765 python files/server.py
curl -i -H 'Host: concept-gate-taxonomy.onrender.com' http://127.0.0.1:8765/health
curl -i -H 'Host: attacker.example' http://127.0.0.1:8765/health
```

Expected fixed behavior:

- Allowed hosted domain returns `200 OK`.
- Unknown host still returns `421 Misdirected Request`.

## Core Solution

For FastMCP versions that expose host/origin guard controls at HTTP run time, configure them explicitly:

```python
mcp.run(
    transport="http",
    host="0.0.0.0",
    port=port,
    host_origin_protection=True,
    allowed_hosts=[
        "127.0.0.1",
        "localhost",
        "::1",
        "0.0.0.0",
        "*.onrender.com",
        "concept-gate-taxonomy.onrender.com",
    ],
    allowed_origins=[
        "https://chatgpt.com",
        "https://chat.openai.com",
        "https://platform.openai.com",
    ],
)
```

Pin the dependency when local and hosted environments disagree:

```text
fastmcp==3.4.3
```

If the installed FastMCP version does not expose these arguments, do not guess. Inspect `FastMCP.run_http_async`, `FastMCP.http_app`, and the transport middleware implementation, then adapt the smallest equivalent host/origin guard configuration for that version.

## Validation Gate

Do not mark the issue fixed until all checks pass:

- Server file compiles with `python -m py_compile`.
- Project server tests pass.
- Local `/health` with the hosted domain as `Host` returns `200`.
- Local `/health` with an unknown `Host` still returns `421`.
- Render deploy becomes live.

## Failure Boundaries

- `connection refused`: inspect port binding and start command.
- `404`: inspect route path and app mounting.
- `421`: inspect host guard configuration.
- `403`: inspect origin guard configuration.
- No startup line: inspect dependency install and process boot.

## Pattern Library Note

After resolving a case, archive it in [Pattern Library](../PATTERN_LIBRARY.md) as a deploy/configuration regression with the Good Case commit, Bad Case commit, host/origin guard delta, dependency version delta, and exact curl evidence.
