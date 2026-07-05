#!/usr/bin/env python3
"""
클래스 계층 구조 분류 도구

공통 경로는 병합하고, 다중 상속 지점에서 분기합니다.
다중 상속 시 graph-structure-classifier와 연동하여 구조를 분류합니다.
"""

import inspect
import importlib
import sys
import json
import argparse
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Union
from collections import defaultdict


def get_skills_root() -> str:
    """
    Get skills root directory.
    Priority: SKILLS_ROOT env var > relative path from this script
    """
    # 1. Check environment variable
    if os.environ.get("SKILLS_ROOT"):
        return os.environ["SKILLS_ROOT"]
    
    # 2. Calculate relative path from this script
    # This script: .../class-hierarchy-classifier/scripts/hierarchy_classifier.py
    # Skills root: .../  (2 levels up from scripts/)
    script_dir = Path(__file__).resolve().parent
    skills_root = script_dir.parent.parent
    
    return str(skills_root)


def dynamic_import(spec: str) -> Any:
    """문자열 경로로부터 객체를 동적으로 import"""
    parts = spec.split('.')
    for i in range(len(parts), 0, -1):
        module_path = '.'.join(parts[:i])
        try:
            obj = importlib.import_module(module_path)
            for attr in parts[i:]:
                obj = getattr(obj, attr)
            return obj
        except (ImportError, AttributeError):
            continue
    raise ImportError(f"Cannot import '{spec}'")


def get_mro_names(obj: Any) -> List[str]:
    """MRO를 클래스 이름 리스트로 반환 (부모→자식)"""
    cls = obj if inspect.isclass(obj) else obj.__class__
    mro = list(cls.mro())
    mro.reverse()
    return [c.__name__ for c in mro]


def detect_multiple_inheritance(obj: Any) -> Tuple[bool, List[str]]:
    """다중 상속 감지"""
    cls = obj if inspect.isclass(obj) else obj.__class__
    bases = [b for b in cls.__bases__ if b is not object]
    return len(bases) > 1, [b.__name__ for b in bases]


def get_direct_parents(obj: Any) -> List[str]:
    """직계 부모 클래스 이름 반환 (__bases__)"""
    cls = obj if inspect.isclass(obj) else obj.__class__
    bases = [b.__name__ for b in cls.__bases__]
    return bases


def find_common_prefix(paths: List[List[str]]) -> List[str]:
    """여러 경로의 공통 prefix"""
    if not paths:
        return []
    common = []
    for i in range(min(len(p) for p in paths)):
        if all(i < len(p) and p[i] == paths[0][i] for p in paths):
            common.append(paths[0][i])
        else:
            break
    return common


def extract_inheritance_edges(components: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    컴포넌트들에서 상속 관계 edge 추출
    
    Returns:
        List of (parent, child) tuples
    """
    edges = []
    seen = set()
    
    for name, obj in components.items():
        cls = obj if inspect.isclass(obj) else obj.__class__
        mro = cls.mro()
        
        # MRO 순서대로 edge 생성 (자식 → 부모 순이므로 reverse)
        for i in range(len(mro) - 1):
            child = mro[i]
            parent = mro[i + 1]
            edge = (parent.__name__, child.__name__)
            
            if edge not in seen:
                edges.append(edge)
                seen.add(edge)
        
        # 직계 부모 관계도 명시적으로 추가 (다중 상속 처리)
        for base in cls.__bases__:
            edge = (base.__name__, cls.__name__)
            if edge not in seen:
                edges.append(edge)
                seen.add(edge)
    
    return edges


def classify_structure(edges: List[Tuple[str, str]]) -> Dict[str, Any]:
    """
    상속 그래프의 구조 분류 (Tree/DAG/DirectedGraph)
    
    graph-structure-classifier 로직을 내장하여 간단한 분류 수행
    """
    if not edges:
        return {"type": "Empty", "reason": "No edges"}
    
    # Build adjacency
    adj = defaultdict(list)
    reverse_adj = defaultdict(list)
    nodes = set()
    
    for parent, child in edges:
        nodes.add(parent)
        nodes.add(child)
        adj[parent].append(child)
        reverse_adj[child].append(parent)
    
    # Check for cycles (DFS)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    has_cycle = False
    cycle_nodes = []
    
    def dfs(node, path):
        nonlocal has_cycle, cycle_nodes
        color[node] = GRAY
        path.append(node)
        for neighbor in adj.get(node, []):
            if color[neighbor] == GRAY:
                idx = path.index(neighbor)
                cycle_nodes = path[idx:]
                has_cycle = True
                return True
            if color[neighbor] == WHITE and dfs(neighbor, path):
                return True
        color[node] = BLACK
        path.pop()
        return False
    
    for node in nodes:
        if color[node] == WHITE and dfs(node, []):
            break
    
    if has_cycle:
        return {
            "type": "DirectedGraph",
            "reason": f"Cycle detected: {cycle_nodes}",
            "has_cycle": True
        }
    
    # Check in-degree (multi-parent)
    in_degrees = {n: len(set(reverse_adj.get(n, []))) for n in nodes}
    max_in_degree = max(in_degrees.values()) if in_degrees else 0
    multi_parent_nodes = [n for n, d in in_degrees.items() if d > 1]
    
    if max_in_degree > 1:
        return {
            "type": "DAG",
            "reason": f"Multi-parent nodes (다중 상속): {multi_parent_nodes}",
            "has_cycle": False,
            "multi_parent_nodes": multi_parent_nodes
        }
    
    # Check connectivity (single root)
    roots = [n for n in nodes if n not in reverse_adj or not reverse_adj[n]]
    
    if len(roots) != 1:
        return {
            "type": "DAG",
            "reason": f"Multiple roots: {roots}",
            "has_cycle": False,
            "roots": roots
        }
    
    return {
        "type": "Tree",
        "reason": "Single root, single parent, acyclic",
        "has_cycle": False,
        "root": roots[0] if roots else None
    }


def print_merged_tree(components: Dict[str, Any], highlight: List[str] = None):
    """병합+분기 트리 출력"""
    if not components:
        return
    
    if highlight is None:
        highlight = []
    
    # MRO 수집
    mros = {name: get_mro_names(obj) for name, obj in components.items()}
    
    # 공통 prefix
    common = find_common_prefix(list(mros.values()))
    
    print("\n공통 경로:")
    for i, cls_name in enumerate(common):
        comps = [n for n, mro in mros.items() if i < len(mro) and mro[i] == cls_name]
        hl = " ★" if cls_name in highlight else ""
        comp_str = f"  [{', '.join(sorted(comps))}]" if comps else ""
        indent = "  " * i
        prefix = "── " if i == 0 else "└─ "
        print(f"{indent}{prefix}{cls_name}{hl}{comp_str}")
    
    # 공통 이후 분기
    print("\n분기:")
    for name, obj in components.items():
        mro = mros[name]
        remaining = mro[len(common):]
        
        if not remaining:
            continue
        
        is_multi, bases = detect_multiple_inheritance(obj)
        direct_parents = get_direct_parents(obj)
        
        if is_multi:
            print(f"\n  [{name}] - Multiple Inheritance ({len(bases)} parents)")
            if direct_parents:
                print(f"    직계 부모 (__bases__): {', '.join(direct_parents)}")
            print()
            for base in bases:
                print(f"    via {base}:")
                for j, cls_name in enumerate(remaining):
                    hl = " ★" if cls_name in highlight else ""
                    print(f"      {'  ' * j}└─ {cls_name}{hl}")
        else:
            print(f"\n  [{name}] - Single Inheritance:")
            if direct_parents:
                print(f"    직계 부모 (__bases__): {', '.join(direct_parents)}")
            for j, cls_name in enumerate(remaining):
                hl = " ★" if cls_name in highlight else ""
                print(f"    {'  ' * j}└─ {cls_name}{hl}")


def verify_relationship(components: Dict[str, Any], 
                       child_name: str, 
                       parent_name: str) -> None:
    """
    두 클래스 간의 상속 관계 검증 (issubclass)
    """
    print("\n" + "=" * 70)
    print("포함관계 검증 (issubclass)")
    print("=" * 70)
    
    if child_name not in components:
        print(f"✗ Error: '{child_name}' not found in components")
        return
    
    if parent_name not in components:
        print(f"✗ Error: '{parent_name}' not found in components")
        return
    
    child_obj = components[child_name]
    parent_obj = components[parent_name]
    
    child_cls = child_obj if inspect.isclass(child_obj) else child_obj.__class__
    parent_cls = parent_obj if inspect.isclass(parent_obj) else parent_obj.__class__
    
    try:
        is_subclass = issubclass(child_cls, parent_cls)
        
        if is_subclass:
            print(f"\n✓ Yes, {child_name} IS a subclass of {parent_name}")
            
            mro_names = [c.__name__ for c in child_cls.__mro__]
            parent_cls_name = parent_cls.__name__
            
            if parent_cls_name in mro_names:
                child_idx = mro_names.index(child_cls.__name__)
                parent_idx = mro_names.index(parent_cls_name)
                
                path_indices = list(range(parent_idx, child_idx - 1, -1))
                path = [mro_names[i] for i in path_indices]
                
                print(f"\n경로 (MRO):")
                print(f"  {' → '.join(path)}")
                
                distance = parent_idx - child_idx
                if distance == 1:
                    print(f"  (직계 부모)")
                else:
                    print(f"  ({distance}단계 조상)")
        else:
            print(f"\n✗ No, {child_name} is NOT a subclass of {parent_name}")
            print(f"  These classes are unrelated in the inheritance hierarchy.")
    
    except TypeError as e:
        print(f"✗ Error: {e}")
    
    print("=" * 70)


def analyze_hierarchy(component_specs: Dict[str, Union[str, Any]], 
                      highlight_keywords: List[str] = None,
                      check_relationship: Tuple[str, str] = None,
                      classify: bool = False,
                      output_edges: bool = False) -> Dict[str, Any]:
    """계층 구조 분석 및 분류
    
    Args:
        component_specs: {name: spec} 딕셔너리
        highlight_keywords: 강조할 클래스 이름들
        check_relationship: (child_name, parent_name) 튜플로 상속 관계 검증
        classify: True면 구조 분류 수행
        output_edges: True면 edges만 JSON 출력
    
    Returns:
        loaded components dict
    """
    components = {}
    
    if not output_edges:
        print("=" * 70)
        print("  클래스 계층 구조 분석")
        if highlight_keywords:
            print(f"  ★ 표시: {', '.join(highlight_keywords)}")
        print("=" * 70)
    
    for name, spec in component_specs.items():
        try:
            if isinstance(spec, str):
                obj = dynamic_import(spec)
                if not output_edges:
                    print(f"✓ Imported: {name} from {spec}")
            else:
                obj = spec
                if not output_edges:
                    print(f"✓ Loaded: {name}")
            components[name] = obj
        except Exception as e:
            if not output_edges:
                print(f"✗ Failed: {name} - {e}", file=sys.stderr)
    
    if not components:
        if not output_edges:
            print("\n⚠️  No components loaded.")
        return {}
    
    # Edge 출력 모드
    if output_edges:
        edges = extract_inheritance_edges(components)
        print(json.dumps([list(e) for e in edges], indent=2, ensure_ascii=False))
        return components
    
    print("=" * 70)
    print_merged_tree(components, highlight_keywords)
    print("=" * 70)
    
    # 포함관계 검증
    if check_relationship:
        child_name, parent_name = check_relationship
        verify_relationship(components, child_name, parent_name)
    
    # 구조 분류
    if classify:
        edges = extract_inheritance_edges(components)
        structure = classify_structure(edges)
        
        print("\n" + "=" * 70)
        print("구조 분류 (Structure Classification)")
        print("=" * 70)
        print(f"\n타입: {structure['type']}")
        print(f"이유: {structure['reason']}")
        
        if structure['type'] == 'DAG' and 'multi_parent_nodes' in structure:
            print(f"\n다중 상속 노드: {structure['multi_parent_nodes']}")
            print("\n💡 상세 분석이 필요하면 graph-structure-classifier 사용:")
            print("   python hierarchy_classifier.py ... --output-edges | \\")
            # Use relative path hint
            skills_root = get_skills_root()
            classifier_path = os.path.join(skills_root, "graph-structure-classifier/scripts/classifier.py")
            print(f"       python {classifier_path} -")
            print("   또는: python ../graph-structure-classifier/scripts/classifier.py -")
        
        print("=" * 70)
    
    return components


def main():
    parser = argparse.ArgumentParser(
        description="Class Hierarchy Classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic analysis
    python hierarchy_classifier.py pandas.DataFrame pandas.Series
    
    # With structure classification
    python hierarchy_classifier.py pandas.DataFrame --classify-structure
    
    # Output edges for graph-structure-classifier
    python hierarchy_classifier.py pandas.DataFrame --output-edges
    
    # Verify relationship
    python hierarchy_classifier.py pandas.DataFrame pandas.core.generic.NDFrame \\
        --check DataFrame NDFrame
        """
    )
    
    parser.add_argument(
        "specs",
        nargs="+",
        help="Module.Class paths to analyze"
    )
    
    parser.add_argument(
        "--highlight",
        type=str,
        help="Comma-separated keywords to highlight"
    )
    
    parser.add_argument(
        "--check",
        nargs=2,
        metavar=("CHILD", "PARENT"),
        help="Check if CHILD is subclass of PARENT"
    )
    
    parser.add_argument(
        "--classify-structure",
        action="store_true",
        help="Classify graph structure (Tree/DAG/DirectedGraph)"
    )
    
    parser.add_argument(
        "--output-edges",
        action="store_true",
        help="Output inheritance edges as JSON (for graph-structure-classifier)"
    )
    
    args = parser.parse_args()
    
    # Build specs
    specs = {s.split('.')[-1]: s for s in args.specs}
    
    # Parse options
    highlight = None
    if args.highlight:
        highlight = [h.strip() for h in args.highlight.split(",")]
    
    check_rel = None
    if args.check:
        check_rel = tuple(args.check)
    
    analyze_hierarchy(
        specs,
        highlight_keywords=highlight,
        check_relationship=check_rel,
        classify=args.classify_structure,
        output_edges=args.output_edges,
    )


if __name__ == "__main__":
    main()
