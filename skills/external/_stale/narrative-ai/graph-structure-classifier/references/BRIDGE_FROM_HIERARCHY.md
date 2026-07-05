# Bridge: class-hierarchy-classifier → graph-structure-classifier

`class-hierarchy-classifier`에서 추출한 상속 관계 edge를 `graph-structure-classifier`로 분석합니다.

## Quick Start

```bash
# class-hierarchy-classifier에서 edge 추출 후 분류
python $SKILLS_ROOT/class-hierarchy-classifier/scripts/hierarchy_classifier.py \
    pandas.DataFrame --output-edges | python scripts/classifier.py -

# Mermaid 출력
python $SKILLS_ROOT/class-hierarchy-classifier/scripts/hierarchy_classifier.py \
    pandas.DataFrame --output-edges | python scripts/classifier.py - --format mermaid

# GraphML 출력 (LLM context)
python $SKILLS_ROOT/class-hierarchy-classifier/scripts/hierarchy_classifier.py \
    pandas.DataFrame --output-edges | python scripts/classifier.py - --format graphml
```

## Input Format

`class-hierarchy-classifier --output-edges`의 출력:

```json
[
  ["object", "ABC"],
  ["ABC", "NDFrame"],
  ["NDFrame", "DataFrame"],
  ["OpsMixin", "DataFrame"]
]
```

이 형식은 `graph-structure-classifier`의 edge list 입력과 호환됩니다.

## Python API

```python
import sys
sys.path.insert(0, '$SKILLS_ROOT/class-hierarchy-classifier/scripts')
sys.path.insert(0, '$SKILLS_ROOT/graph-structure-classifier/scripts')

from hierarchy_classifier import analyze_hierarchy, extract_inheritance_edges
from classifier import classify_graph, GraphStructureClassifier
from graphml_formatter import GraphMLFormatter

# Step 1: class-hierarchy-classifier에서 edge 추출
specs = {"DataFrame": "pandas.DataFrame"}
components = analyze_hierarchy(specs, output_edges=False)
edges = extract_inheritance_edges(components)

# Step 2: graph-structure-classifier로 분류
result = classify_graph(edges)
print(f"Structure: {result.structure_type.value}")
print(f"Reason: {result.reason}")

# Step 3: 상세 출력 (GraphML)
classifier = GraphStructureClassifier()
classifier.load_edges(edges)
result = classifier.classify()
graphml = GraphMLFormatter.format(classifier, result)
print(graphml)
```

## Use Cases

### 1. 다중 상속 감지

```bash
# DataFrame이 다중 상속인지 확인
python hierarchy_classifier.py pandas.DataFrame --output-edges | \
    python classifier.py -
```

출력:
```json
{
  "structure_type": "DAG",
  "reason": "Multi-parent nodes: ['DataFrame']"
}
```

### 2. 시각화

```bash
# Mermaid 다이어그램 생성
python hierarchy_classifier.py pandas.DataFrame pandas.Series --output-edges | \
    python classifier.py - --format mermaid > hierarchy.mermaid
```

### 3. LLM Context 생성

```bash
# GraphML 형식으로 LLM context 생성
python hierarchy_classifier.py pandas.DataFrame --output-edges | \
    python classifier.py - --format graphml > hierarchy.graphml
```

## Structure Interpretation for Class Hierarchies

| Structure | 의미 | Python 상속 |
|-----------|------|-------------|
| Tree | 모든 클래스가 단일 부모 | 순수 단일 상속 |
| DAG | 일부 클래스가 다중 부모 | 다중 상속 존재 |
| DirectedGraph | 순환 존재 | Python에서 불가능 (오류) |

## Notes

- Python 클래스 상속에서 DirectedGraph(순환)는 발생하지 않음
- 대부분 Tree 또는 DAG
- DAG인 경우 `multi_parent_nodes`에서 다중 상속 클래스 확인 가능
