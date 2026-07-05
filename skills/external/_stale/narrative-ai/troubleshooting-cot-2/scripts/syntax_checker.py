#!/usr/bin/env python3
"""
Syntax Checker - Phase 3-0

문법 오류를 자동으로 검증합니다 (Working Tree 변경 없음).
git show로 커밋 내 파일을 추출하여 임시 파일에서 검증합니다.

Usage:
    python syntax_checker.py --commits abc123,def456
    python syntax_checker.py --commits high_priority.txt --lang python,javascript
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def check_python_syntax(file_path):
    """Python 문법 검증 (표준 라이브러리만 사용)"""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        try:
            compile(source_code, str(file_path), 'exec')
        except SyntaxError as e:
            errors.append({
                'tool': 'python-compile',
                'line': e.lineno,
                'error': f"Line {e.lineno}: {e.msg}"
            })

        # pylint (선택적 보너스)
        try:
            result = subprocess.run(
                ['pylint', '--errors-only', str(file_path)],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0 and result.stdout:
                errors.append({
                    'tool': 'pylint',
                    'error': result.stdout
                })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    except Exception as e:
        errors.append({'tool': 'file-read', 'error': str(e)})

    return errors


def check_javascript_syntax(file_path):
    """JavaScript 문법 검증"""
    errors = []

    # node --check (Node.js 내장)
    try:
        result = subprocess.run(
            ['node', '--check', str(file_path)],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            errors.append({
                'tool': 'node-check',
                'error': result.stderr
            })
    except FileNotFoundError:
        # Node.js 없으면 정규식 휴리스틱
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            patterns = [
                (r'{\s*[^}]*$', 'Unclosed brace'),
                (r'\([^)]*$', 'Unclosed parenthesis'),
                (r'\[[^\]]*$', 'Unclosed bracket'),
            ]

            for pattern, msg in patterns:
                if re.search(pattern, content, re.MULTILINE):
                    errors.append({
                        'tool': 'regex-heuristic',
                        'error': f'Possible: {msg}'
                    })
                    break
        except Exception:
            pass
    except subprocess.TimeoutExpired:
        pass

    # eslint (선택적 보너스)
    try:
        result = subprocess.run(
            ['eslint', str(file_path)],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0 and result.stdout:
            errors.append({
                'tool': 'eslint',
                'error': result.stdout
            })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return errors


def get_file_language(file_path):
    """파일 확장자로 언어 판단"""
    suffix = Path(file_path).suffix.lower()
    return {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'javascript',
        '.tsx': 'javascript',
    }.get(suffix)


def check_commit_syntax(commit_hash, languages=None):
    """커밋의 변경 파일 문법 검증 (Working Tree 변경 없음)

    git show로 파일 내용을 추출하여 임시 파일에서 검증.
    git checkout을 사용하지 않으므로 Working Tree가 안전합니다.
    """

    # 변경된 파일 목록
    try:
        result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
            capture_output=True, text=True, check=True
        )
        changed_files = [f for f in result.stdout.strip().split('\n') if f]
    except subprocess.CalledProcessError:
        print(f"Error: Could not get files for {commit_hash}", file=sys.stderr)
        return []

    errors = []

    for file_path_str in changed_files:
        lang = get_file_language(file_path_str)

        if lang is None:
            continue
        if languages and lang not in languages:
            continue

        # git show로 파일 내용 추출 (checkout 불필요!)
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{file_path_str}'],
                capture_output=True, text=True, check=True
            )
            content = result.stdout
        except subprocess.CalledProcessError:
            continue  # 삭제된 파일

        # 임시 파일에 쓰고 검증
        suffix = Path(file_path_str).suffix
        with tempfile.NamedTemporaryFile(
            mode='w', suffix=suffix, delete=False, encoding='utf-8'
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            if lang == 'python':
                file_errors = check_python_syntax(tmp_path)
            elif lang == 'javascript':
                file_errors = check_javascript_syntax(tmp_path)
            else:
                continue

            for err in file_errors:
                err['file'] = file_path_str
                err['commit'] = commit_hash

            errors.extend(file_errors)
        finally:
            os.unlink(tmp_path)

    return errors


def main():
    parser = argparse.ArgumentParser(description='Check syntax errors in commits')
    parser.add_argument('--commits', required=True,
                       help='Comma-separated commit hashes or file path')
    parser.add_argument('--lang', default='python,javascript',
                       help='Comma-separated languages to check')

    args = parser.parse_args()

    # Parse commits
    if Path(args.commits).exists():
        with open(args.commits) as f:
            commit_hashes = [line.strip() for line in f if line.strip()]
    else:
        commit_hashes = args.commits.split(',')

    languages = set(args.lang.split(','))

    print(f"Checking syntax for {len(commit_hashes)} commits")
    print(f"Languages: {', '.join(languages)}")
    print()

    all_errors = []

    for commit in commit_hashes:
        print(f"  {commit}...", end=' ')
        errors = check_commit_syntax(commit, languages)

        if errors:
            print(f"FAIL ({len(errors)} errors)")
            all_errors.extend(errors)
        else:
            print("OK")

    print()

    if all_errors:
        print(f"Total: {len(all_errors)} syntax error(s)\n")
        for error in all_errors:
            print(f"  Commit: {error.get('commit', '?')}")
            print(f"  File:   {error.get('file', '?')}")
            print(f"  Tool:   {error['tool']}")
            print(f"  Error:  {error['error']}")
            print()
        return 1
    else:
        print("No syntax errors found")
        print("Proceed to Phase 3-1 (Git Bisect)")
        return 0


if __name__ == '__main__':
    sys.exit(main())
