#!/usr/bin/env python3
"""
Semantic Diff - Phase 2 (EXT-3)

텍스트 diff가 아닌 AST(추상 구문 트리) 비교를 통해
'구조적 변경(함수 삭제, 로직 변경)'만 추출합니다.

Fixes based on CTO feedback:
- REMOVED: Unnecessary AttributeCleaner class (ast.dump excludes attributes by default)
- FIXED: noise_ratio calculation (denominator = len(nodes_good))
- FIXED: Exit code 1 on SyntaxError
- REMOVED: Unused import os
"""

import argparse
import ast
import subprocess
import sys
import json
from typing import Dict, Any, Optional

class ScopeTrackingVisitor(ast.NodeVisitor):
    """
    AST를 순회하며 클래스/함수의 계층적 이름(Qualified Name)을 수집합니다.
    예: ClassA.methodB.nestedC
    """
    def __init__(self):
        self.nodes = {}
        self.stack = []

    def _visit_scope(self, node):
        # 현재 스코프 + 노드 이름으로 Qualified Name 생성
        qname = ".".join(self.stack + [node.name])

        # full dump: 이름 포함 (같은 이름 비교용)
        full_dump = ast.dump(node)

        # content dump: 이름 제외 (리네이밍 감지용)
        # 이름을 임시 치환 후 dump, 복원
        original_name = node.name
        node.name = "_"
        content_dump = ast.dump(node)
        node.name = original_name

        self.nodes[qname] = (full_dump, content_dump)

        # 스택에 추가하고 자식 노드 방문
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_ClassDef(self, node):
        self._visit_scope(node)

    def visit_FunctionDef(self, node):
        self._visit_scope(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_scope(node)

def git_show(revision: str, filepath: str) -> Optional[str]:
    """Git에서 특정 리비전의 파일 내용을 가져옴"""
    try:
        cmd = ["git", "show", f"{revision}:{filepath}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None # 파일 없음
        return result.stdout
    except Exception:
        return None

def get_ast_nodes(source: str) -> Dict[str, str]:
    """소스코드에서 함수/클래스 정의와 그 구조(Dump)를 추출"""
    if not source.strip():
        return {}
    
    try:
        tree = ast.parse(source)
    except SyntaxError:
        raise ValueError("SyntaxError: Unable to parse source code")
        
    # 계층적 이름으로 노드 추출 (Name Collision 방지)
    visitor = ScopeTrackingVisitor()
    visitor.visit(tree)
            
    return visitor.nodes

def analyze_diff(src_good: str, src_bad: str):
    """두 소스 코드의 AST 구조 비교"""
    try:
        nodes_good = get_ast_nodes(src_good)
    except ValueError:
        return {"error": "SyntaxError in GOOD commit file"}
        
    try:
        nodes_bad = get_ast_nodes(src_bad)
    except ValueError:
        return {"error": "SyntaxError in BAD commit file"}

    all_keys = set(nodes_good.keys()) | set(nodes_bad.keys())
    
    # Fix: 분모는 Good Commit 기준 (원래 있던 함수 개수)
    total_before = len(nodes_good)
    
    added_names = set()
    removed_names = set()
    modified = []
    unchanged_count = 0

    # 1차 분류: 이름 기준 (full_dump = tuple[0])
    for name in all_keys:
        in_good = name in nodes_good
        in_bad = name in nodes_bad

        if in_good and not in_bad:
            removed_names.add(name)
        elif not in_good and in_bad:
            added_names.add(name)
        elif nodes_good[name][0] != nodes_bad[name][0]:
            modified.append(name)
        else:
            unchanged_count += 1

    # 2차 분류: 내용(Content) 기준 매칭 — 리네이밍 감지
    # content_dump(tuple[1])가 동일한 쌍 = 이름만 바뀐 것
    renamed = []
    for r_name in list(removed_names):
        r_content = nodes_good[r_name][1]
        for a_name in list(added_names):
            if r_content == nodes_bad[a_name][1]:
                renamed.append([r_name, a_name])
                removed_names.discard(r_name)
                added_names.discard(a_name)
                break

    noise_ratio = unchanged_count / max(total_before, 1)

    return {
        "renamed": sorted(renamed),
        "added": sorted(added_names),
        "removed": sorted(removed_names),
        "modified": sorted(modified),
        "unchanged_count": unchanged_count,
        "total_functions": len(all_keys),
        "noise_ratio": round(noise_ratio, 2)
    }

def print_human_readable(result: Dict[str, Any], good_rev: str, bad_rev: str, filepath: str):
    print(f"============================================================")
    print(f"  Semantic Diff: {good_rev} -> {bad_rev}")
    print(f"  File: {filepath}")
    print(f"============================================================")
    
    if "error" in result:
        print(f"\n  ❌ Analysis Failed: {result['error']}")
        return

    print(f"\n  Functions Analysis (Total: {result['total_functions']}):")
    print(f"  - Unchanged: {result['unchanged_count']} (Noise Ratio: {result['noise_ratio']})")

    if result.get('renamed'):
        print(f"\n  [->] RENAMED ({len(result['renamed'])}) - Name only, logic identical:")
        for old, new in result['renamed']:
            print(f"       {old} -> {new}")

    if result['added']:
        print(f"\n  [+] ADDED ({len(result['added'])}):")
        for name in result['added']:
            print(f"      + {name}")

    if result['removed']:
        print(f"\n  [-] REMOVED ({len(result['removed'])}) - Check for accidental deletion!:")
        for name in result['removed']:
            print(f"      - {name}")

    if result['modified']:
        print(f"\n  [*] MODIFIED ({len(result['modified'])}) - Logic Changed:")
        for name in result['modified']:
            print(f"      * {name}")

    has_changes = (result.get('renamed') or result['added']
                   or result['removed'] or result['modified'])
    if not has_changes:
        print("\n  No structural changes detected.")
        if result['total_functions'] > 0:
            print("     (Changes might be comments, formatting, or top-level variables)")

def main():
    parser = argparse.ArgumentParser(description='AST-based Semantic Diff')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--commit', help='Analyze a single commit (compare with parent)')
    group.add_argument('--good', help='Good commit hash (start of range)')
    
    parser.add_argument('--bad', help='Bad commit hash (end of range, required if --good used)')
    parser.add_argument('--file', required=True, help='Target file path (Python only)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()

    # 파일 확장자 검사
    if not args.file.endswith('.py'):
        error_msg = f"Error: '{args.file}' is not a Python file. Semantic diff currently supports only .py files."
        if args.json:
            print(json.dumps({"error": error_msg}))
        else:
            print(error_msg)
        sys.exit(1)

    # 리비전 설정
    if args.commit:
        good_rev = f"{args.commit}~1"
        bad_rev = args.commit
    else:
        if not args.bad:
            parser.error("--bad is required when --good is used")
        good_rev = args.good
        bad_rev = args.bad

    # 소스 추출
    src_good = git_show(good_rev, args.file)
    src_bad = git_show(bad_rev, args.file)

    if src_good is None and src_bad is None:
        msg = f"File '{args.file}' not found in both revisions"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    # 한쪽만 있는 경우 (파일 생성/삭제) 처리
    if src_good is None: src_good = ""
    if src_bad is None: src_bad = ""

    # 분석
    result = analyze_diff(src_good, src_bad)
    result['file'] = args.file
    result['revisions'] = {'good': good_rev, 'bad': bad_rev}

    # 출력
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_readable(result, good_rev, bad_rev, args.file)

    # Fix: Exit code handling
    if "error" in result:
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
