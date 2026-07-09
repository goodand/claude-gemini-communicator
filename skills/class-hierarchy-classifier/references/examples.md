# Examples

## Example 1: 포함관계 질문 + 검증

**User**: "DataFrame도 NDFrame이야?"

```python
from scripts.hierarchy_classifier import analyze_hierarchy

analyze_hierarchy(
    {
        "DataFrame": "pandas.DataFrame",
        "NDFrame": "pandas.core.generic.NDFrame"
    },
    check_relationship=("DataFrame", "NDFrame")
)
```

**Output shows**:
```
분기:
  [DataFrame] - Multiple Inheritance (2 parents)
    직계 부모 (__bases__): NDFrame, OpsMixin  ← 명확히 확인!

======================================================================
포함관계 검증 (issubclass)
======================================================================
✓ Yes, DataFrame IS a subclass of NDFrame

경로 (MRO):
  NDFrame → DataFrame
  (직계 부모)  ← DataFrame의 직계 부모임!
```

**Answer**: 네, DataFrame은 NDFrame을 직접 상속합니다!

---

## Example 2: 직계 부모 확인

**User**: "DataFrame의 직계 부모가 뭐야?"

```python
analyze_hierarchy({"DataFrame": "pandas.DataFrame"})
```

**Output shows**:
```
[DataFrame] - Multiple Inheritance (2 parents)
  직계 부모 (__bases__): NDFrame, OpsMixin  ← 여기!
```

**Answer**: NDFrame과 OpsMixin입니다 (다중 상속).

---

## Example 3: 구조 분류 (다중 상속 → DAG)

**User**: "DataFrame의 상속 구조가 Tree야 DAG야?"

```bash
python scripts/hierarchy_classifier.py pandas.DataFrame --classify-structure
```

**Output**:
```
======================================================================
구조 분류 (Structure Classification)
======================================================================

타입: DAG
이유: Multi-parent nodes (다중 상속): ['DataFrame']

다중 상속 노드: ['DataFrame']

💡 상세 분석이 필요하면 graph-structure-classifier 사용:
   python hierarchy_classifier.py ... --output-edges | \
       python $SKILLS_ROOT/graph-structure-classifier/scripts/classifier.py -
======================================================================
```

**Answer**: DAG입니다 (다중 상속으로 인해).

---

## Example 4: Edge 출력 (graph-structure-classifier 연동)

**User**: "상속 관계를 graph-structure-classifier로 분석하고 싶어"

```bash
# Step 1: Edge 추출
python scripts/hierarchy_classifier.py pandas.DataFrame --output-edges
```

**Output**:
```json
[
  ["object", "DirNamesMixin"],
  ["DirNamesMixin", "PandasObject"],
  ["PandasObject", "NDFrame"],
  ["object", "OpsMixin"],
  ["NDFrame", "DataFrame"],
  ["OpsMixin", "DataFrame"]
]
```

```bash
# Step 2: graph-structure-classifier로 파이프
python scripts/hierarchy_classifier.py pandas.DataFrame --output-edges | \
    python $SKILLS_ROOT/graph-structure-classifier/scripts/classifier.py -
```

**Output**:
```json
{
  "structure_type": "DAG",
  "reason": "Multi-parent nodes: ['DataFrame']",
  ...
}
```

---

## Example 5: 관계 없는 클래스 검증

**User**: "DataFrame과 Series는 서로 부모-자식 관계야?"

```python
analyze_hierarchy(
    {
        "DataFrame": "pandas.DataFrame",
        "Series": "pandas.Series"
    },
    check_relationship=("DataFrame", "Series")
)
```

**Output**:
```
✗ No, DataFrame is NOT a subclass of Series
  These classes are unrelated in the inheritance hierarchy.
```

**Answer**: 아니요, 둘은 형제 관계입니다 (같은 부모를 가진 별개 클래스).

---

## Example 6: 단순 상속 (Tree 구조)

**User**: "이 클래스는 Tree 구조야?"

```python
# 단일 상속 클래스 분석
analyze_hierarchy(
    {"MyClass": "mymodule.MyClass"},
    classify=True
)
```

**Output**:
```
[MyClass] - Single Inheritance:
  직계 부모 (__bases__): BaseClass

======================================================================
구조 분류 (Structure Classification)
======================================================================

타입: Tree
이유: Single root, single parent, acyclic
======================================================================
```

**Answer**: 네, Tree 구조입니다 (단일 상속).

---

## Example 7: CLI로 여러 클래스 한번에 분석

```bash
python scripts/hierarchy_classifier.py \
    pandas.DataFrame \
    pandas.Series \
    pandas.core.generic.NDFrame \
    --highlight NDFrame,OpsMixin \
    --classify-structure
```

Highlight로 특정 클래스 강조 + 구조 분류까지 한번에.
