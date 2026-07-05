#!/usr/bin/env python3
"""
skill_paths.py - Universal Skill Path Resolution Module (Core)

핵심 경로 해석 모듈. 다른 스킬들이 import하여 사용.
resolver.py도 이 모듈을 import하여 CLI 기능을 제공.

Usage in other skills:
    from skill_paths import SkillPaths, get_skill_script, setup_skill_environment
    
    paths = SkillPaths()
    tracer = paths.get_script('runtime-flow-tracer', 'tracer.py')
    subprocess.run([sys.executable, tracer, ...])

Zero dependencies - Python standard library only.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import lru_cache
from dataclasses import dataclass, field


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class EnvironmentInfo:
    """환경 감지 결과"""
    name: str
    skills_root: str
    detection_method: str
    confidence: str  # HIGH, MEDIUM, LOW
    found_skills: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'skills_root': self.skills_root,
            'detection_method': self.detection_method,
            'confidence': self.confidence,
            'found_skills': self.found_skills,
        }


# =============================================================================
# Known Environments
# =============================================================================

KNOWN_ENVIRONMENTS = [
    {
        'name': 'Claude Container',
        'paths': ['/mnt/skills/user', '/mnt/skills/public'],
        'priority': 1,
    },
    {
        'name': 'Gemini CLI (global)',
        'paths': ['~/.gemini/skills', '~/gemini/skills'],
        'priority': 2,
    },
    {
        'name': 'Gemini CLI (local)',
        'paths': ['.gemini/skills', './.gemini/skills'],
        'priority': 3,
    },
    {
        'name': 'Claude CLI (local)',
        'paths': ['.claude/skills', './.claude/skills'],
        'priority': 4,
    },
]


# =============================================================================
# Main Class
# =============================================================================

class SkillPaths:
    """
    Universal skill path resolver.
    
    자동 탐지 우선순위:
    1. $SKILLS_ROOT 환경변수 (명시적 설정)
    2. /mnt/skills/user (Claude Container)
    3. ~/.gemini/skills (Gemini CLI global)
    4. ./.gemini/skills (Gemini CLI local)
    5. ./.claude/skills (Claude CLI local)
    6. 현재 스크립트 위치 기반 추론
    """
    
    def __init__(self, skills_root: Optional[str] = None):
        """
        Args:
            skills_root: 명시적 스킬 루트 경로. None이면 자동 탐지.
        """
        self._skills_root = skills_root or self._auto_detect()
        self._env_info: Optional[EnvironmentInfo] = None
    
    @property
    def root(self) -> str:
        """스킬 루트 디렉토리 경로"""
        return self._skills_root
    
    # Alias for compatibility with resolver.py
    @property
    def skills_root(self) -> str:
        """스킬 루트 디렉토리 경로 (resolver.py 호환)"""
        return self._skills_root
    
    def detect_environment(self) -> EnvironmentInfo:
        """환경 감지 및 정보 반환"""
        if self._env_info is not None:
            return self._env_info
        
        skills_root = self._skills_root
        detection_method = 'unknown'
        confidence = 'LOW'
        env_name = 'Unknown'
        
        # 탐지 방법 결정
        if os.environ.get('SKILLS_ROOT'):
            detection_method = 'environment_variable'
            confidence = 'HIGH'
            env_name = 'Custom (env var)'
        else:
            detection_method = 'directory_scan'
            # 알려진 환경과 매칭
            for env in KNOWN_ENVIRONMENTS:
                for path in env['paths']:
                    expanded = os.path.expanduser(path)
                    try:
                        if os.path.exists(expanded) and os.path.exists(skills_root):
                            if os.path.samefile(skills_root, expanded):
                                env_name = env['name']
                                confidence = 'HIGH'
                                break
                    except (OSError, ValueError):
                        pass
                    
                    if skills_root == expanded or skills_root.endswith(path.lstrip('./')):
                        env_name = env['name']
                        confidence = 'MEDIUM'
        
        self._env_info = EnvironmentInfo(
            name=env_name,
            skills_root=skills_root,
            detection_method=detection_method,
            confidence=confidence,
            found_skills=self.list_skills(),
        )
        
        return self._env_info
    
    @lru_cache(maxsize=32)
    def get_skill_dir(self, skill_name: str) -> Optional[str]:
        """스킬 디렉토리의 절대 경로 반환"""
        path = Path(self._skills_root) / skill_name
        if path.is_dir():
            return str(path.resolve())
        return None
    
    # Alias for compatibility with resolver.py
    def get_skill_path(self, skill_name: str, subpath: str = '') -> str:
        """스킬 경로 반환 (resolver.py 호환)"""
        path = Path(self._skills_root) / skill_name
        if subpath:
            path = path / subpath
        return str(path)
    
    def get_script(self, skill_name: str, script_name: str) -> Optional[str]:
        """스킬 스크립트의 절대 경로 반환"""
        skill_dir = self.get_skill_dir(skill_name)
        if not skill_dir:
            return None
        
        # scripts/ 디렉토리 내
        script_path = Path(skill_dir) / 'scripts' / script_name
        if script_path.is_file():
            return str(script_path.resolve())
        
        # 스킬 디렉토리 직접
        script_path = Path(skill_dir) / script_name
        if script_path.is_file():
            return str(script_path.resolve())
        
        return None
    
    def get_reference(self, skill_name: str, ref_name: str) -> Optional[str]:
        """스킬 참조 문서 경로 반환"""
        skill_dir = self.get_skill_dir(skill_name)
        if not skill_dir:
            return None
        
        ref_path = Path(skill_dir) / 'references' / ref_name
        if ref_path.is_file():
            return str(ref_path.resolve())
        return None
    
    def list_skills(self) -> List[str]:
        """발견된 모든 스킬 이름 목록"""
        skills = []
        root = Path(self._skills_root)
        
        if not root.is_dir():
            return skills
        
        for item in root.iterdir():
            if item.is_dir():
                # SKILL.md 또는 scripts/ 있으면 스킬로 인식
                if (item / 'SKILL.md').exists() or (item / 'scripts').is_dir():
                    skills.append(item.name)
        
        return sorted(skills)
    
    def resolve_relative(self, from_skill: str, to_skill: str,
                         from_subpath: str = 'scripts',
                         to_subpath: str = 'scripts') -> str:
        """두 스킬 간 상대 경로 계산"""
        from_path = Path(self._skills_root) / from_skill / from_subpath
        to_path = Path(self._skills_root) / to_skill / to_subpath
        
        try:
            return os.path.relpath(to_path, from_path)
        except ValueError:
            # Windows에서 드라이브가 다른 경우
            return str(to_path)
    
    # Alias for compatibility
    resolve_relative_path = resolve_relative
    
    def _auto_detect(self) -> str:
        """자동으로 스킬 루트 탐지"""
        
        # 1. 환경변수 (최우선)
        env_root = os.environ.get('SKILLS_ROOT')
        if env_root and os.path.isdir(env_root):
            return env_root
        
        # 2. 알려진 경로 탐색
        for env in KNOWN_ENVIRONMENTS:
            for path in env['paths']:
                expanded = os.path.expanduser(path)
                
                # 절대 경로
                if os.path.isabs(expanded) and os.path.isdir(expanded):
                    return expanded
                
                # 상대 경로 - 프로젝트 루트부터 탐색
                for start_dir in self._get_project_roots():
                    candidate = os.path.join(start_dir, expanded)
                    if os.path.isdir(candidate):
                        return os.path.abspath(candidate)
        
        # 3. 현재 스크립트 위치 기반 추론
        script_based = self._detect_from_script_location()
        if script_based:
            return script_based
        
        # 4. Fallback
        return os.getcwd()
    
    def _get_project_roots(self) -> List[str]:
        """프로젝트 루트 후보 디렉토리 목록"""
        roots = [os.getcwd()]
        
        current = Path.cwd()
        for parent in [current] + list(current.parents)[:5]:
            markers = ['.git', 'package.json', 'pyproject.toml', 'setup.py', 'Cargo.toml']
            if any((parent / m).exists() for m in markers):
                roots.append(str(parent))
        
        return roots
    
    def _detect_from_script_location(self) -> Optional[str]:
        """현재 실행 중인 스크립트 위치에서 스킬 루트 추론"""
        try:
            script_path = Path(__file__).resolve()
        except NameError:
            return None
        
        # 상위 디렉토리 탐색
        for parent in script_path.parents:
            if (parent / 'SKILL.md').exists():
                return str(parent.parent)
            
            # 여러 스킬 디렉토리가 있는지 확인
            if parent.is_dir():
                skill_count = sum(
                    1 for item in parent.iterdir()
                    if item.is_dir() and (item / 'SKILL.md').exists()
                )
                if skill_count >= 2:
                    return str(parent)
        
        return None
    
    def __str__(self) -> str:
        return f"SkillPaths(root={self._skills_root})"
    
    def __repr__(self) -> str:
        return self.__str__()


# =============================================================================
# Convenience Functions (다른 스킬에서 간편하게 사용)
# =============================================================================

_default_paths: Optional[SkillPaths] = None

def get_paths() -> SkillPaths:
    """싱글톤 SkillPaths 인스턴스 반환"""
    global _default_paths
    if _default_paths is None:
        _default_paths = SkillPaths()
    return _default_paths

def get_skill_script(skill_name: str, script_name: str) -> Optional[str]:
    """스킬 스크립트 경로 반환 (편의 함수)"""
    return get_paths().get_script(skill_name, script_name)

def get_skills_root() -> str:
    """스킬 루트 디렉토리 반환 (편의 함수)"""
    return get_paths().root

def setup_skill_environment(skill_name: str) -> None:
    """
    스킬 환경 설정 - sys.path에 스킬 경로 추가
    
    다른 스킬을 import해야 할 때 사용:
        setup_skill_environment('class-hierarchy-classifier')
        from hierarchy_classifier import ClassHierarchyAnalyzer
    """
    paths = get_paths()
    skill_dir = paths.get_skill_dir(skill_name)
    
    if skill_dir:
        scripts_dir = os.path.join(skill_dir, 'scripts')
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        if skill_dir not in sys.path:
            sys.path.insert(0, skill_dir)


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI로 실행 시 환경 정보 출력"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description='Skill Path Resolver - Core Module',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('command', nargs='?', default='info',
                        choices=['info', 'list', 'path', 'export', 'env'],
                        help='Command to run')
    parser.add_argument('--skill', help='Skill name')
    parser.add_argument('--script', help='Script name')
    parser.add_argument('--shell', default='bash', 
                        choices=['bash', 'zsh', 'fish', 'powershell'],
                        help='Shell for export command')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    paths = SkillPaths()
    
    if args.command == 'info' or args.command == 'env':
        env = paths.detect_environment()
        if args.json:
            print(json.dumps(env.to_dict(), indent=2))
        else:
            print(f"SKILLS_ROOT: {env.skills_root}")
            print(f"Environment: {env.name}")
            print(f"Detection: {env.detection_method} ({env.confidence})")
            print(f"Skills found: {len(env.found_skills)}")
            
    elif args.command == 'list':
        for skill in paths.list_skills():
            print(f"  {skill}")
            
    elif args.command == 'path':
        if args.skill:
            if args.script:
                result = paths.get_script(args.skill, args.script)
            else:
                result = paths.get_skill_dir(args.skill)
            print(result or f"Not found: {args.skill}")
        else:
            print(paths.root)
            
    elif args.command == 'export':
        root = paths.root
        if args.shell in ['bash', 'zsh']:
            print(f'export SKILLS_ROOT="{root}"')
        elif args.shell == 'fish':
            print(f'set -gx SKILLS_ROOT "{root}"')
        elif args.shell == 'powershell':
            print(f'$env:SKILLS_ROOT = "{root}"')


if __name__ == '__main__':
    main()
