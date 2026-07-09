#!/usr/bin/env python3
"""
Skill Path Resolver - CLI Tool for path management across environments

This is the CLI tool version. For programmatic use in other skills,
use skill_paths.py instead:

    from skill_paths import SkillPaths, get_skill_script
    paths = SkillPaths()
    script = paths.get_script('some-skill', 'script.py')

Unique features of resolver.py (not in skill_paths.py):
- Hardcoded path fixing (fix, fix-all commands)
- Pattern-based path replacement in source files

Supports:
- Environment detection (Claude, Gemini CLI, Custom)
- Path resolution between skills
- Hardcoded path fixing
- Configuration export

Usage:
    python resolver.py detect
    python resolver.py fix --skill <skill_name>
    python resolver.py fix-all [--dry-run]
    python resolver.py export --shell bash
"""

from __future__ import annotations

import os
import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# ============================================================
# Optional Integration with skill_paths.py
# ============================================================

def _try_import_skill_paths():
    """Try to import skill_paths.py for consistent path resolution"""
    try:
        from skill_paths import SkillPaths, get_skills_root
        return SkillPaths, get_skills_root
    except ImportError:
        return None, None

_CoreSkillPaths, _get_core_skills_root = _try_import_skill_paths()


# ============================================================
# Path Patterns to Detect and Fix
# ============================================================

HARDCODED_PATTERNS = {
    'python': [
        # sys.path.insert with absolute path
        (r'sys\.path\.insert\(\s*\d+\s*,\s*["\'](/[^"\']+/skills/[^"\']+)["\']',
         'sys.path.insert(0, os.path.join(get_skills_root(), "{relative_path}"))'),
        
        # Direct path strings
        (r'["\'](/mnt/skills/user/[^"\']+)["\']',
         '"{resolved_path}"'),
        (r'["\'](/[^"\']*\.gemini/skills/[^"\']+)["\']',
         '"{resolved_path}"'),
    ],
    'bash': [
        # Absolute paths in commands
        (r'(/mnt/skills/user/[^\s"\']+)',
         '$SKILLS_ROOT/{relative_path}'),
        (r'(/[^\s"\']*\.gemini/skills/[^\s"\']+)',
         '$SKILLS_ROOT/{relative_path}'),
    ],
    'markdown': [
        # Paths in documentation
        (r'`(/mnt/skills/user/[^`]+)`',
         '`$SKILLS_ROOT/{relative_path}`'),
        (r'(/mnt/skills/user/[^\s\)]+)',
         '$SKILLS_ROOT/{relative_path}'),
    ]
}

KNOWN_ENVIRONMENTS = [
    {
        'name': 'Claude Container',
        'paths': ['/mnt/skills/user', '/mnt/skills/public'],
        'priority': 1,
    },
    {
        'name': 'Gemini CLI (global)',
        'paths': [
            os.path.expanduser('~/.gemini/skills'),
            os.path.expanduser('~/gemini/skills'),
        ],
        'priority': 2,
    },
    {
        'name': 'Gemini CLI (local)',
        'paths': ['.gemini/skills', './.gemini/skills'],
        'priority': 3,
    },
    {
        'name': 'Custom (env var)',
        'paths': [],  # Populated from SKILLS_ROOT
        'priority': 0,
    },
]


@dataclass
class EnvironmentInfo:
    """Detected environment information"""
    name: str
    skills_root: str
    detection_method: str
    confidence: str  # HIGH, MEDIUM, LOW
    found_skills: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'skills_root': self.skills_root,
            'detection_method': self.detection_method,
            'confidence': self.confidence,
            'found_skills': self.found_skills,
        }


@dataclass
class FixResult:
    """Result of a path fix operation"""
    file_path: str
    changes: List[Tuple[str, str]]  # (old, new)
    success: bool
    error: Optional[str] = None


class SkillPathResolver:
    """
    Main resolver class with hardcoded path fixing capabilities.
    
    Uses skill_paths.py for path detection if available,
    otherwise falls back to built-in implementation.
    """
    
    def __init__(self, skills_root: Optional[str] = None):
        # Try to use skill_paths.py first for consistent detection
        if skills_root:
            self.skills_root = skills_root
        elif _CoreSkillPaths is not None:
            # Use skill_paths.py's detection
            core = _CoreSkillPaths()
            self.skills_root = core.root
        else:
            # Fallback to built-in detection
            self.skills_root = self._detect_skills_root()
    
    def _detect_skills_root(self) -> str:
        """Auto-detect skills root directory (fallback if skill_paths.py unavailable)"""
        
        # 1. Check environment variable (highest priority)
        if os.environ.get('SKILLS_ROOT'):
            path = os.environ['SKILLS_ROOT']
            if os.path.isdir(path):
                return path
        
        # 2. Check known locations
        for env in KNOWN_ENVIRONMENTS:
            for path in env['paths']:
                expanded = os.path.expanduser(path)
                if os.path.isdir(expanded):
                    return expanded
        
        # 3. Try to detect from current script location
        script_dir = Path(__file__).resolve().parent
        # Assume: .../skill-path-resolver/scripts/resolver.py
        potential_root = script_dir.parent.parent
        if (potential_root / 'skill-path-resolver').is_dir():
            return str(potential_root)
        
        # 4. Fallback
        return os.getcwd()
    
    def detect_environment(self) -> EnvironmentInfo:
        """Detect current environment and return info"""
        
        skills_root = self.skills_root
        detection_method = 'unknown'
        confidence = 'LOW'
        env_name = 'Unknown'
        
        # Determine detection method
        if os.environ.get('SKILLS_ROOT'):
            detection_method = 'environment_variable'
            confidence = 'HIGH'
            env_name = 'Custom (env var)'
        else:
            detection_method = 'directory_scan'
            # Match against known environments
            for env in KNOWN_ENVIRONMENTS:
                for path in env['paths']:
                    expanded = os.path.expanduser(path)
                    if os.path.samefile(skills_root, expanded) if os.path.exists(expanded) else False:
                        env_name = env['name']
                        confidence = 'HIGH'
                        break
                    elif skills_root == expanded or skills_root.endswith(path.lstrip('./')):
                        env_name = env['name']
                        confidence = 'MEDIUM'
        
        # Find skills in directory
        found_skills = []
        if os.path.isdir(skills_root):
            for item in os.listdir(skills_root):
                item_path = os.path.join(skills_root, item)
                if os.path.isdir(item_path):
                    # Check if it looks like a skill (has SKILL.md or scripts/)
                    if (os.path.exists(os.path.join(item_path, 'SKILL.md')) or
                        os.path.exists(os.path.join(item_path, 'scripts'))):
                        found_skills.append(item)
        
        return EnvironmentInfo(
            name=env_name,
            skills_root=skills_root,
            detection_method=detection_method,
            confidence=confidence,
            found_skills=sorted(found_skills),
        )
    
    def resolve_relative_path(self, from_skill: str, to_skill: str, 
                               from_subpath: str = 'scripts', 
                               to_subpath: str = 'scripts') -> str:
        """Calculate relative path between two skills"""
        
        from_path = Path(self.skills_root) / from_skill / from_subpath
        to_path = Path(self.skills_root) / to_skill / to_subpath
        
        try:
            relative = os.path.relpath(to_path, from_path)
            return relative
        except ValueError:
            # Different drives on Windows
            return str(to_path)
    
    def get_skill_path(self, skill_name: str, subpath: str = '') -> str:
        """Get absolute path to a skill or its subpath"""
        path = Path(self.skills_root) / skill_name
        if subpath:
            path = path / subpath
        return str(path)
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type for pattern matching"""
        ext = Path(file_path).suffix.lower()
        if ext in ['.py']:
            return 'python'
        elif ext in ['.sh', '.bash', '.zsh']:
            return 'bash'
        elif ext in ['.md', '.markdown']:
            return 'markdown'
        elif ext in ['.js', '.ts']:
            return 'javascript'
        return 'unknown'
    
    def _extract_relative_path(self, absolute_path: str) -> str:
        """Extract relative path from absolute skill path"""
        # Match various skill root patterns
        patterns = [
            r"$SKILLS_ROOT/(.+)",
            r'/mnt/skills/public/(.+)',
            r'\.gemini/skills/(.+)',
            r'gemini/skills/(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, absolute_path)
            if match:
                return match.group(1)
        
        # If no match, try to extract from skills_root
        if self.skills_root and absolute_path.startswith(self.skills_root):
            return absolute_path[len(self.skills_root):].lstrip('/')
        
        return absolute_path
    
    def fix_file(self, file_path: str, dry_run: bool = False) -> FixResult:
        """Fix hardcoded paths in a single file"""
        
        if not os.path.exists(file_path):
            return FixResult(file_path, [], False, f"File not found: {file_path}")
        
        file_type = self._get_file_type(file_path)
        if file_type not in HARDCODED_PATTERNS:
            return FixResult(file_path, [], True, "Unsupported file type")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return FixResult(file_path, [], False, str(e))
        
        changes = []
        new_content = content
        
        patterns = HARDCODED_PATTERNS[file_type]
        for pattern, replacement_template in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                old_text = match.group(0)
                if match.groups():
                    absolute_path = match.group(1)
                    relative_path = self._extract_relative_path(absolute_path)
                    
                    # Create replacement
                    if '{relative_path}' in replacement_template:
                        new_text = replacement_template.format(relative_path=relative_path)
                    elif '{resolved_path}' in replacement_template:
                        new_text = replacement_template.format(
                            resolved_path=f"$SKILLS_ROOT/{relative_path}"
                        )
                    else:
                        new_text = replacement_template
                    
                    if old_text != new_text:
                        changes.append((old_text, new_text))
                        new_content = new_content.replace(old_text, new_text, 1)
        
        if changes and not dry_run:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            except Exception as e:
                return FixResult(file_path, changes, False, str(e))
        
        return FixResult(file_path, changes, True)
    
    def fix_skill(self, skill_name: str, dry_run: bool = False) -> List[FixResult]:
        """Fix all files in a skill"""
        
        skill_path = self.get_skill_path(skill_name)
        if not os.path.isdir(skill_path):
            return [FixResult(skill_path, [], False, f"Skill not found: {skill_name}")]
        
        results = []
        
        # File extensions to process
        extensions = ['.py', '.sh', '.bash', '.md', '.js']
        
        for root, dirs, files in os.walk(skill_path):
            # Skip __pycache__
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    result = self.fix_file(file_path, dry_run)
                    if result.changes:  # Only include files with changes
                        results.append(result)
        
        return results
    
    def fix_all_skills(self, dry_run: bool = False) -> Dict[str, List[FixResult]]:
        """Fix all skills in the skills root"""
        
        env = self.detect_environment()
        all_results = {}
        
        for skill_name in env.found_skills:
            results = self.fix_skill(skill_name, dry_run)
            if results:
                all_results[skill_name] = results
        
        return all_results
    
    def export_config(self, shell: str = 'bash', format: str = 'shell') -> str:
        """Export configuration for different shells/formats"""
        
        env = self.detect_environment()
        
        if format == 'json':
            return json.dumps({
                'SKILLS_ROOT': env.skills_root,
                'environment': env.to_dict(),
            }, indent=2)
        
        if shell == 'bash' or shell == 'zsh':
            return f'''# Skill Path Configuration
# Generated by skill-path-resolver

export SKILLS_ROOT="{env.skills_root}"

# Helper function to get skill path
get_skill_path() {{
    echo "$SKILLS_ROOT/$1"
}}

# Verify setup
if [ -d "$SKILLS_ROOT" ]; then
    echo "✓ SKILLS_ROOT set to: $SKILLS_ROOT"
else
    echo "✗ Warning: SKILLS_ROOT directory not found: $SKILLS_ROOT"
fi
'''
        
        elif shell == 'fish':
            return f'''# Skill Path Configuration
# Generated by skill-path-resolver

set -gx SKILLS_ROOT "{env.skills_root}"

# Helper function
function get_skill_path
    echo "$SKILLS_ROOT/$argv[1]"
end
'''
        
        elif shell == 'powershell':
            return f'''# Skill Path Configuration
# Generated by skill-path-resolver

$env:SKILLS_ROOT = "{env.skills_root}"

function Get-SkillPath {{
    param([string]$SkillName)
    return Join-Path $env:SKILLS_ROOT $SkillName
}}
'''
        
        return f'export SKILLS_ROOT="{env.skills_root}"'


def main():
    parser = argparse.ArgumentParser(
        description='Skill Path Resolver - Fix paths across environments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # detect command
    detect_parser = subparsers.add_parser('detect', help='Detect environment')
    detect_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # resolve command
    resolve_parser = subparsers.add_parser('resolve', help='Resolve path between skills')
    resolve_parser.add_argument('--from', dest='from_path', required=True,
                                help='Source skill/path')
    resolve_parser.add_argument('--to', dest='to_path', required=True,
                                help='Target skill/path')
    
    # fix command
    fix_parser = subparsers.add_parser('fix', help='Fix hardcoded paths in a skill')
    fix_parser.add_argument('--skill', required=True, help='Skill name to fix')
    fix_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    
    # fix-all command
    fix_all_parser = subparsers.add_parser('fix-all', help='Fix all skills')
    fix_all_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
    
    # export command
    export_parser = subparsers.add_parser('export', help='Export configuration')
    export_parser.add_argument('--shell', choices=['bash', 'zsh', 'fish', 'powershell'],
                               default='bash', help='Shell type')
    export_parser.add_argument('--format', choices=['shell', 'json'],
                               default='shell', help='Output format')
    
    args = parser.parse_args()
    
    resolver = SkillPathResolver()
    
    if args.command == 'detect':
        env = resolver.detect_environment()
        if args.json:
            print(json.dumps(env.to_dict(), indent=2))
        else:
            print("Environment Detection Report")
            print("=" * 40)
            print(f"Detected SKILLS_ROOT: {env.skills_root}")
            print(f"Environment: {env.name}")
            print(f"Detection Method: {env.detection_method}")
            print(f"Confidence: {env.confidence}")
            print()
            print("Found Skills:")
            for skill in env.found_skills:
                print(f"  ✓ {skill}")
    
    elif args.command == 'resolve':
        # Parse from/to paths
        from_parts = args.from_path.split('/')
        to_parts = args.to_path.split('/')
        
        from_skill = from_parts[0]
        to_skill = to_parts[0]
        
        from_subpath = '/'.join(from_parts[1:]) if len(from_parts) > 1 else 'scripts'
        to_subpath = '/'.join(to_parts[1:]) if len(to_parts) > 1 else 'scripts'
        
        relative = resolver.resolve_relative_path(from_skill, to_skill, 
                                                   from_subpath, to_subpath)
        print(f"Resolved Path: {relative}")
    
    elif args.command == 'fix':
        results = resolver.fix_skill(args.skill, args.dry_run)
        
        action = "Would fix" if args.dry_run else "Fixed"
        
        if not results:
            print(f"No changes needed for skill: {args.skill}")
        else:
            for result in results:
                print(f"\n{result.file_path}:")
                for old, new in result.changes:
                    print(f"  - {old[:50]}...")
                    print(f"  + {new[:50]}...")
                if not result.success:
                    print(f"  ✗ Error: {result.error}")
                else:
                    print(f"  ✓ {action} {len(result.changes)} path(s)")
    
    elif args.command == 'fix-all':
        all_results = resolver.fix_all_skills(args.dry_run)
        
        action = "Would fix" if args.dry_run else "Fixed"
        
        if not all_results:
            print("No changes needed for any skill")
        else:
            total_changes = 0
            for skill_name, results in all_results.items():
                skill_changes = sum(len(r.changes) for r in results)
                total_changes += skill_changes
                print(f"\n{skill_name}: {skill_changes} change(s)")
                for result in results:
                    print(f"  {Path(result.file_path).name}: {len(result.changes)} change(s)")
            
            print(f"\n{'=' * 40}")
            print(f"Total: {action} {total_changes} path(s) in {len(all_results)} skill(s)")
    
    elif args.command == 'export':
        config = resolver.export_config(args.shell, args.format)
        print(config)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
