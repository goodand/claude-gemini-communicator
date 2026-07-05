#!/usr/bin/env python3
"""
workspace_manager.py - 스킬 실행 중 생성되는 중간 파일 관리

Problems solved:
1. 스킬 실행 후 남는 불필요한 파일들 자동 정리
2. 임시 작업 디렉토리 자동 생성/삭제
3. 최종 결과물만 지정 위치로 이동

Usage:
    from workspace_manager import Workspace
    
    with Workspace(keep=['final_flow.mmd']) as ws:
        # 모든 중간 파일은 ws.path에 생성
        trace_file = ws.temp_file('trace.json')
        
        # 작업 수행...
        subprocess.run([...], cwd=ws.path)
        
        # with 블록 종료 시 keep 목록 외 파일 자동 삭제
        # keep 파일들은 원래 위치로 복사

Zero dependencies - Python standard library only.
"""

import os
import sys
import shutil
import tempfile
import atexit
from pathlib import Path
from typing import List, Optional, Set, Union
from contextlib import contextmanager
from datetime import datetime


class Workspace:
    """
    스킬 작업용 임시 워크스페이스 관리자
    
    Features:
    - 임시 디렉토리에서 작업
    - 종료 시 자동 정리
    - 지정 파일만 보존
    """
    
    def __init__(
        self,
        keep: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        prefix: str = 'skill_workspace_',
        cleanup_on_error: bool = False,
        verbose: bool = False
    ):
        """
        Args:
            keep: 보존할 파일 패턴 목록 (예: ['*.mmd', 'final_*.json'])
            output_dir: 최종 결과물 저장 위치 (기본: 현재 디렉토리)
            prefix: 임시 디렉토리 접두사
            cleanup_on_error: 에러 발생 시에도 정리할지 여부
            verbose: 상세 로그 출력
        """
        self.keep_patterns = keep or []
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.prefix = prefix
        self.cleanup_on_error = cleanup_on_error
        self.verbose = verbose
        
        self._temp_dir: Optional[tempfile.TemporaryDirectory] = None
        self._path: Optional[Path] = None
        self._created_files: Set[str] = set()
        self._error_occurred = False
    
    @property
    def path(self) -> Path:
        """현재 작업 디렉토리 경로"""
        if self._path is None:
            raise RuntimeError("Workspace not initialized. Use 'with Workspace() as ws:'")
        return self._path
    
    def temp_file(self, name: str) -> Path:
        """임시 파일 경로 생성 및 추적"""
        file_path = self.path / name
        self._created_files.add(name)
        return file_path
    
    def keep_file(self, name: str) -> None:
        """파일을 보존 목록에 추가"""
        self.keep_patterns.append(name)
    
    def __enter__(self) -> 'Workspace':
        """워크스페이스 생성"""
        self._temp_dir = tempfile.TemporaryDirectory(prefix=self.prefix)
        self._path = Path(self._temp_dir.name)
        
        if self.verbose:
            print(f"[Workspace] Created: {self._path}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """워크스페이스 정리"""
        if exc_type is not None:
            self._error_occurred = True
            if self.verbose:
                print(f"[Workspace] Error occurred: {exc_val}")
        
        if self._error_occurred and not self.cleanup_on_error:
            if self.verbose:
                print(f"[Workspace] Keeping files due to error: {self._path}")
            return
        
        # 보존할 파일 복사
        self._copy_kept_files()
        
        # 임시 디렉토리 삭제
        if self._temp_dir:
            self._temp_dir.cleanup()
            if self.verbose:
                print(f"[Workspace] Cleaned up: {self._path}")
    
    def _copy_kept_files(self) -> None:
        """보존 패턴에 맞는 파일들을 출력 디렉토리로 복사"""
        import fnmatch
        
        if not self._path or not self._path.exists():
            return
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in self._path.iterdir():
            if not file_path.is_file():
                continue
            
            # 보존 패턴 매칭
            should_keep = any(
                fnmatch.fnmatch(file_path.name, pattern)
                for pattern in self.keep_patterns
            )
            
            if should_keep:
                dest = self.output_dir / file_path.name
                shutil.copy2(file_path, dest)
                if self.verbose:
                    print(f"[Workspace] Kept: {file_path.name} -> {dest}")


class FileTracker:
    """
    기존 디렉토리에서 새로 생성된 파일 추적 및 정리
    
    Usage:
        tracker = FileTracker(cleanup_patterns=['*.json', '*.log'])
        tracker.snapshot()  # 현재 상태 저장
        
        # 작업 수행...
        
        tracker.cleanup()  # 새로 생성된 파일 중 패턴 매칭된 것 삭제
    """
    
    def __init__(
        self,
        directory: Optional[str] = None,
        cleanup_patterns: Optional[List[str]] = None,
        keep_patterns: Optional[List[str]] = None
    ):
        """
        Args:
            directory: 추적할 디렉토리 (기본: 현재 디렉토리)
            cleanup_patterns: 정리할 파일 패턴 (예: ['*_trace.json', '*.log'])
            keep_patterns: 정리에서 제외할 패턴 (예: ['final_*'])
        """
        self.directory = Path(directory) if directory else Path.cwd()
        self.cleanup_patterns = cleanup_patterns or []
        self.keep_patterns = keep_patterns or []
        self._initial_files: Set[str] = set()
    
    def snapshot(self) -> None:
        """현재 파일 목록 저장"""
        self._initial_files = set(
            f.name for f in self.directory.iterdir() if f.is_file()
        )
    
    def get_new_files(self) -> List[str]:
        """스냅샷 이후 새로 생성된 파일 목록"""
        current_files = set(
            f.name for f in self.directory.iterdir() if f.is_file()
        )
        return sorted(current_files - self._initial_files)
    
    def cleanup(self, dry_run: bool = False) -> List[str]:
        """
        새로 생성된 파일 중 cleanup_patterns에 맞는 것 삭제
        
        Returns:
            삭제된(또는 삭제 예정인) 파일 목록
        """
        import fnmatch
        
        deleted = []
        new_files = self.get_new_files()
        
        for filename in new_files:
            # cleanup 패턴 매칭 확인
            should_cleanup = any(
                fnmatch.fnmatch(filename, pattern)
                for pattern in self.cleanup_patterns
            )
            
            # keep 패턴 매칭 확인 (우선)
            should_keep = any(
                fnmatch.fnmatch(filename, pattern)
                for pattern in self.keep_patterns
            )
            
            if should_cleanup and not should_keep:
                file_path = self.directory / filename
                if not dry_run:
                    file_path.unlink()
                deleted.append(filename)
        
        return deleted


# ============================================================
# Convenience Functions
# ============================================================

@contextmanager
def skill_workspace(
    keep: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    verbose: bool = False
):
    """
    스킬 실행용 임시 워크스페이스 컨텍스트 매니저
    
    Usage:
        with skill_workspace(keep=['final_flow.mmd']) as ws:
            # ws.path에서 작업
            subprocess.run([...], cwd=ws.path)
    """
    with Workspace(keep=keep, output_dir=output_dir, verbose=verbose) as ws:
        yield ws


def cleanup_skill_artifacts(
    directory: Optional[str] = None,
    patterns: Optional[List[str]] = None,
    keep: Optional[List[str]] = None,
    dry_run: bool = False
) -> List[str]:
    """
    스킬 실행 후 중간 파일 정리
    
    Args:
        directory: 정리할 디렉토리
        patterns: 정리할 파일 패턴
        keep: 보존할 파일 패턴
        dry_run: True면 실제 삭제하지 않음
        
    Returns:
        삭제된 파일 목록
    """
    default_patterns = [
        # 로그 파일
        '*.log',
        '*_log.txt',
        # 중간 데이터 파일
        '*_trace.json',
        '*_arch.json',
        '*_edges.txt',
        '*_edges.json',
        'static_arch.json',
        'dynamic_trace.json',
        # 임시 파일
        '*.tmp',
        '*.temp',
    ]
    
    default_keep = [
        # 최종 결과물
        'final_*',
        '*_final.*',
        '*.mmd',  # Mermaid 다이어그램
        'REPORT_*',
    ]
    
    dir_path = Path(directory) if directory else Path.cwd()
    cleanup_patterns = patterns or default_patterns
    keep_patterns = keep or default_keep
    
    import fnmatch
    deleted = []
    
    for file_path in dir_path.iterdir():
        if not file_path.is_file():
            continue
        
        filename = file_path.name
        
        # cleanup 패턴 매칭
        should_cleanup = any(
            fnmatch.fnmatch(filename, p) for p in cleanup_patterns
        )
        
        # keep 패턴 매칭 (우선)
        should_keep = any(
            fnmatch.fnmatch(filename, p) for p in keep_patterns
        )
        
        if should_cleanup and not should_keep:
            if not dry_run:
                file_path.unlink()
            deleted.append(filename)
    
    return deleted


# ============================================================
# CLI Interface
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Skill Workspace Manager - Clean up intermediate files'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up skill artifacts')
    cleanup_parser.add_argument('--dir', '-d', default='.', help='Directory to clean')
    cleanup_parser.add_argument('--pattern', '-p', action='append', 
                                help='Patterns to delete (can use multiple)')
    cleanup_parser.add_argument('--keep', '-k', action='append',
                                help='Patterns to keep (can use multiple)')
    cleanup_parser.add_argument('--dry-run', action='store_true',
                                help='Show what would be deleted')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List skill artifacts')
    list_parser.add_argument('--dir', '-d', default='.', help='Directory to scan')
    
    args = parser.parse_args()
    
    if args.command == 'cleanup':
        deleted = cleanup_skill_artifacts(
            directory=args.dir,
            patterns=args.pattern,
            keep=args.keep,
            dry_run=args.dry_run
        )
        
        action = "Would delete" if args.dry_run else "Deleted"
        if deleted:
            print(f"{action} {len(deleted)} file(s):")
            for f in deleted:
                print(f"  - {f}")
        else:
            print("No files to clean up")
            
    elif args.command == 'list':
        dir_path = Path(args.dir)
        default_patterns = ['*.log', '*_trace.json', '*_arch.json', '*_edges.*']
        
        import fnmatch
        artifacts = []
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                if any(fnmatch.fnmatch(file_path.name, p) for p in default_patterns):
                    artifacts.append(file_path.name)
        
        if artifacts:
            print(f"Found {len(artifacts)} artifact(s):")
            for f in sorted(artifacts):
                print(f"  {f}")
        else:
            print("No artifacts found")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
