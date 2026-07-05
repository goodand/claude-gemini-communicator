#!/usr/bin/env python3
"""
Pattern Archiver - Phase 4

해결된 이슈를 PATTERN_LIBRARY.md에 패턴으로 저장합니다.

Usage:
    python pattern_archiver.py --good abc123 --bad def456 --category authentication
    python pattern_archiver.py --interactive
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_commit_info(commit_hash):
    """커밋 정보 가져오기"""
    try:
        result = subprocess.run(
            ['git', 'show', '--stat', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def get_commit_diff(commit_hash):
    """커밋 diff 가져오기"""
    try:
        result = subprocess.run(
            ['git', 'show', commit_hash, '-p'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def interactive_mode():
    """대화형 모드로 패턴 입력받기"""
    print("=== 패턴 아카이버 (대화형 모드) ===\n")
    
    pattern = {}
    
    # Pattern ID
    pattern_id = input("Pattern ID (예: SESSION_SAVE_MISSING_001): ").strip()
    if not pattern_id:
        print("Error: Pattern ID는 필수입니다")
        return None
    pattern['pattern_id'] = pattern_id
    
    # Category
    print("\n카테고리 선택:")
    print("  1. authentication")
    print("  2. database")
    print("  3. async")
    print("  4. ui")
    print("  5. defensive-programming")
    print("  6. datetime")
    print("  7. other")
    
    category_choice = input("선택 (1-7): ").strip()
    categories = {
        '1': 'authentication',
        '2': 'database',
        '3': 'async',
        '4': 'ui',
        '5': 'defensive-programming',
        '6': 'datetime',
        '7': 'other'
    }
    pattern['category'] = categories.get(category_choice, 'other')
    
    # Good commit
    good_commit = input("\nGood Case 커밋 해시: ").strip()
    if not good_commit:
        print("Error: Good commit은 필수입니다")
        return None
    pattern['good_commit'] = good_commit
    
    # Mechanism
    print("\n핵심 메커니즘 (수도코드, 여러 줄 입력 시 빈 줄로 종료):")
    mechanism_lines = []
    while True:
        line = input()
        if not line:
            break
        mechanism_lines.append(line)
    pattern['mechanism'] = '\n'.join(mechanism_lines)
    
    # Constraints
    print("\n제약 조건 (예: CONSTRAINT-001, 여러 개 입력 시 쉼표 구분):")
    constraints_input = input().strip()
    pattern['constraints'] = [c.strip() for c in constraints_input.split(',') if c.strip()]
    
    # Bad commit
    bad_commit = input("\nBad Case 커밋 해시: ").strip()
    if not bad_commit:
        print("Error: Bad commit은 필수입니다")
        return None
    pattern['bad_commit'] = bad_commit
    
    # Violation
    violation = input("위반 내용 (한 줄): ").strip()
    pattern['violation'] = violation
    
    # Symptom
    symptom = input("증상 (한 줄): ").strip()
    pattern['symptom'] = symptom
    
    # Root cause
    root_cause = input("근본 원인 (한 줄): ").strip()
    pattern['root_cause'] = root_cause
    
    # Auto check
    auto_check = input("자동 검증 방법 (선택, 예: ESLint 규칙): ").strip()
    if auto_check:
        pattern['auto_check'] = auto_check
    
    return pattern


def append_to_library(pattern, library_path):
    """PATTERN_LIBRARY.md에 패턴 추가"""
    
    # Generate markdown section
    md_lines = []
    md_lines.append(f"\n---\n")
    md_lines.append(f"\n### PATTERN-{pattern['pattern_id'].replace('_', '-')}\n")
    md_lines.append(f"\n**카테고리:** {pattern['category']}\n")
    
    # Good Case
    md_lines.append(f"\n**Good Case (커밋 {pattern['good_commit']}):**\n")
    md_lines.append("```\n")
    md_lines.append(pattern['mechanism'])
    md_lines.append("\n```\n")
    
    # Constraints
    if pattern.get('constraints'):
        md_lines.append("\n**제약 조건:**\n")
        for constraint in pattern['constraints']:
            md_lines.append(f"- {constraint}\n")
    
    # Bad Case
    md_lines.append(f"\n**Bad Case (커밋 {pattern['bad_commit']}):**\n")
    md_lines.append(f"- 위반: {pattern['violation']}\n")
    
    # Symptom
    md_lines.append(f"\n**증상:**\n")
    md_lines.append(f"- {pattern['symptom']}\n")
    
    # Root cause
    if pattern.get('root_cause'):
        md_lines.append(f"\n**근본 원인:**\n")
        md_lines.append(f"- {pattern['root_cause']}\n")
    
    # Auto check
    if pattern.get('auto_check'):
        md_lines.append(f"\n**자동 검증:**\n")
        md_lines.append(f"- {pattern['auto_check']}\n")
    
    # Timestamp
    md_lines.append(f"\n*추가 일시: {datetime.now().isoformat()}*\n")
    
    # Append to file
    markdown = ''.join(md_lines)
    
    with open(library_path, 'a') as f:
        f.write(markdown)
    
    return markdown


def main():
    parser = argparse.ArgumentParser(description='Archive troubleshooting patterns')
    parser.add_argument('--good', help='Good commit hash')
    parser.add_argument('--bad', help='Bad commit hash')
    parser.add_argument('--category', help='Pattern category')
    parser.add_argument('--pattern-id', help='Pattern ID')
    parser.add_argument('--interactive', action='store_true', 
                       help='Interactive mode')
    parser.add_argument('--library', default='references/PATTERN_LIBRARY.md',
                       help='Pattern library file path')
    
    args = parser.parse_args()
    
    # Determine skill directory
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    library_path = skill_dir / args.library
    
    if not library_path.exists():
        print(f"Warning: {library_path} not found", file=sys.stderr)
        create = input("Create new PATTERN_LIBRARY.md? (y/n): ").strip().lower()
        if create != 'y':
            return 1
        library_path.parent.mkdir(parents=True, exist_ok=True)
        library_path.write_text("# Good/Bad Case 패턴 라이브러리\n\n")
    
    # Get pattern data
    if args.interactive:
        pattern = interactive_mode()
        if not pattern:
            return 1
    else:
        if not all([args.good, args.bad, args.category]):
            print("Error: --good, --bad, --category required (or use --interactive)",
                  file=sys.stderr)
            return 1
        
        pattern = {
            'pattern_id': args.pattern_id or f"{args.category.upper()}_001",
            'category': args.category,
            'good_commit': args.good,
            'bad_commit': args.bad,
            'mechanism': f"[Good Case mechanism for {args.good}]",
            'violation': f"[Violation in {args.bad}]",
            'symptom': "[Symptom description]",
            'root_cause': "[Root cause]"
        }
    
    # Append to library
    print(f"\n📚 Adding pattern to {library_path}")
    markdown = append_to_library(pattern, library_path)
    
    print("\n✅ Pattern archived successfully!")
    print()
    print("Preview:")
    print(markdown)
    
    print()
    print("Next steps:")
    print(f"  1. Review {library_path}")
    print("  2. Add auto-check implementation if applicable")
    print("  3. Share with team")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
