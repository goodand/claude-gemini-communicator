#!/usr/bin/env python3
"""
Pattern Detector - Phase 5

악순환 패턴을 탐지합니다:
- 시간 패턴 (fix → revert 간격)
- 파일 Hot Spot (반복 수정되는 파일)
- 개발자 패턴 (특정 모듈에서 버그 밀도)

Usage:
    python pattern_detector.py --mode time --days 90
    python pattern_detector.py --mode file --days 90
    python pattern_detector.py --mode all --days 90
"""

import argparse
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def detect_time_patterns(days):
    """시간 패턴: fix → revert 간격 분석"""
    
    # Get fix commits
    result = subprocess.run(
        ['git', 'log', f'--since={days} days ago', '--grep=fix', 
         '--pretty=format:%H|%ad|%s', '--date=unix'],
        capture_output=True,
        text=True
    )
    
    fix_commits = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        hash_, date, msg = line.split('|', 2)
        fix_commits.append({
            'hash': hash_,
            'date': int(date),
            'message': msg
        })
    
    # Get revert commits
    result = subprocess.run(
        ['git', 'log', f'--since={days} days ago', '--grep=revert', 
         '--pretty=format:%H|%ad|%s', '--date=unix'],
        capture_output=True,
        text=True
    )
    
    revert_commits = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        hash_, date, msg = line.split('|', 2)
        revert_commits.append({
            'hash': hash_,
            'date': int(date),
            'message': msg
        })
    
    # Find quick reverts (< 1 day)
    quick_reverts = []
    
    for fix in fix_commits:
        for revert in revert_commits:
            if revert['date'] > fix['date']:
                gap_hours = (revert['date'] - fix['date']) / 3600
                if gap_hours < 24:
                    quick_reverts.append({
                        'fix': fix,
                        'revert': revert,
                        'gap_hours': gap_hours
                    })
    
    return {
        'total_fixes': len(fix_commits),
        'total_reverts': len(revert_commits),
        'quick_reverts': quick_reverts
    }


def detect_file_hotspots(days):
    """파일 Hot Spot: 자주 수정되는 파일"""
    
    result = subprocess.run(
        ['git', 'log', f'--since={days} days ago', '--name-only', 
         '--pretty=format:'],
        capture_output=True,
        text=True
    )
    
    file_changes = Counter()
    
    for line in result.stdout.strip().split('\n'):
        if line:
            file_changes[line] += 1
    
    # Top 10 most changed files
    hotspots = file_changes.most_common(10)
    
    # Get bug-related changes
    result = subprocess.run(
        ['git', 'log', f'--since={days} days ago', '--grep=fix\\|bug', 
         '--name-only', '--pretty=format:'],
        capture_output=True,
        text=True
    )
    
    bug_changes = Counter()
    for line in result.stdout.strip().split('\n'):
        if line:
            bug_changes[line] += 1
    
    return {
        'hotspots': hotspots,
        'bug_hotspots': bug_changes.most_common(10)
    }


def detect_developer_patterns(days):
    """개발자 패턴: 모듈별 버그 밀도"""
    
    # Get all commits by author
    result = subprocess.run(
        ['git', 'log', f'--since={days} days ago', 
         '--pretty=format:%an|%s|%H'],
        capture_output=True,
        text=True
    )
    
    author_stats = defaultdict(lambda: {'total': 0, 'fixes': 0})
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        
        author, msg, hash_ = line.split('|', 2)
        author_stats[author]['total'] += 1
        
        if 'fix' in msg.lower() or 'bug' in msg.lower():
            author_stats[author]['fixes'] += 1
    
    # Calculate fix ratio
    patterns = []
    for author, stats in author_stats.items():
        if stats['total'] > 5:  # Minimum 5 commits
            fix_ratio = stats['fixes'] / stats['total']
            patterns.append({
                'author': author,
                'total_commits': stats['total'],
                'fix_commits': stats['fixes'],
                'fix_ratio': fix_ratio
            })
    
    # Sort by fix ratio
    patterns.sort(key=lambda x: x['fix_ratio'], reverse=True)
    
    return patterns


def generate_report(time_patterns, file_patterns, dev_patterns):
    """분석 보고서 생성"""
    
    report = []
    report.append("# 악순환 패턴 분석 보고서\n")
    report.append(f"생성일: {datetime.now().isoformat()}\n")
    report.append("\n")
    
    # Time patterns
    report.append("## 시간 패턴 (Fix → Revert)\n")
    report.append("\n")
    report.append(f"- 총 Fix 커밋: {time_patterns['total_fixes']}개\n")
    report.append(f"- 총 Revert 커밋: {time_patterns['total_reverts']}개\n")
    report.append(f"- 빠른 Revert (< 24시간): {len(time_patterns['quick_reverts'])}개\n")
    report.append("\n")
    
    if time_patterns['quick_reverts']:
        report.append("### 빠른 Revert 사례 (근본 원인 미해결 신호)\n")
        report.append("\n")
        for qr in time_patterns['quick_reverts'][:5]:
            report.append(f"- Fix: {qr['fix']['hash'][:7]} - {qr['fix']['message']}\n")
            report.append(f"  Revert: {qr['revert']['hash'][:7]} - {qr['revert']['message']}\n")
            report.append(f"  간격: {qr['gap_hours']:.1f}시간\n")
            report.append("\n")
    
    # File hotspots
    report.append("## 파일 Hot Spot\n")
    report.append("\n")
    report.append("### 전체 변경 빈도 Top 10\n")
    report.append("\n")
    for file, count in file_patterns['hotspots']:
        report.append(f"- {file}: {count}회\n")
    report.append("\n")
    
    report.append("### 버그 수정 빈도 Top 10\n")
    report.append("\n")
    for file, count in file_patterns['bug_hotspots']:
        report.append(f"- {file}: {count}회\n")
        if count > 5:
            report.append(f"  ⚠️ 설계 문제 의심 (5회 이상)\n")
    report.append("\n")
    
    # Developer patterns
    if dev_patterns:
        report.append("## 개발자 패턴 (Fix 비율)\n")
        report.append("\n")
        for pattern in dev_patterns[:10]:
            report.append(f"- {pattern['author']}\n")
            report.append(f"  총 커밋: {pattern['total_commits']}개\n")
            report.append(f"  Fix 커밋: {pattern['fix_commits']}개\n")
            report.append(f"  Fix 비율: {pattern['fix_ratio']:.1%}\n")
            report.append("\n")
    
    # Recommendations
    report.append("## 권장 사항\n")
    report.append("\n")
    
    if time_patterns['quick_reverts']:
        report.append("1. **빠른 Revert 패턴**\n")
        report.append("   - 근본 원인 분석 없이 빠르게 되돌리는 패턴 발견\n")
        report.append("   - 권장: Fix 전 충분한 테스트 및 근본 원인 분석\n")
        report.append("\n")
    
    bug_hotspots = [f for f, c in file_patterns['bug_hotspots'] if c > 5]
    if bug_hotspots:
        report.append("2. **파일 Hot Spot**\n")
        report.append(f"   - 반복 수정 파일: {', '.join(bug_hotspots[:3])}\n")
        report.append("   - 권장: 해당 파일 리팩토링 또는 설계 개선\n")
        report.append("\n")
    
    high_fix_ratio = [p for p in dev_patterns if p['fix_ratio'] > 0.3]
    if high_fix_ratio:
        report.append("3. **높은 Fix 비율**\n")
        report.append("   - 일부 개발자/모듈에서 Fix 비율 > 30%\n")
        report.append("   - 권장: 페어 프로그래밍, 코드 리뷰 강화\n")
        report.append("\n")
    
    return ''.join(report)


def main():
    parser = argparse.ArgumentParser(description='Detect anti-patterns')
    parser.add_argument('--mode', default='all',
                       choices=['time', 'file', 'developer', 'all'],
                       help='Pattern detection mode')
    parser.add_argument('--days', type=int, default=90,
                       help='Analysis period in days')
    parser.add_argument('--output', default='patterns_report.md',
                       help='Output report file')
    
    args = parser.parse_args()
    
    print(f"🔍 Detecting patterns (last {args.days} days)")
    print(f"   Mode: {args.mode}")
    print()
    
    time_patterns = {}
    file_patterns = {}
    dev_patterns = []
    
    if args.mode in ['time', 'all']:
        print("Analyzing time patterns...")
        time_patterns = detect_time_patterns(args.days)
        print(f"  Found {len(time_patterns['quick_reverts'])} quick reverts")
    
    if args.mode in ['file', 'all']:
        print("Analyzing file hotspots...")
        file_patterns = detect_file_hotspots(args.days)
        print(f"  Top hotspot: {file_patterns['hotspots'][0] if file_patterns['hotspots'] else 'None'}")
    
    if args.mode in ['developer', 'all']:
        print("Analyzing developer patterns...")
        dev_patterns = detect_developer_patterns(args.days)
        print(f"  Analyzed {len(dev_patterns)} developers")
    
    print()
    
    # Generate report
    report = generate_report(time_patterns, file_patterns, dev_patterns)
    
    # Save report
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"📊 Report saved to: {output_path}")
    print()
    print("Next steps:")
    print("  1. Review patterns_report.md")
    print("  2. Identify root causes with LLM")
    print("  3. Create action plan to break the cycle")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
