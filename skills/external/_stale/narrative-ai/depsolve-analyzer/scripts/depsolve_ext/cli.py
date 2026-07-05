#!/usr/bin/env python3
"""
depsolve_ext/cli.py
===================
depsolve ÃƒÂ­Ã¢â€žÂ¢Ã¢â‚¬Â¢ÃƒÂ¬Ã…Â¾Ã‚Â¥ ÃƒÂ«Ã‚ÂªÃ‚Â¨ÃƒÂ«Ã¢â‚¬Å“Ã‹â€  CLI

Usage:
    python -m depsolve_ext analyze ./my-project
    python -m depsolve_ext analyze . --verify --verbose
    python -m depsolve_ext phantoms .
    python -m depsolve_ext graph .
    python -m depsolve_ext imports ./src/App.tsx
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Set

from .analyzer import DependencyAnalyzer, analyze
from .graph import DependencyGraph
from .extensions import (
    ImportExtractor, PhantomDetector, RuntimeVerifier, EcosystemDetector
)
from .reporters import ConsoleReporter, MarkdownReporter, JsonReporter
from .models import Severity

# Override ëª¨ë“ˆ (lazy import for backward compatibility)
def _get_override_modules():
    from .override_engine import OverrideConfig, OverrideApplicator, create_initial_overrides
    from .override_verifier import (
        OverrideVerifier, update_overrides_with_verification, generate_verification_report
    )
    return {
        'OverrideConfig': OverrideConfig,
        'OverrideApplicator': OverrideApplicator,
        'create_initial_overrides': create_initial_overrides,
        'OverrideVerifier': OverrideVerifier,
        'update_overrides_with_verification': update_overrides_with_verification,
        'generate_verification_report': generate_verification_report,
    }


def load_npm_deps(project_path: Path) -> tuple[Set[str], Set[str]]:
    """package.jsonÃƒÂ¬Ã¢â‚¬â€Ã‚ÂÃƒÂ¬Ã¢â‚¬Å¾Ã…â€œ ÃƒÂ¬Ã‚ÂÃ‹Å“ÃƒÂ¬Ã‚Â¡Ã‚Â´ÃƒÂ¬Ã¢â‚¬Å¾Ã‚Â± ÃƒÂ«Ã‚Â¡Ã…â€œÃƒÂ«Ã¢â‚¬Å“Ã…â€œ"""
    pkg_json = project_path / "package.json"
    if not pkg_json.exists():
        return set(), set()
    
    try:
        with open(pkg_json) as f:
            data = json.load(f)
        return (
            set(data.get("dependencies", {}).keys()),
            set(data.get("devDependencies", {}).keys())
        )
    except Exception:
        return set(), set()


def print_header(text: str):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print('=' * 60)


def print_section(text: str):
    print(f"\n--- {text} ---")


# =============================================================================
# Commands
# =============================================================================

def cmd_analyze(args):
    """ÃƒÂ­Ã¢â‚¬ÂÃ¢â‚¬Å¾ÃƒÂ«Ã‚Â¡Ã…â€œÃƒÂ¬Ã‚Â Ã‚ÂÃƒÂ­Ã…Â Ã‚Â¸ ÃƒÂ¬Ã‚Â Ã¢â‚¬Å¾ÃƒÂ¬Ã‚Â²Ã‚Â´ ÃƒÂ«Ã‚Â¶Ã¢â‚¬Å¾ÃƒÂ¬Ã¢â‚¬Å¾Ã‚Â"""
    project = Path(args.path).resolve()
    
    if not project.exists():
        print(f"Error: Path not found: {project}", file=sys.stderr)
        return 1
    
    # ÃƒÂ«Ã‚Â¶Ã¢â‚¬Å¾ÃƒÂ¬Ã¢â‚¬Å¾Ã‚Â ÃƒÂ¬Ã¢â‚¬Â¹Ã‚Â¤ÃƒÂ­Ã¢â‚¬â€œÃ¢â‚¬Â°
    result = analyze(
        project_path=str(project),
        verify=args.verify,
        include_dev=not args.no_dev,
        max_nodes=args.max_nodes
    )
    
    # ÃƒÂ¬Ã‚Â¶Ã…â€œÃƒÂ«Ã‚Â Ã‚Â¥ ÃƒÂ­Ã‹Å“Ã¢â‚¬Â¢ÃƒÂ¬Ã¢â‚¬Â¹Ã‚Â ÃƒÂ¬Ã¢â‚¬Å¾Ã‚Â ÃƒÂ­Ã†â€™Ã‚Â
    if args.format == "json":
        reporter = JsonReporter()
    elif args.format == "markdown":
        reporter = MarkdownReporter()
    else:
        reporter = ConsoleReporter(
            use_color=not args.no_color,
            verbose=args.verbose
        )
    
    reporter.report(result)
    
    # ÃƒÂ¬Ã‚Â¢Ã¢â‚¬Â¦ÃƒÂ«Ã‚Â£Ã…â€™ ÃƒÂ¬Ã‚Â½Ã¢â‚¬ÂÃƒÂ«Ã¢â‚¬Å“Ã…â€œ: HIGH ÃƒÂ¬Ã‚ÂÃ‚Â´ÃƒÂ¬Ã†â€™Ã‚Â ÃƒÂ¬Ã‚ÂÃ‚Â´ÃƒÂ¬Ã…Â Ã‹â€ ÃƒÂªÃ‚Â°Ã¢â€šÂ¬ ÃƒÂ¬Ã…Â¾Ã‹â€ ÃƒÂ¬Ã…â€œÃ‚Â¼ÃƒÂ«Ã‚Â©Ã‚Â´ 1
    has_high = any(
        i.severity in (Severity.CRITICAL, Severity.HIGH)
        for i in result.issues
    )
    return 1 if has_high else 0


def cmd_phantoms(args):
    """Phantom ÃƒÂ¬Ã‚ÂÃ‹Å“ÃƒÂ¬Ã‚Â¡Ã‚Â´ÃƒÂ¬Ã¢â‚¬Å¾Ã‚Â± ÃƒÂ­Ã†â€™Ã‚ÂÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬"""
    project = Path(args.path).resolve()
    
    if not project.exists():
        print(f"Error: Path not found: {project}", file=sys.stderr)
        return 1
    
    deps, dev_deps = load_npm_deps(project)
    
    if not deps and not dev_deps:
        print("No package.json found or no dependencies declared")
        return 0
    
    print_header(f"Phantom Detection: {project}")
    print(f"  Dependencies: {len(deps)}")
    print(f"  DevDependencies: {len(dev_deps)}")
    
    detector = PhantomDetector(
        project_path=project,
        deps=deps,
        dev_deps=dev_deps,
        verify=args.verify
    )
    
    phantoms = detector.detect()
    
    reporter = ConsoleReporter(use_color=not args.no_color)
    reporter.report_phantoms(phantoms)
    
    real_phantoms = [p for p in phantoms if p.is_phantom]
    return 1 if real_phantoms else 0


def cmd_graph(args):
    """ÃƒÂ¬Ã‚ÂÃ‹Å“ÃƒÂ¬Ã‚Â¡Ã‚Â´ÃƒÂ¬Ã¢â‚¬Å¾Ã‚Â± ÃƒÂªÃ‚Â·Ã‚Â¸ÃƒÂ«Ã…Â¾Ã‹Å“ÃƒÂ­Ã¢â‚¬ÂÃ¢â‚¬Å¾ ÃƒÂ«Ã‚Â¶Ã¢â‚¬Å¾ÃƒÂ¬Ã¢â‚¬Å¾Ã‚Â"""
    project = Path(args.path).resolve()
    
    if not project.exists():
        print(f"Error: Path not found: {project}", file=sys.stderr)
        return 1
    
    analyzer = DependencyAnalyzer(project, verify_runtime=args.verify)
    analyzer._detect_ecosystem()
    analyzer._load_manifest()
    analyzer._build_graph()
    
    graph = analyzer.graph
    
    print_header(f"Graph Analysis: {project}")
    print(f"  Nodes: {graph.node_count}")
    print(f"  Edges: {graph.edge_count}")
    
    # ÃƒÂ¬Ã‹â€ Ã…â€œÃƒÂ­Ã¢â€žÂ¢Ã‹Å“ ÃƒÂ­Ã†â€™Ã‚ÂÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬
    cycles = graph.find_cycles()
    if cycles:
        print_section(f"Circular Dependencies ({len(cycles)})")
        for cycle in cycles[:10]:
            print(f"  ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢ {' ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ '.join(cycle.path)}")
    
    # ÃƒÂ«Ã¢â‚¬Â¹Ã‚Â¤ÃƒÂ¬Ã‚ÂÃ‚Â´ÃƒÂ¬Ã¢â‚¬Â¢Ã¢â‚¬Å¾ÃƒÂ«Ã‚ÂªÃ‚Â¬ÃƒÂ«Ã¢â‚¬Å“Ã…â€œ ÃƒÂ­Ã†â€™Ã‚ÂÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬
    diamonds = graph.find_diamonds()
    conflicts = [d for d in diamonds if d.has_version_conflict]
    
    if diamonds:
        print_section(f"Diamond Dependencies ({len(diamonds)})")
        print(f"  With version conflicts: {len(conflicts)}")
        
        for d in conflicts[:5]:
            print(f"\n  {d.top}")
            print(f"    ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ {d.left} ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ {d.bottom}@{d.left_version}")
            print(f"    ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ {d.right} ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ {d.bottom}@{d.right_version}")
    
    # Mermaid ÃƒÂ¬Ã‚Â¶Ã…â€œÃƒÂ«Ã‚Â Ã‚Â¥
    if args.mermaid:
        print_section("Mermaid Diagram")
        print()
        print("```mermaid")
        print(graph.to_mermaid(max_nodes=args.max_nodes))
        print("```")
    
    print()
    return 0


def cmd_imports(args):
    """ÃƒÂ­Ã…â€™Ã…â€™ÃƒÂ¬Ã‚ÂÃ‚Â¼ÃƒÂ¬Ã¢â‚¬â€Ã‚ÂÃƒÂ¬Ã¢â‚¬Å¾Ã…â€œ import ÃƒÂ¬Ã‚Â¶Ã¢â‚¬ÂÃƒÂ¬Ã‚Â¶Ã…â€œ"""
    path = Path(args.file).resolve()
    
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        return 1
    
    extractor = ImportExtractor()
    imports = extractor.extract_file(path)
    
    print_header(f"Imports: {path.name}")
    print(f"Total: {len(imports)}")
    
    # ÃƒÂ­Ã†â€™Ã¢â€šÂ¬ÃƒÂ¬Ã…Â¾Ã¢â‚¬Â¦ÃƒÂ«Ã‚Â³Ã¢â‚¬Å¾ ÃƒÂªÃ‚Â·Ã‚Â¸ÃƒÂ«Ã‚Â£Ã‚Â¹ÃƒÂ­Ã¢â€žÂ¢Ã¢â‚¬Â
    by_type = {}
    for imp in imports:
        t = imp.import_type.value
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(imp)
    
    for imp_type, imps in sorted(by_type.items()):
        print(f"\n[{imp_type}] ({len(imps)})")
        for imp in imps:
            extra = " (type-only)" if imp.is_type_only else ""
            print(f"  ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢ {imp.package}{extra}")
            if args.verbose:
                print(f"    {imp.module} (line {imp.line})")
    
    if args.json:
        print("\n--- JSON ---")
        data = [{"package": i.package, "type": i.import_type.value,
                 "line": i.line, "type_only": i.is_type_only} for i in imports]
        print(json.dumps(data, indent=2))
    
    print()
    return 0


def cmd_ecosystem(args):
    """ÃƒÂ¬Ã†â€™Ã‚ÂÃƒÂ­Ã†â€™Ã…â€œÃƒÂªÃ‚Â³Ã¢â‚¬Å¾ ÃƒÂªÃ‚Â°Ã‚ÂÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬"""
    project = Path(args.path).resolve()
    
    if not project.exists():
        print(f"Error: Path not found: {project}", file=sys.stderr)
        return 1
    
    print_header(f"Ecosystem Detection: {project}")
    
    # ÃƒÂ«Ã¢â‚¬Å¡Ã‚Â´ÃƒÂ¬Ã…Â¾Ã‚Â¥ ÃƒÂªÃ‚Â°Ã‚ÂÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬
    detected = EcosystemDetector.detect(project)
    
    # npm/pip ÃƒÂ¬Ã‚Â¶Ã¢â‚¬ÂÃƒÂªÃ‚Â°Ã¢â€šÂ¬ ÃƒÂªÃ‚Â°Ã‚ÂÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬
    if (project / "package.json").exists():
        print("\n[NPM]")
        deps, dev_deps = load_npm_deps(project)
        print(f"  Dependencies: {len(deps)}")
        print(f"  DevDependencies: {len(dev_deps)}")
    
    if (project / "requirements.txt").exists():
        print("\n[PIP]")
        print("  requirements.txt detected")
    
    for name, adapter in detected:
        print(f"\n[{name.upper()}]")
        try:
            info = adapter.get_info()
            print(f"  Name: {info.name}")
            print(f"  Version: {info.version}")
            print(f"  Dependencies: {len(info.dependencies)}")
            for dep, ver in list(info.dependencies.items())[:5]:
                print(f"    ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢ {dep}: {ver}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print()
    return 0


def cmd_multi_version(args):
    """ÃƒÂ«Ã¢â‚¬Â¹Ã‚Â¤ÃƒÂ¬Ã‚Â¤Ã¢â‚¬Ëœ ÃƒÂ«Ã‚Â²Ã¢â‚¬Å¾ÃƒÂ¬Ã‚Â Ã¢â‚¬Å¾ ÃƒÂ­Ã…â€™Ã‚Â¨ÃƒÂ­Ã¢â‚¬Å¡Ã‚Â¤ÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬ ÃƒÂ­Ã†â€™Ã‚ÂÃƒÂ¬Ã‚Â§Ã¢â€šÂ¬"""
    project = Path(args.path).resolve()
    
    print_header(f"Multi-Version Detection: {project}")
    
    verifier = RuntimeVerifier(project)
    
    if not verifier.npm_available:
        print("  Error: npm not available", file=sys.stderr)
        return 1
    
    multi = verifier.get_multi_versions()
    
    if not multi:
        print("  ÃƒÂ¢Ã…â€œÃ¢â‚¬Å“ No multiple version packages found")
        return 0
    
    print(f"  Found {len(multi)} packages with multiple versions:\n")
    
    for m in multi:
        print(f"  ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢ {m.package}")
        print(f"    Versions: {', '.join(m.versions)}")
        if args.verbose:
            for path in m.paths[:3]:
                print(f"    Path: {' ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ '.join(path)}")
    
    print()
    return 0


def cmd_verify_overrides(args):
    """Override ê²€ì¦"""
    project = Path(args.path).resolve()
    
    if not project.exists():
        print(f"Error: Path not found: {project}", file=sys.stderr)
        return 1
    
    override_modules = _get_override_modules()
    OverrideConfig = override_modules['OverrideConfig']
    OverrideVerifier = override_modules['OverrideVerifier']
    update_overrides_with_verification = override_modules['update_overrides_with_verification']
    generate_verification_report = override_modules['generate_verification_report']
    
    override_file = project / ".depsolve" / "overrides.yaml"
    if not override_file.exists():
        print(f"Error: No overrides.yaml found at {override_file}", file=sys.stderr)
        print("Run 'depsolve_ext init-overrides' first.", file=sys.stderr)
        return 1
    
    print_header("Override Verification")
    print(f"  Project: {project}")
    print(f"  Override file: {override_file}")
    
    # ì„¤ì • ë¡œë“œ (ê²€ì¦ ëŒ€ìƒì´ë¯€ë¡œ ë¯¸ê²€ì¦ í•­ëª©ë„ í¬í•¨)
    config = OverrideConfig.load(project, include_unverified=True)
    
    if not config.has_any_overrides():
        print("\n  No overrides to verify.")
        return 0
    
    # ê²€ì¦ ì‹¤í–‰
    print_section("Running Verification")
    verifier = OverrideVerifier(project)
    results = verifier.verify_all(config)
    
    # ê²°ê³¼ ì¶œë ¥
    success = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"\n  Total: {len(results)} entries")
    print(f"  âœ“ Passed: {len(success)}")
    print(f"  âœ— Failed: {len(failed)}")
    
    if args.verbose:
        if success:
            print_section("Verified")
            for r in success:
                print(f"  âœ“ {r.entry.key} â†’ {r.entry.value}")
                if r.details:
                    for k, v in r.details.items():
                        print(f"      {k}: {v}")
        
        if failed:
            print_section("Failed")
            for r in failed:
                print(f"  âœ— {r.entry.key}")
                print(f"      Error: {r.error}")
    
    # overrides.yaml ì—…ë°ì´íŠ¸
    success_count, fail_count = update_overrides_with_verification(project, results)
    
    print_section("Summary")
    print(f"  Updated overrides.yaml: {success_count} verified, {fail_count} failed")
    
    # ë¦¬í¬íŠ¸ ìƒì„± (ì˜µì…˜)
    if args.report:
        report = generate_verification_report(results)
        report_path = project / ".depsolve" / "verification_report.md"
        report_path.write_text(report)
        print(f"  Report saved: {report_path}")
    
    print()
    return 1 if failed else 0


def cmd_init_overrides(args):
    """Override í…œí”Œë¦¿ ì´ˆê¸°í™”"""
    project = Path(args.path).resolve()
    
    if not project.exists():
        print(f"Error: Path not found: {project}", file=sys.stderr)
        return 1
    
    override_modules = _get_override_modules()
    create_initial_overrides = override_modules['create_initial_overrides']
    
    override_dir = project / ".depsolve"
    override_file = override_dir / "overrides.yaml"
    
    if override_file.exists() and not args.force:
        print(f"Error: {override_file} already exists.", file=sys.stderr)
        print("Use --force to overwrite.", file=sys.stderr)
        return 1
    
    override_dir.mkdir(parents=True, exist_ok=True)
    
    # í…œí”Œë¦¿ ìƒì„±
    config = create_initial_overrides(project)
    config.save(project)
    
    print_header("Override Initialization")
    print(f"  Created: {override_file}")
    print()
    print("  Next steps:")
    print("  1. Edit .depsolve/overrides.yaml to add your overrides")
    print("  2. Run 'depsolve_ext verify-overrides .' to validate")
    print("  3. Run 'depsolve_ext analyze .' to apply overrides")
    print()
    
    return 0


def cmd_apply_overrides(args):
    """Override ì ìš© ê²°ê³¼ ë¯¸ë¦¬ë³´ê¸°"""
    project = Path(args.path).resolve()
    
    if not project.exists():
        print(f"Error: Path not found: {project}", file=sys.stderr)
        return 1
    
    override_modules = _get_override_modules()
    OverrideConfig = override_modules['OverrideConfig']
    OverrideApplicator = override_modules['OverrideApplicator']
    
    override_file = project / ".depsolve" / "overrides.yaml"
    if not override_file.exists():
        print(f"Error: No overrides.yaml found at {override_file}", file=sys.stderr)
        return 1
    
    print_header("Override Application Preview")
    print(f"  Project: {project}")
    
    # Phantom íƒì§€
    from .extensions import load_hybrid_manifest
    manifest = load_hybrid_manifest(project)
    
    detector = PhantomDetector(
        project,
        js_deps=manifest.js_deps,
        js_dev_deps=manifest.js_dev_deps,
        py_deps=manifest.py_deps,
        py_dev_deps=manifest.py_dev_deps,
        verify=args.verify
    )
    
    phantoms = detector.detect()
    original_count = len([p for p in phantoms if p.is_phantom])
    
    print_section("Before Override")
    print(f"  Phantoms detected: {original_count}")
    
    # Override ì ìš©
    config = OverrideConfig.load(project)
    applicator = OverrideApplicator(config)
    modified = applicator.apply(phantoms)
    
    final_count = len([p for p in modified if p.is_phantom])
    
    print_section("After Override")
    print(f"  Phantoms remaining: {final_count}")
    print(f"  Resolved: {original_count - final_count}")
    
    stats = applicator.stats
    print_section("Override Stats")
    print(f"  Typo corrected: {stats['typo_corrected']}")
    print(f"  Alias resolved: {stats['alias_resolved']}")
    print(f"  Internal marked: {stats['internal_marked']}")
    print(f"  Ignored: {stats['ignored']}")
    
    if args.verbose:
        # ë³€ê²½ëœ í•­ëª© ìƒì„¸
        print_section("Changed Items")
        for p in modified:
            if "[Override]" in p.reason:
                print(f"  â€¢ {p.package}: {p.reason}")
    
    print()
    return 0

# =============================================================================
# Main
# =============================================================================

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='depsolve_ext',
        description='depsolve í†µí•© ì˜ì¡´ì„± ë¶„ì„ê¸°'
    )
    parser.add_argument('--version', action='version', version='0.3.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # analyze
    p_analyze = subparsers.add_parser('analyze', help='í”„ë¡œì íŠ¸ ì „ì²´ ë¶„ì„')
    p_analyze.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    p_analyze.add_argument('--verify', '-v', action='store_true', help='ëŸ°íƒ€ìž„ ê²€ì¦')
    p_analyze.add_argument('--verbose', action='store_true', help='ìƒì„¸ ì¶œë ¥')
    p_analyze.add_argument('--no-dev', action='store_true', help='devDependencies ì œì™¸')
    p_analyze.add_argument('--no-color', action='store_true', help='ìƒ‰ìƒ ë¹„í™œì„±í™”')
    p_analyze.add_argument('--format', '-f', choices=['console', 'json', 'markdown'],
                          default='console', help='ì¶œë ¥ í˜•ì‹')
    p_analyze.add_argument('--max-nodes', type=int, default=50, help='Mermaid ìµœëŒ€ ë…¸ë“œ ìˆ˜')
    
    # phantoms
    p_phantoms = subparsers.add_parser('phantoms', help='Phantom ì˜ì¡´ì„± íƒì§€')
    p_phantoms.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    p_phantoms.add_argument('--verify', '-v', action='store_true', help='ëŸ°íƒ€ìž„ ê²€ì¦')
    p_phantoms.add_argument('--no-color', action='store_true')
    
    # graph
    p_graph = subparsers.add_parser('graph', help='ì˜ì¡´ì„± ê·¸ëž˜í”„ ë¶„ì„')
    p_graph.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    p_graph.add_argument('--verify', '-v', action='store_true')
    p_graph.add_argument('--mermaid', '-m', action='store_true', help='Mermaid ë‹¤ì´ì–´ê·¸ëž¨ ì¶œë ¥')
    p_graph.add_argument('--max-nodes', type=int, default=50, help='ìµœëŒ€ ë…¸ë“œ ìˆ˜')
    
    # imports
    p_imports = subparsers.add_parser('imports', help='íŒŒì¼ import ì¶”ì¶œ')
    p_imports.add_argument('file', help='íŒŒì¼ ê²½ë¡œ')
    p_imports.add_argument('--json', action='store_true', help='JSON ì¶œë ¥')
    p_imports.add_argument('--verbose', action='store_true')
    
    # ecosystem
    p_eco = subparsers.add_parser('ecosystem', help='ìƒíƒœê³„ ê°ì§€')
    p_eco.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    
    # multi-version
    p_multi = subparsers.add_parser('multi-version', help='ë‹¤ì¤‘ ë²„ì „ íƒì§€')
    p_multi.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    p_multi.add_argument('--verbose', action='store_true')
    
    # verify-overrides
    p_verify_override = subparsers.add_parser('verify-overrides', help='Override ê²€ì¦')
    p_verify_override.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    p_verify_override.add_argument('--verbose', action='store_true', help='ìƒì„¸ ì¶œë ¥')
    p_verify_override.add_argument('--report', action='store_true', help='ê²€ì¦ ë¦¬í¬íŠ¸ ìƒì„±')
    
    # init-overrides
    p_init_override = subparsers.add_parser('init-overrides', help='Override í…œí”Œë¦¿ ì´ˆê¸°í™”')
    p_init_override.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    p_init_override.add_argument('--force', action='store_true', help='ê¸°ì¡´ íŒŒì¼ ë®ì–´ì“°ê¸°')
    
    # apply-overrides
    p_apply_override = subparsers.add_parser('apply-overrides', help='Override ì ìš© ë¯¸ë¦¬ë³´ê¸°')
    p_apply_override.add_argument('path', help='í”„ë¡œì íŠ¸ ê²½ë¡œ')
    p_apply_override.add_argument('--verify', '-v', action='store_true', help='ëŸ°íƒ€ìž„ ê²€ì¦')
    p_apply_override.add_argument('--verbose', action='store_true', help='ìƒì„¸ ì¶œë ¥')
    
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        'analyze': cmd_analyze,
        'phantoms': cmd_phantoms,
        'graph': cmd_graph,
        'imports': cmd_imports,
        'ecosystem': cmd_ecosystem,
        'multi-version': cmd_multi_version,
        'verify-overrides': cmd_verify_overrides,
        'init-overrides': cmd_init_overrides,
        'apply-overrides': cmd_apply_overrides,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
