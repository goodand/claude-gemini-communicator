#!/usr/bin/env python3
"""
Test Suite Tracer - Trace function calls during test execution

Runs test suites (pytest, npm test, jest) with runtime tracing and
archives test failures for later analysis.

Usage:
    python test_tracer.py pytest tests/
    python test_tracer.py npm test
    python test_tracer.py jest tests/
    
    # With archive on failure
    python test_tracer.py pytest tests/ --archive-dir ./failures
"""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional


@dataclass
class TestResult:
    """Individual test result"""
    name: str
    status: str  # passed, failed, error, skipped
    duration_ms: float = 0
    error_message: str = ""
    traceback: str = ""


@dataclass  
class TestSuiteResult:
    """Test suite execution result"""
    framework: str
    command: str
    executed_at: str
    duration_ms: float
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    tests: list[TestResult] = field(default_factory=list)
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    
    @property
    def success(self) -> bool:
        return self.failed == 0 and self.errors == 0
    
    def to_dict(self) -> dict:
        return {
            "framework": self.framework,
            "command": self.command,
            "executed_at": self.executed_at,
            "duration_ms": self.duration_ms,
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "errors": self.errors,
                "skipped": self.skipped,
                "success": self.success,
            },
            "tests": [asdict(t) for t in self.tests],
            "exit_code": self.exit_code,
        }


@dataclass
class TracedTestResult:
    """Combined trace and test result"""
    test_result: TestSuiteResult
    trace_result: Any  # TraceResult from tracer.py
    
    def to_dict(self) -> dict:
        return {
            "test": self.test_result.to_dict(),
            "trace": self.trace_result.to_dict() if self.trace_result else None,
        }


class PytestTracer:
    """Trace pytest execution"""
    
    def __init__(self, archive_dir: Optional[Path] = None):
        self.archive_dir = archive_dir
        
    def check_available(self) -> bool:
        try:
            result = subprocess.run(
                ["pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def run(self, test_path: str, extra_args: list[str] = None, with_trace: bool = False) -> TracedTestResult:
        """Run pytest with optional call tracing
        
        Args:
            test_path: Path to tests
            extra_args: Extra pytest arguments
            with_trace: If True, run with sys.settrace for call tracing (slower)
        """
        extra_args = extra_args or []
        
        if not self.check_available():
            return TracedTestResult(
                test_result=TestSuiteResult(
                    framework="pytest",
                    command=f"pytest {test_path}",
                    executed_at=datetime.now().isoformat(),
                    duration_ms=0,
                    exit_code=1,
                    stderr="pytest not installed"
                ),
                trace_result=None
            )
        
        # Build command - always use pytest directly
        cmd = ["pytest", test_path, "-v", "--tb=short"] + extra_args
        
        start_time = datetime.now()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Parse pytest output
            test_result = self._parse_pytest_output(
                test_path, result.stdout, result.stderr, 
                result.returncode, duration_ms
            )
            
            # Run separate trace if with_trace
            trace_result = None
            if with_trace:
                trace_result = self._run_trace(test_path, extra_args, duration_ms)
            
            # Archive if failed and archive_dir specified
            if not test_result.success and self.archive_dir:
                self._archive_failure(test_result, trace_result, result.stdout, result.stderr)
            
            return TracedTestResult(test_result=test_result, trace_result=trace_result)
            
        except subprocess.TimeoutExpired:
            return TracedTestResult(
                test_result=TestSuiteResult(
                    framework="pytest",
                    command=f"pytest {test_path}",
                    executed_at=datetime.now().isoformat(),
                    duration_ms=600000,
                    exit_code=124,
                    stderr="Test timeout (10 minutes)"
                ),
                trace_result=None
            )
    
    def _parse_pytest_output(self, test_path: str, stdout: str, stderr: str, 
                             exit_code: int, duration_ms: float) -> TestSuiteResult:
        """Parse pytest verbose output"""
        tests = []
        passed = failed = errors = skipped = 0
        
        # Parse test results from verbose output
        # Format: "test_file.py::test_name PASSED/FAILED/ERROR/SKIPPED"
        test_pattern = re.compile(r'^(.+::.+)\s+(PASSED|FAILED|ERROR|SKIPPED)', re.MULTILINE)
        
        for match in test_pattern.finditer(stdout):
            name = match.group(1)
            status = match.group(2).lower()
            
            tests.append(TestResult(
                name=name,
                status=status,
            ))
            
            if status == "passed":
                passed += 1
            elif status == "failed":
                failed += 1
            elif status == "error":
                errors += 1
            elif status == "skipped":
                skipped += 1
        
        # Extract summary line if present
        # Format: "X passed, Y failed, Z errors in N.NNs"
        summary_pattern = re.compile(r'(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+error|(\d+)\s+skipped')
        for match in summary_pattern.finditer(stdout):
            if match.group(1):
                passed = int(match.group(1))
            elif match.group(2):
                failed = int(match.group(2))
            elif match.group(3):
                errors = int(match.group(3))
            elif match.group(4):
                skipped = int(match.group(4))
        
        return TestSuiteResult(
            framework="pytest",
            command=f"pytest {test_path}",
            executed_at=datetime.now().isoformat(),
            duration_ms=duration_ms,
            total=passed + failed + errors + skipped,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            tests=tests,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
        )
    
    def _run_trace(self, test_path: str, extra_args: list[str], duration_ms: float) -> Any:
        """Run separate trace using sys.settrace based tracer
        
        Note: For pytest, full call tracing requires complex integration.
        This method provides basic support.
        """
        try:
            # Import local tracer
            import importlib.util
            tracer_path = Path(__file__).parent / "tracer.py"
            spec = importlib.util.spec_from_file_location("tracer", tracer_path)
            tracer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tracer_module)
            
            # For now, return None - full pytest tracing is complex
            # Users can run tracer.py separately on their test files
            return None
            
        except Exception as e:
            print(f"Trace error: {e}", file=sys.stderr)
            return None
    
    def _archive_failure(self, test_result: TestSuiteResult, trace_result: Any,
                         stdout: str, stderr: str) -> Path:
        """Archive test failure for later analysis"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"failure_{timestamp}.json"
        
        archive_data = {
            "archived_at": datetime.now().isoformat(),
            "test_result": test_result.to_dict(),
            "trace": trace_result.to_dict() if trace_result else None,
            "raw_output": {
                "stdout": stdout,
                "stderr": stderr,
            },
            "analysis_hints": {
                "failed_tests": [t.name for t in test_result.tests if t.status == "failed"],
                "error_tests": [t.name for t in test_result.tests if t.status == "error"],
            }
        }
        
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
        
        print(f"Failure archived to: {archive_file}", file=sys.stderr)
        return archive_file


class NpmTestTracer:
    """Trace npm test / jest execution"""
    
    def __init__(self, archive_dir: Optional[Path] = None):
        self.archive_dir = archive_dir
    
    def check_available(self) -> bool:
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def run(self, test_command: str = "test", extra_args: list[str] = None,
            project_dir: str = ".") -> TracedTestResult:
        """Run npm test with njstrace tracing"""
        extra_args = extra_args or []
        
        if not self.check_available():
            return TracedTestResult(
                test_result=TestSuiteResult(
                    framework="npm",
                    command=f"npm {test_command}",
                    executed_at=datetime.now().isoformat(),
                    duration_ms=0,
                    exit_code=1,
                    stderr="npm not installed"
                ),
                trace_result=None
            )
        
        # For npm test, we need to modify package.json or use a wrapper
        # For now, just run npm test and capture output
        cmd = ["npm", test_command] + extra_args
        
        start_time = datetime.now()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_dir,
                timeout=600
            )
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            test_result = self._parse_npm_output(
                test_command, result.stdout, result.stderr,
                result.returncode, duration_ms
            )
            
            # Archive if failed
            if not test_result.success and self.archive_dir:
                self._archive_failure(test_result, None, result.stdout, result.stderr)
            
            return TracedTestResult(test_result=test_result, trace_result=None)
            
        except subprocess.TimeoutExpired:
            return TracedTestResult(
                test_result=TestSuiteResult(
                    framework="npm",
                    command=f"npm {test_command}",
                    executed_at=datetime.now().isoformat(),
                    duration_ms=600000,
                    exit_code=124,
                    stderr="Test timeout"
                ),
                trace_result=None
            )
    
    def _parse_npm_output(self, command: str, stdout: str, stderr: str,
                          exit_code: int, duration_ms: float) -> TestSuiteResult:
        """Parse npm test / jest output"""
        passed = failed = 0
        tests = []
        
        # Jest output pattern: ✓ test name (Xms)  or  ✕ test name
        pass_pattern = re.compile(r'[✓✔]\s+(.+?)(?:\s+\((\d+)\s*m?s\))?$', re.MULTILINE)
        fail_pattern = re.compile(r'[✕✗]\s+(.+?)$', re.MULTILINE)
        
        for match in pass_pattern.finditer(stdout):
            tests.append(TestResult(
                name=match.group(1).strip(),
                status="passed",
                duration_ms=float(match.group(2)) if match.group(2) else 0
            ))
            passed += 1
        
        for match in fail_pattern.finditer(stdout):
            tests.append(TestResult(
                name=match.group(1).strip(),
                status="failed"
            ))
            failed += 1
        
        # Jest summary: Tests: X passed, Y failed, Z total
        summary_match = re.search(r'Tests:\s+(\d+)\s+passed.*?(\d+)\s+failed', stdout)
        if summary_match:
            passed = int(summary_match.group(1))
            failed = int(summary_match.group(2))
        
        return TestSuiteResult(
            framework="npm/jest",
            command=f"npm {command}",
            executed_at=datetime.now().isoformat(),
            duration_ms=duration_ms,
            total=passed + failed,
            passed=passed,
            failed=failed,
            tests=tests,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
        )
    
    def _archive_failure(self, test_result: TestSuiteResult, trace_result: Any,
                         stdout: str, stderr: str) -> Path:
        """Archive test failure"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"failure_{timestamp}.json"
        
        archive_data = {
            "archived_at": datetime.now().isoformat(),
            "test_result": test_result.to_dict(),
            "trace": trace_result.to_dict() if trace_result else None,
            "raw_output": {
                "stdout": stdout,
                "stderr": stderr,
            },
        }
        
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
        
        print(f"Failure archived to: {archive_file}", file=sys.stderr)
        return archive_file


def main():
    parser = argparse.ArgumentParser(
        description="Test Suite Tracer - Trace function calls during test execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python test_tracer.py pytest tests/
    python test_tracer.py pytest tests/ --archive-dir ./failures
    python test_tracer.py npm test --project-dir ./my-app
    python test_tracer.py jest tests/ --archive-dir ./failures
    
Archive Format:
    When tests fail, a JSON file is created with:
    - Test results (passed/failed/errors)
    - Function call trace (if available)
    - Raw stdout/stderr for debugging
    - Analysis hints (failed test names)
        """
    )
    
    parser.add_argument("framework", choices=["pytest", "npm", "jest"],
                        help="Test framework to use")
    parser.add_argument("target", nargs="?", default=".",
                        help="Test target (path for pytest/jest, command for npm)")
    parser.add_argument("--args", "-a", default="",
                        help="Extra arguments to pass to test framework")
    parser.add_argument("--archive-dir", type=Path,
                        help="Directory to archive failures (enables failure archiving)")
    parser.add_argument("--project-dir", default=".",
                        help="Project directory for npm (default: current)")
    parser.add_argument("--with-trace", action="store_true",
                        help="Enable function call tracing (slower)")
    parser.add_argument("--format", "-f",
                        choices=["json", "summary", "trace-only"],
                        default="json",
                        help="Output format")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    extra_args = args.args.split() if args.args else []
    
    # Select tracer
    if args.framework == "pytest":
        tracer = PytestTracer(archive_dir=args.archive_dir)
        result = tracer.run(args.target, extra_args, with_trace=args.with_trace)
    elif args.framework in ["npm", "jest"]:
        tracer = NpmTestTracer(archive_dir=args.archive_dir)
        if args.framework == "jest":
            result = tracer.run("test", ["--", "--testPathPattern", args.target] + extra_args,
                               args.project_dir)
        else:
            result = tracer.run(args.target, extra_args, args.project_dir)
    
    # Format output
    if args.format == "json":
        output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    elif args.format == "summary":
        tr = result.test_result
        status = "✓ PASSED" if tr.success else "✗ FAILED"
        output = f"""Test Suite: {tr.framework}
Command: {tr.command}
Status: {status}
Duration: {tr.duration_ms:.0f}ms

Summary:
  Total:   {tr.total}
  Passed:  {tr.passed}
  Failed:  {tr.failed}
  Errors:  {tr.errors}
  Skipped: {tr.skipped}
"""
        if tr.failed > 0 or tr.errors > 0:
            output += "\nFailed Tests:\n"
            for t in tr.tests:
                if t.status in ("failed", "error"):
                    output += f"  - {t.name}\n"
    elif args.format == "trace-only":
        if result.trace_result:
            output = json.dumps(result.trace_result.to_dict(), indent=2, ensure_ascii=False)
        else:
            output = '{"error": "No trace data available"}'
    
    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)
    
    # Exit with test exit code
    return result.test_result.exit_code


if __name__ == "__main__":
    sys.exit(main())
