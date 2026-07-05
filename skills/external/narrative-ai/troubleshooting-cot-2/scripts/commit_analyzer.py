#!/usr/bin/env python3
"""
Commit Analyzer - Phase 1

커밋 메시지를 분석하여 관련성 점수를 부여합니다.
LLM이 없어도 기본적인 키워드 매칭으로 동작합니다.

Usage:
    python commit_analyzer.py --problem "세션 토큰 누락" --count 40 --output scores.md
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_commits(count=40):
    """최근 N개 커밋 가져오기"""
    try:
        result = subprocess.run(
            ['git', 'log', f'-{count}', '--pretty=format:%h|%ad|%an|%s', '--date=short'],
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 3)
            if len(parts) == 4:
                commits.append({
                    'hash': parts[0],
                    'date': parts[1],
                    'author': parts[2],
                    'message': parts[3]
                })
        
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error getting commits: {e}", file=sys.stderr)
        return []


def extract_keywords(problem_description):
    """문제 설명에서 키워드 추출"""
    # 간단한 키워드 추출 (공백으로 분리)
    words = re.findall(r'\w+', problem_description.lower())
    
    # 불용어 제거
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    
    return keywords


def score_commit(commit, keywords, problem_description):
    """커밋의 관련성 점수 계산 (0-10)"""
    message = commit['message'].lower()
    score = 0
    reasons = []
    
    # 키워드 매칭 (최대 7점)
    keyword_matches = sum(1 for kw in keywords if kw in message)
    if keyword_matches > 0:
        keyword_score = min(keyword_matches * 2, 7)
        score += keyword_score
        reasons.append(f"{keyword_matches}개 키워드 일치")
    
    # Fix/Bug 키워드 가산점 (최대 +2점)
    if any(word in message for word in ['fix', 'bug', 'error', 'issue']):
        score += 2
        reasons.append("버그 수정 관련")
    
    # Revert 감점 (-1점)
    if 'revert' in message:
        score = max(0, score - 1)
        reasons.append("Revert 커밋")
    
    # Docs/Test만 수정은 낮은 점수
    if any(word in message for word in ['docs:', 'doc:', 'test:', 'tests:']):
        if score > 3:
            score = 3
        reasons.append("문서/테스트만 수정")
    
    # 점수 정규화 (0-10)
    score = min(score, 10)
    
    return score, reasons


def generate_markdown_report(commits, scores, problem):
    """마크다운 보고서 생성"""
    lines = []
    
    lines.append(f"# 커밋 분석 보고서\n")
    lines.append(f"\n**문제:** {problem}\n")
    lines.append(f"**분석 커밋 수:** {len(commits)}개\n")
    lines.append("\n---\n")
    
    # 점수별로 정렬
    sorted_commits = sorted(
        zip(commits, scores),
        key=lambda x: x[1][0],
        reverse=True
    )
    
    # HIGH 우선순위 (9-10점)
    high = [c for c, (s, _) in sorted_commits if s >= 9]
    lines.append("\n## HIGH 우선순위 (9-10점)\n")
    if high:
        lines.append("\n| 점수 | 해시 | 날짜 | 메시지 | 분류 근거 |\n")
        lines.append("|------|------|------|--------|----------|\n")
        for commit, (score, reasons) in sorted_commits:
            if score >= 9:
                reason_str = ", ".join(reasons) if reasons else "-"
                lines.append(f"| {score} | {commit['hash']} | {commit['date']} | {commit['message']} | {reason_str} |\n")
    else:
        lines.append("\n해당 없음\n")
    
    # MEDIUM 우선순위 (6-8점)
    medium = [c for c, (s, _) in sorted_commits if 6 <= s < 9]
    lines.append("\n## MEDIUM 우선순위 (6-8점)\n")
    if medium:
        lines.append("\n| 점수 | 해시 | 날짜 | 메시지 | 분류 근거 |\n")
        lines.append("|------|------|------|--------|----------|\n")
        for commit, (score, reasons) in sorted_commits:
            if 6 <= score < 9:
                reason_str = ", ".join(reasons) if reasons else "-"
                lines.append(f"| {score} | {commit['hash']} | {commit['date']} | {commit['message']} | {reason_str} |\n")
    else:
        lines.append("\n해당 없음\n")
    
    # LOW 우선순위 (1-5점)
    lines.append("\n## LOW 우선순위 (1-5점)\n")
    low_count = sum(1 for c, (s, _) in sorted_commits if 1 <= s < 6)
    lines.append(f"\n{low_count}개 커밋 (자세한 내용 생략)\n")
    
    # 다음 단계
    lines.append("\n---\n\n## 다음 단계\n")
    if high:
        lines.append(f"\n1. HIGH 우선순위 {len(high)}개 커밋의 상세 diff 분석\n")
        lines.append("2. Phase 2로 진행: Good/Bad Case 식별\n")
        lines.append("\n```bash\n")
        for commit, _ in sorted_commits[:5]:
            if commit in high:
                lines.append(f"git show {commit['hash']} -p > diffs/{commit['hash']}.diff\n")
        lines.append("```\n")
    else:
        lines.append("\n⚠️ HIGH 우선순위 커밋이 없습니다.\n")
        lines.append("- 분석 범위 확대 고려 (60개 커밋)\n")
        lines.append("- 문제 정의 구체화 필요\n")
    
    return ''.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Analyze commit messages')
    parser.add_argument('--problem', required=True, help='Problem description')
    parser.add_argument('--count', type=int, default=40, help='Number of commits to analyze')
    parser.add_argument('--output', default='scores.md', help='Output markdown file')
    
    args = parser.parse_args()
    
    print(f"🔍 Analyzing {args.count} commits")
    print(f"   Problem: {args.problem}")
    print()
    
    # Get commits
    commits = get_commits(args.count)
    if not commits:
        print("Error: No commits found", file=sys.stderr)
        return 1
    
    print(f"Found {len(commits)} commits")
    
    # Extract keywords
    keywords = extract_keywords(args.problem)
    print(f"Keywords: {', '.join(keywords)}")
    print()
    
    # Score each commit
    scores = []
    for commit in commits:
        score, reasons = score_commit(commit, keywords, args.problem)
        scores.append((score, reasons))
    
    # Generate report
    report = generate_markdown_report(commits, scores, args.problem)
    
    # Save to file
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"📊 Analysis complete")
    
    # Summary
    high_count = sum(1 for s, _ in scores if s >= 9)
    medium_count = sum(1 for s, _ in scores if 6 <= s < 9)
    
    print(f"\n   HIGH (9-10):   {high_count} commits")
    print(f"   MEDIUM (6-8):  {medium_count} commits")
    print(f"   LOW (1-5):     {len(commits) - high_count - medium_count} commits")
    print()
    print(f"💾 Report saved to: {output_path}")
    
    if high_count == 0:
        print()
        print("⚠️  No HIGH priority commits found")
        print("   Consider: expanding search range or refining problem description")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
