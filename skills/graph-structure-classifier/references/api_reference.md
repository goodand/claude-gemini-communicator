# API Reference

## ClassificationResult

```python
@dataclass
class ClassificationResult:
    structure_type: StructureType  # TREE, DAG, MULTI_EDGE_DAG, DIRECTED_GRAPH, INVALID
    reason: str                    # Human-readable explanation
    step_failed: int | None        # 2=cycle, 3=degree, 4=connectivity, None=Tree
    
    # Stats
    node_count: int
    edge_count: int
    unique_edge_count: int
    has_cycle: bool
    max_in_degree: int
    
    # Details
    cycle_nodes: list[str]         # Nodes in detected cycle
    multi_parent_nodes: list[str]  # Nodes with in-degree > 1
    root_nodes: list[str]          # Nodes with in-degree = 0
    unreachable_nodes: list[str]   # Disconnected nodes
    duplicate_edges: list[tuple]   # Repeated edges
```

## GraphStructureClassifier

```python
class GraphStructureClassifier:
    def load_edges(self, edges: list) -> None
        """Load edges as tuples or dicts"""
    
    def classify(self) -> ClassificationResult
        """Run Waterfall algorithm"""
    
    def get_in_degrees(self) -> dict[str, int]
    def get_out_degrees(self) -> dict[str, int]
    
    # Attributes
    nodes: set[str]
    edges: list[tuple[str, str]]
    adj_list: dict[str, list[str]]
    reverse_adj: dict[str, list[str]]
```

## GraphMLFormatter

```python
class GraphMLFormatter:
    @staticmethod
    def format(classifier, result) -> str
        """JSON with layer/position encoding"""
    
    @staticmethod
    def format_for_llm_context(classifier, result) -> str
        """Concise Markdown summary"""
```

## Output Formats

| Format | Method | Use Case |
|--------|--------|----------|
| JSON | `result.to_dict()` | Full info |
| Mermaid | `format_mermaid()` | Documentation |
| GraphML | `GraphMLFormatter.format()` | LLM context |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Tree, DAG, MultiEdgeDAG (acyclic) |
| 1 | DirectedGraph (cyclic) |
| 2 | Invalid |
