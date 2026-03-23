#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent / 'analyze_codebase.py'
SPEC = importlib.util.spec_from_file_location('analyze_codebase', SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AnalyzeCodebaseTests(unittest.TestCase):
    def test_build_summary_supports_custom_exclude_dir_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'main.py').write_text('import os\n', encoding='utf-8')
            (root / 'logs').mkdir()
            (root / 'logs' / 'noise.py').write_text('import sys\n', encoding='utf-8')

            summary = MODULE.build_summary(
                root,
                top_n_ext=10,
                excluded_dir_names=MODULE.DEFAULT_EXCLUDES | {'logs'},
            )

            self.assertEqual(summary['total_files'], 1)
            self.assertEqual(summary['python_files'], 1)
            self.assertEqual(summary['total_import_statements'], 1)
            self.assertEqual(summary['top_level_file_counts'], {'src': 1})
            self.assertIn('logs', summary['excluded_dir_names'])

    def test_cli_output_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'pkg').mkdir()
            (root / 'pkg' / 'app.py').write_text('from pathlib import Path\n', encoding='utf-8')
            out = root / 'artifacts' / 'nested' / 'summary.json'

            proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(root), '--output', str(out)],
                capture_output=True,
                text=True,
            )

            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertTrue(out.exists())
            data = json.loads(out.read_text(encoding='utf-8'))
            self.assertEqual(data['repo_root'], str(root.resolve()))
            self.assertEqual(proc.stdout, '')

    def test_build_summary_reports_python_parse_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'good.py').write_text('import os\n', encoding='utf-8')
            (root / 'src' / 'bad.py').write_text('def broken(:\n', encoding='utf-8')

            summary = MODULE.build_summary(root, top_n_ext=10)

            self.assertEqual(summary['python_files'], 2)
            self.assertEqual(summary['total_import_statements'], 1)
            self.assertEqual(summary['python_parse_failure_count'], 1)
            self.assertEqual(summary['python_parse_failure_files'], ['src/bad.py'])

    def test_cli_include_and_exclude_top_level_controls_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('import os\n', encoding='utf-8')
            (root / 'tests').mkdir()
            (root / 'tests' / 'test_app.py').write_text('import unittest\n', encoding='utf-8')
            (root / 'plans').mkdir()
            (root / 'plans' / 'note.md').write_text('note\n', encoding='utf-8')

            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    str(root),
                    '--include-top-level',
                    'src',
                    '--include-top-level',
                    'tests',
                    '--exclude-top-level',
                    'tests',
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data['top_level_file_counts'], {'src': 1})
            self.assertEqual(data['total_files'], 1)
            self.assertEqual(data['included_top_level_names'], ['src', 'tests'])
            self.assertEqual(data['excluded_top_level_names'], ['tests'])


class CanonicalGraphTests(unittest.TestCase):
    """Tests derived from spec Acceptance Criteria + implementation request Done Definition."""

    def _make_fixture(self, root: Path) -> None:
        """Common fixture: src/app.py imports src/core.py, config.yaml, README.md, notes.txt."""
        (root / 'src').mkdir()
        (root / 'src' / 'app.py').write_text(
            'import os\nfrom src import core\n', encoding='utf-8',
        )
        (root / 'src' / 'core.py').write_text('import json\n', encoding='utf-8')
        (root / 'config.yaml').write_text('key: value\n', encoding='utf-8')
        (root / 'README.md').write_text('# readme\n', encoding='utf-8')
        (root / 'notes.txt').write_text('note\n', encoding='utf-8')

    # --- Step 2c: graph dict contract ---

    def test_canonical_graph_required_top_level_fields(self) -> None:
        """Spec Acceptance: canonical output set required top-level fields."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, _sidecar = MODULE.build_canonical_graph(root)
            required = {'graph_id', 'generated_at', 'source_scope', 'graph_kind', 'schema_version', 'nodes', 'edges'}
            self.assertTrue(required <= set(graph), f'missing: {required - set(graph)}')

    def test_nodes_have_required_fields(self) -> None:
        """Spec Acceptance: Node Schema required fields id, kind, name."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, _ = MODULE.build_canonical_graph(root)
            for node in graph['nodes']:
                self.assertIn('id', node)
                self.assertIn('kind', node)
                self.assertIn('name', node)

    def test_edges_have_required_fields(self) -> None:
        """Spec Acceptance: Edge Schema required fields src, dst, rel."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, _ = MODULE.build_canonical_graph(root)
            for edge in graph['edges']:
                self.assertIn('src', edge)
                self.assertIn('dst', edge)
                self.assertIn('rel', edge)

    # --- Step 3: artifact output contract ---

    def test_graph_meta_required_fields(self) -> None:
        """Done Definition: graph_meta.json minimum required fields."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, sidecar = MODULE.build_canonical_graph(root)
            out_dir = Path(tmp) / 'out'
            meta = MODULE.write_canonical_artifacts(graph, sidecar, out_dir)
            required = {
                'graph_id', 'schema_version', 'generated_at', 'source_scope',
                'graph_kind', 'artifact_paths', 'trace_id', 'artifact_location',
            }
            self.assertTrue(required <= set(meta), f'missing: {required - set(meta)}')

    def test_artifact_paths_point_to_real_files(self) -> None:
        """Done Definition: graph_meta.artifact_paths point to canonical triple."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, sidecar = MODULE.build_canonical_graph(root)
            out_dir = Path(tmp) / 'out'
            meta = MODULE.write_canonical_artifacts(graph, sidecar, out_dir)
            for name, rel_path in meta['artifact_paths'].items():
                full = out_dir / rel_path
                self.assertTrue(full.exists(), f'{name} -> {full} does not exist')

    def test_nodes_jsonl_is_newline_delimited(self) -> None:
        """Required Check: nodes.jsonl is newline-delimited JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, sidecar = MODULE.build_canonical_graph(root)
            out_dir = Path(tmp) / 'out'
            MODULE.write_canonical_artifacts(graph, sidecar, out_dir)
            lines = (out_dir / 'nodes.jsonl').read_text(encoding='utf-8').strip().split('\n')
            self.assertGreater(len(lines), 0)
            for line in lines:
                record = json.loads(line)
                self.assertIn('id', record)

    def test_edges_jsonl_is_newline_delimited(self) -> None:
        """Required Check: edges.jsonl is newline-delimited JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, sidecar = MODULE.build_canonical_graph(root)
            out_dir = Path(tmp) / 'out'
            MODULE.write_canonical_artifacts(graph, sidecar, out_dir)
            content = (out_dir / 'edges.jsonl').read_text(encoding='utf-8').strip()
            if content:
                for line in content.split('\n'):
                    record = json.loads(line)
                    self.assertIn('src', record)

    # --- Sidecar evidence contract ---

    def test_sidecar_routing_path_exists(self) -> None:
        """Done Definition: sidecar routing path exists in code even if empty."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('import nonexistent_module\n', encoding='utf-8')
            _graph, sidecar = MODULE.build_canonical_graph(root)
            self.assertGreater(len(sidecar), 0)
            self.assertEqual(sidecar[0]['evidence_kind'], 'unresolved')

    def test_sidecar_evidence_required_fields(self) -> None:
        """Spec Acceptance: Sidecar Evidence required fields."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('import nonexistent_module\n', encoding='utf-8')
            _graph, sidecar = MODULE.build_canonical_graph(root)
            required = {
                'evidence_kind', 'subject_anchor', 'summary',
                'source_path', 'evidence_path', 'reason', 'confidence',
            }
            for record in sidecar:
                self.assertTrue(required <= set(record), f'missing: {required - set(record)}')

    # --- merged_graph contract ---

    def test_merged_graph_kind_allowed(self) -> None:
        """Done Definition: merged_graph is an allowed graph_kind."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, _ = MODULE.build_canonical_graph(root, graph_kind='merged_graph')
            self.assertEqual(graph['graph_kind'], 'merged_graph')

    def test_invalid_graph_kind_rejected(self) -> None:
        """Guardrail: invalid graph_kind must raise ValueError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            with self.assertRaises(ValueError):
                MODULE.build_canonical_graph(root, graph_kind='invalid')

    # --- Node scope contract ---

    def test_doc_only_files_excluded(self) -> None:
        """Implementation decision: .md, .txt excluded from graph nodes."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, _ = MODULE.build_canonical_graph(root)
            node_ids = {n['id'] for n in graph['nodes']}
            for nid in node_ids:
                self.assertNotIn('.md', nid, f'doc file in nodes: {nid}')
                self.assertNotIn('.txt', nid, f'doc file in nodes: {nid}')
            self.assertTrue(any('config.yaml' in nid for nid in node_ids), 'config.yaml should be a node')

    # --- CLI contract ---

    def test_cli_canonical_output(self) -> None:
        """Done Definition: --canonical-output generates 4 artifact files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            out_dir = Path(tmp) / 'canonical_out'
            proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(root), '--canonical-output', str(out_dir)],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertTrue((out_dir / 'normalized_graph.json').exists())
            self.assertTrue((out_dir / 'nodes.jsonl').exists())
            self.assertTrue((out_dir / 'edges.jsonl').exists())
            self.assertTrue((out_dir / 'graph_meta.json').exists())

    def test_cli_both_outputs(self) -> None:
        """Implementation decision: --output and --canonical-output together, both produced."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            summary_out = Path(tmp) / 'summary.json'
            canonical_dir = Path(tmp) / 'canonical_out'
            proc = subprocess.run(
                [
                    sys.executable, str(SCRIPT_PATH), str(root),
                    '--output', str(summary_out),
                    '--canonical-output', str(canonical_dir),
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertTrue(summary_out.exists(), 'coarse summary file missing')
            self.assertTrue((canonical_dir / 'normalized_graph.json').exists(), 'canonical artifact missing')

    def test_cli_canonical_output_respects_include_filter(self) -> None:
        """Fix 1 guard: --include-top-level filter is applied to canonical graph."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('import os\n', encoding='utf-8')
            (root / 'tests').mkdir()
            (root / 'tests' / 'test_app.py').write_text('import unittest\n', encoding='utf-8')
            out_dir = Path(tmp) / 'canonical_out'
            proc = subprocess.run(
                [
                    sys.executable, str(SCRIPT_PATH), str(root),
                    '--include-top-level', 'src',
                    '--canonical-output', str(out_dir),
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            graph = json.loads((out_dir / 'normalized_graph.json').read_text(encoding='utf-8'))
            node_ids = {n['id'] for n in graph['nodes']}
            # tests/ files must not appear in the canonical graph
            tests_nodes = [nid for nid in node_ids if nid.startswith('file:tests/')]
            self.assertEqual(tests_nodes, [],
                             f'tests/ files leaked into canonical graph: {tests_nodes}')
            # src/ files must appear
            src_nodes = [nid for nid in node_ids if nid.startswith('file:src/')]
            self.assertGreater(len(src_nodes), 0, 'no src/ nodes found in canonical graph')

    # --- Regression guards ---

    def test_existing_coarse_summary_preserved(self) -> None:
        """P1 guard: build_summary still works with same key structure."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            summary = MODULE.build_summary(root, top_n_ext=10)
            expected_keys = {
                'repo_root', 'total_files', 'python_files', 'total_import_statements',
                'python_parse_failure_count', 'python_parse_failure_files',
                'top_level_file_counts', 'top_extensions',
                'excluded_dir_names', 'included_top_level_names', 'excluded_top_level_names',
            }
            self.assertTrue(expected_keys <= set(summary), f'missing: {expected_keys - set(summary)}')

    def test_parse_failure_goes_to_sidecar(self) -> None:
        """Edge case: unparseable .py generates sidecar warning, not crash."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'bad.py').write_text('def broken(:\n', encoding='utf-8')
            _graph, sidecar = MODULE.build_canonical_graph(root)
            warnings = [s for s in sidecar if s['evidence_kind'] == 'warning']
            self.assertGreater(len(warnings), 0)

    def test_v0_core_relation_is_imports_centered(self) -> None:
        """Required Check: v0 core relation minimum is IMPORTS-centered."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_fixture(root)
            graph, _ = MODULE.build_canonical_graph(root)
            for edge in graph['edges']:
                self.assertEqual(edge['rel'], 'IMPORTS', f'unexpected relation: {edge["rel"]}')

    def test_sidecar_routing_when_empty(self) -> None:
        """Done Definition: sidecar routing path exists even when all imports resolve."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            # app.py imports core, and core.py exists → all resolve, sidecar should be empty list
            (root / 'src' / '__init__.py').write_text('', encoding='utf-8')
            (root / 'src' / 'app.py').write_text('from src import core\n', encoding='utf-8')
            (root / 'src' / 'core.py').write_text('x = 1\n', encoding='utf-8')
            _graph, sidecar = MODULE.build_canonical_graph(root)
            self.assertIsInstance(sidecar, list)

    def test_extract_imports_resolves_internal(self) -> None:
        """Step 1 unit test: extract_imports returns edge for internal import
        and dst resolves to src/core.py (not src/__init__.py)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / '__init__.py').write_text('', encoding='utf-8')
            (root / 'src' / 'app.py').write_text('from src import core\n', encoding='utf-8')
            (root / 'src' / 'core.py').write_text('x = 1\n', encoding='utf-8')
            edges, sidecar = MODULE.extract_imports(root / 'src' / 'app.py', root)
            self.assertGreater(len(edges), 0)
            self.assertEqual(edges[0]['rel'], 'IMPORTS')
            dst_values = {e['dst'] for e in edges}
            self.assertIn('file:src/core.py', dst_values,
                          f'expected file:src/core.py in dst values, got: {dst_values}')

    def test_extract_imports_unresolved_goes_to_sidecar(self) -> None:
        """Step 1 unit test: extract_imports returns sidecar for unresolved import."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'app.py').write_text('import nonexistent_module\n', encoding='utf-8')
            edges, sidecar = MODULE.extract_imports(root / 'src' / 'app.py', root)
            self.assertEqual(len(edges), 0)
            self.assertGreater(len(sidecar), 0)
            self.assertEqual(sidecar[0]['evidence_kind'], 'unresolved')


if __name__ == '__main__':
    unittest.main()
