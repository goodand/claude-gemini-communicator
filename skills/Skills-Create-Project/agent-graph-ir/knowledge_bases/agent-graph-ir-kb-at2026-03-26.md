# agent-graph-ir knowledge base

## Canonical design takeaways

1. Source of truth is typed JSON IR, not DOT or Mermaid.
2. Static spec and dynamic run trace share the same ID system.
3. Condition expressions are stored as AST, not opaque strings.
4. Langfuse integration starts as JSON-compatible trace shape first, SDK second.
5. First vertical slice should validate structure and emit derived artifacts before parser import expansion.
