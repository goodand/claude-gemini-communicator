#!/usr/bin/env python3
"""
depsolve_ext/tests.py
=====================
Ã­â€ ÂµÃ­â€¢Â© Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸

Ã¬â€¹Â¤Ã­â€“â€°:
    python -m pytest tests.py -v
    python tests.py
"""

import unittest
import tempfile
import json
from pathlib import Path

from .models import (
    IssueType, Severity, ImportType, FileContext, VerifyStatus,
    PackageNode, DependencyEdge, CycleInfo, DiamondInfo, Ecosystem
)
from .graph import DependencyGraph
from .extensions import (
    ImportExtractor, RuntimeVerifier, PhantomDetector,
    GoAdapter, CargoAdapter, EcosystemDetector,
    get_file_ecosystem, is_stdlib, load_hybrid_manifest,
    normalize_package_name, get_package_aliases,
    IgnoreRule, IgnoreConfig,
    NODE_BUILTINS, PYTHON_STDLIB
)
from .analyzer import DependencyAnalyzer, analyze


class TestGraph(unittest.TestCase):
    """ÃªÂ·Â¸Ã«Å¾ËœÃ­â€â€ž Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_add_nodes_edges(self):
        """Ã«â€¦Â¸Ã«â€œÅ“/Ã¬â€”Â£Ã¬Â§â‚¬ Ã¬Â¶â€ÃªÂ°â‚¬"""
        g = DependencyGraph()
        g.add_node("A", "1.0.0")
        g.add_edge(DependencyEdge(source="A", target="B", version_range="^2.0.0"))
        
        self.assertEqual(g.node_count, 2)
        self.assertEqual(g.edge_count, 1)
        self.assertTrue(g.has_node("A"))
        self.assertTrue(g.has_edge("A", "B"))
    
    def test_find_cycles(self):
        """Ã¬Ë†Å“Ã­â„¢Ëœ Ã­Æ’ÂÃ¬Â§â‚¬"""
        g = DependencyGraph()
        g.add_edge(DependencyEdge(source="A", target="B"))
        g.add_edge(DependencyEdge(source="B", target="C"))
        g.add_edge(DependencyEdge(source="C", target="A"))
        
        cycles = g.find_cycles()
        self.assertEqual(len(cycles), 1)
        self.assertEqual(set(cycles[0].path[:-1]), {"A", "B", "C"})
    
    def test_no_cycle(self):
        """Ã¬Ë†Å“Ã­â„¢Ëœ Ã¬â€”â€ Ã¬ÂÅ’"""
        g = DependencyGraph()
        g.add_edge(DependencyEdge(source="A", target="B"))
        g.add_edge(DependencyEdge(source="B", target="C"))
        
        self.assertFalse(g.has_cycle())
    
    def test_find_diamonds(self):
        """Ã«â€¹Â¤Ã¬ÂÂ´Ã¬â€¢â€žÃ«ÂªÂ¬Ã«â€œÅ“ Ã­Æ’ÂÃ¬Â§â‚¬"""
        g = DependencyGraph()
        g.add_edge(DependencyEdge(source="A", target="B"))
        g.add_edge(DependencyEdge(source="A", target="C"))
        g.add_edge(DependencyEdge(source="B", target="D", version_range="^1.0.0"))
        g.add_edge(DependencyEdge(source="C", target="D", version_range="^2.0.0"))
        
        diamonds = g.find_diamonds()
        self.assertEqual(len(diamonds), 1)
        self.assertEqual(diamonds[0].bottom, "D")
        self.assertTrue(diamonds[0].has_version_conflict)
    
    def test_mermaid_output(self):
        """Mermaid Ã¬Â¶Å“Ã«Â Â¥"""
        g = DependencyGraph()
        g.add_edge(DependencyEdge(source="A", target="B", version_range="^1.0.0"))
        
        mermaid = g.to_mermaid()
        self.assertIn("graph TD", mermaid)
        self.assertIn("-->", mermaid)
    
    def test_transitive_deps(self):
        """Ã¬Â â€žÃ¬ÂÂ´Ã¬Â Â Ã¬ÂËœÃ¬Â¡Â´Ã¬â€žÂ±"""
        g = DependencyGraph()
        g.add_edge(DependencyEdge(source="A", target="B"))
        g.add_edge(DependencyEdge(source="B", target="C"))
        g.add_edge(DependencyEdge(source="C", target="D"))
        
        deps = g.get_transitive_dependencies("A")
        self.assertEqual(deps, {"B", "C", "D"})


class TestEcosystemDetection(unittest.TestCase):
    """Ã¬Æ’ÂÃ­Æ’Å“ÃªÂ³â€ž ÃªÂ°ÂÃ¬Â§â‚¬ Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_js_extensions(self):
        """JS/TS Ã­â„¢â€¢Ã¬Å¾Â¥Ã¬Å¾Â ÃªÂ°ÂÃ¬Â§â‚¬"""
        self.assertEqual(get_file_ecosystem("app.js"), Ecosystem.JAVASCRIPT)
        self.assertEqual(get_file_ecosystem("App.tsx"), Ecosystem.JAVASCRIPT)
        self.assertEqual(get_file_ecosystem("index.mjs"), Ecosystem.JAVASCRIPT)
    
    def test_python_extensions(self):
        """Python Ã­â„¢â€¢Ã¬Å¾Â¥Ã¬Å¾Â ÃªÂ°ÂÃ¬Â§â‚¬"""
        self.assertEqual(get_file_ecosystem("main.py"), Ecosystem.PYTHON)
        self.assertEqual(get_file_ecosystem("utils.pyx"), Ecosystem.PYTHON)
    
    def test_unknown_extensions(self):
        """Ã¬â€¢Å’ Ã¬Ë†Ëœ Ã¬â€”â€ Ã«Å â€ Ã­â„¢â€¢Ã¬Å¾Â¥Ã¬Å¾Â"""
        self.assertEqual(get_file_ecosystem("readme.md"), Ecosystem.UNKNOWN)


class TestStdlibFiltering(unittest.TestCase):
    """Ã­â€˜Å“Ã¬Â¤â‚¬ Ã«ÂÂ¼Ã¬ÂÂ´Ã«Â¸Å’Ã«Å¸Â¬Ã«Â¦Â¬ Ã­â€¢â€žÃ­â€žÂ°Ã«Â§Â Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_node_builtins(self):
        """Node.js Ã«â€šÂ´Ã¬Å¾Â¥ Ã«ÂªÂ¨Ã«â€œË†"""
        self.assertTrue(is_stdlib('fs', Ecosystem.JAVASCRIPT))
        self.assertTrue(is_stdlib('https', Ecosystem.JAVASCRIPT))
        self.assertTrue(is_stdlib('path', Ecosystem.JAVASCRIPT))
        self.assertTrue(is_stdlib('node:fs', Ecosystem.JAVASCRIPT))
        
        self.assertFalse(is_stdlib('express', Ecosystem.JAVASCRIPT))
        self.assertFalse(is_stdlib('react', Ecosystem.JAVASCRIPT))
    
    def test_python_stdlib(self):
        """Python Ã­â€˜Å“Ã¬Â¤â‚¬ Ã«ÂÂ¼Ã¬ÂÂ´Ã«Â¸Å’Ã«Å¸Â¬Ã«Â¦Â¬"""
        self.assertTrue(is_stdlib('os', Ecosystem.PYTHON))
        self.assertTrue(is_stdlib('sys', Ecosystem.PYTHON))
        self.assertTrue(is_stdlib('json', Ecosystem.PYTHON))
        self.assertTrue(is_stdlib('pathlib', Ecosystem.PYTHON))
        
        self.assertFalse(is_stdlib('requests', Ecosystem.PYTHON))
        self.assertFalse(is_stdlib('numpy', Ecosystem.PYTHON))


class TestPackageNameNormalization(unittest.TestCase):
    """Ã­Å’Â¨Ã­â€šÂ¤Ã¬Â§â‚¬Ã«Âªâ€¦ Ã¬Â â€¢ÃªÂ·Å“Ã­â„¢â€ Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_hyphen_to_underscore(self):
        """Ã­â€¢ËœÃ¬ÂÂ´Ã­â€Ë† Ã¢â€ â€™ Ã¬â€“Â¸Ã«Ââ€Ã¬Å Â¤Ã¬Â½â€Ã¬â€“Â´"""
        self.assertEqual(normalize_package_name("pydantic-settings"), "pydantic_settings")
        self.assertEqual(normalize_package_name("scikit-learn"), "scikit_learn")
    
    def test_already_normalized(self):
        """Ã¬ÂÂ´Ã«Â¯Â¸ Ã¬Â â€¢ÃªÂ·Å“Ã­â„¢â€Ã«ÂÅ“ Ã¬ÂÂ´Ã«Â¦â€ž"""
        self.assertEqual(normalize_package_name("pydantic_settings"), "pydantic_settings")
        self.assertEqual(normalize_package_name("requests"), "requests")
    
    def test_case_normalization(self):
        """Ã«Å’â‚¬Ã¬â€ Å’Ã«Â¬Â¸Ã¬Å¾Â Ã¬Â â€¢ÃªÂ·Å“Ã­â„¢â€"""
        self.assertEqual(normalize_package_name("PyYAML"), "pyyaml")
        self.assertEqual(normalize_package_name("Flask"), "flask")
    
    def test_dot_handling(self):
        """Ã¬Â Â Ã¬Â²ËœÃ«Â¦Â¬"""
        self.assertEqual(normalize_package_name("zope.interface"), "zope_interface")
    
    def test_get_aliases(self):
        """Ã«Â³â€žÃ¬Â¹Â­ Ã¬Æ’ÂÃ¬â€žÂ±"""
        aliases = get_package_aliases("pydantic-settings")
        self.assertIn("pydantic-settings", aliases)
        self.assertIn("pydantic_settings", aliases)
        
        # Ã¬ÂÂ´Ã«Â¯Â¸ Ã¬Â â€¢ÃªÂ·Å“Ã­â„¢â€Ã«ÂÅ“ Ã¬ÂÂ´Ã«Â¦â€ž
        aliases2 = get_package_aliases("requests")
        self.assertEqual(aliases2, {"requests"})


class TestIgnoreConfig(unittest.TestCase):
    """Ignore ÃªÂ·Å“Ã¬Â¹â„¢ Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_basic_rule(self):
        """ÃªÂ¸Â°Ã«Â³Â¸ ÃªÂ·Å“Ã¬Â¹â„¢"""
        config = IgnoreConfig()
        config.add_rule("pytest")
        
        ignored, _ = config.should_ignore_package("pytest", Ecosystem.PYTHON)
        self.assertTrue(ignored)
        ignored, _ = config.should_ignore_package("requests", Ecosystem.PYTHON)
        self.assertFalse(ignored)
    
    def test_regex_rule(self):
        """Ã¬Â â€¢ÃªÂ·Å“Ã¬â€¹Â ÃªÂ·Å“Ã¬Â¹â„¢ (Ã¬â„¢â‚¬Ã¬ÂÂ¼Ã«â€œÅ“Ã¬Â¹Â´Ã«â€œÅ“)"""
        config = IgnoreConfig()
        config.add_rule("mypy*")  # ÃªÂ¸â‚¬Ã«Â¡Å“Ã«Â¸Å’ Ã­Å’Â¨Ã­â€žÂ´ Ã¢â€ â€™ Ã¬Â â€¢ÃªÂ·Å“Ã¬â€¹ÂÃ¬Å“Â¼Ã«Â¡Å“ Ã«Â³â‚¬Ã­â„¢ËœÃ«ÂÂ¨
        
        ignored, _ = config.should_ignore_package("mypy", Ecosystem.PYTHON)
        self.assertTrue(ignored)
        ignored, _ = config.should_ignore_package("mypy-extensions", Ecosystem.PYTHON)
        self.assertTrue(ignored)
        ignored, _ = config.should_ignore_package("pytest", Ecosystem.PYTHON)
        self.assertFalse(ignored)
    
    def test_ecosystem_specific_rule(self):
        """Ã¬Æ’ÂÃ­Æ’Å“ÃªÂ³â€žÃ«Â³â€ž ÃªÂ·Å“Ã¬Â¹â„¢"""
        config = IgnoreConfig()
        config.add_rule("pytest", ecosystem=Ecosystem.PYTHON)
        
        ignored, _ = config.should_ignore_package("pytest", Ecosystem.PYTHON)
        self.assertTrue(ignored)
        ignored, _ = config.should_ignore_package("pytest", Ecosystem.JAVASCRIPT)
        self.assertFalse(ignored)
    
    def test_skip_dirs(self):
        """Ã¬Å Â¤Ã­â€šÂµ Ã«â€â€Ã«Â â€°Ã­â€ Â Ã«Â¦Â¬"""
        config = IgnoreConfig()
        config.add_skip_dir(".mypy_cache")
        
        self.assertTrue(config.should_skip_path(Path("/project/.mypy_cache/file.py")))
        self.assertFalse(config.should_skip_path(Path("/project/src/file.py")))
    
    def test_load_from_file(self):
        """Ã­Å’Å’Ã¬ÂÂ¼Ã¬â€”ÂÃ¬â€žÅ“ Ã«Â¡Å“Ã«â€œÅ“"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # .depsolve-ignore Ã­Å’Å’Ã¬ÂÂ¼ Ã¬Æ’ÂÃ¬â€žÂ±
            ignore_file = project / ".depsolve-ignore"
            ignore_file.write_text("""
# Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸ Ã«Ââ€žÃªÂµÂ¬
pytest
mypy
[python] black
[javascript] eslint
            """)
            
            config = IgnoreConfig.load_from_file(ignore_file)
            
            ignored, _ = config.should_ignore_package("pytest", Ecosystem.PYTHON)
            self.assertTrue(ignored)
            ignored, _ = config.should_ignore_package("mypy", Ecosystem.PYTHON)
            self.assertTrue(ignored)
            ignored, _ = config.should_ignore_package("black", Ecosystem.PYTHON)
            self.assertTrue(ignored)
            ignored, _ = config.should_ignore_package("black", Ecosystem.JAVASCRIPT)
            self.assertFalse(ignored)
    
    def test_load_json_config(self):
        """JSON Ã¬â€žÂ¤Ã¬Â â€¢ Ã«Â¡Å“Ã«â€œÅ“"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            config_file = project / "depsolve.config.json"
            config_file.write_text(json.dumps({
                "ignore_packages": [
                    "pytest",
                    {"pattern": "mypy*"}
                ],
                "skip_dirs": [".mypy_cache"]
            }))
            
            config = IgnoreConfig.load_from_file(config_file)
            
            ignored, _ = config.should_ignore_package("pytest", Ecosystem.PYTHON)
            self.assertTrue(ignored)
            ignored, _ = config.should_ignore_package("mypy-extensions", Ecosystem.PYTHON)
            self.assertTrue(ignored)
            self.assertTrue(config.should_skip_path(Path("/project/.mypy_cache/file.py")))


class TestImportExtractor(unittest.TestCase):
    """Import Ã¬Â¶â€Ã¬Â¶Å“ Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def setUp(self):
        self.extractor = ImportExtractor()
    
    def test_static_import(self):
        """ÃªÂ¸Â°Ã«Â³Â¸ import"""
        imports = self.extractor.extract_content("import React from 'react';")
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].package, "react")
        self.assertEqual(imports[0].import_type, ImportType.STATIC)
    
    def test_type_import(self):
        """TypeScript type-only"""
        imports = self.extractor.extract_content("import type { FC } from 'react';")
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].import_type, ImportType.TYPE_ONLY)
        self.assertTrue(imports[0].is_type_only)
    
    def test_require(self):
        """CommonJS require"""
        imports = self.extractor.extract_content("const x = require('express');")
        self.assertEqual(imports[0].package, "express")
        self.assertEqual(imports[0].import_type, ImportType.REQUIRE)
    
    def test_re_export(self):
        """Re-export"""
        imports = self.extractor.extract_content("export * from 'lodash';")
        self.assertEqual(imports[0].import_type, ImportType.RE_EXPORT)
    
    def test_jest_mock(self):
        """Jest mock"""
        imports = self.extractor.extract_content("jest.mock('axios');")
        self.assertEqual(imports[0].import_type, ImportType.JEST_MOCK)
    
    def test_scoped_package(self):
        """Scoped Ã­Å’Â¨Ã­â€šÂ¤Ã¬Â§â‚¬"""
        imports = self.extractor.extract_content("import { x } from '@babel/core';")
        self.assertEqual(imports[0].package, "@babel/core")
    
    def test_node_builtin_ignored(self):
        """Node.js Ã«â€šÂ´Ã¬Å¾Â¥ Ã«ÂªÂ¨Ã«â€œË† Ã«Â¬Â´Ã¬â€¹Å“"""
        imports = self.extractor.extract_content("import fs from 'fs';")
        self.assertEqual(len(imports), 0)
    
    def test_node_https_ignored(self):
        """Node.js https Ã«ÂªÂ¨Ã«â€œË† Ã«Â¬Â´Ã¬â€¹Å“ (Ã­â€¢ÂµÃ¬â€¹Â¬ Ã¬Ë†ËœÃ¬Â â€¢ ÃªÂ²â‚¬Ã¬Â¦Â)"""
        imports = self.extractor.extract_content("import https from 'https';")
        self.assertEqual(len(imports), 0)
    
    def test_file_context_config(self):
        """Ã­Å’Å’Ã¬ÂÂ¼ Ã¬Â»Â¨Ã­â€¦ÂÃ¬Å Â¤Ã­Å Â¸ - config"""
        imports = self.extractor.extract_content(
            "import x from 'pkg';", "vite.config.ts")
        self.assertEqual(imports[0].file_context, FileContext.CONFIG)
    
    def test_file_context_test(self):
        """Ã­Å’Å’Ã¬ÂÂ¼ Ã¬Â»Â¨Ã­â€¦ÂÃ¬Å Â¤Ã­Å Â¸ - test"""
        imports = self.extractor.extract_content(
            "import x from 'pkg';", "App.test.tsx")
        self.assertEqual(imports[0].file_context, FileContext.TEST)
    
    def test_with_ignore_config(self):
        """Ignore Ã¬â€žÂ¤Ã¬Â â€¢ÃªÂ³Â¼ Ã­â€¢Â¨ÃªÂ»Ëœ"""
        config = IgnoreConfig()
        config.add_rule("axios")
        
        extractor = ImportExtractor(ignore_config=config)
        imports = extractor.extract_content("import axios from 'axios';")
        self.assertEqual(len(imports), 0)


class TestPythonImportExtraction(unittest.TestCase):
    """Python Import Ã¬Â¶â€Ã¬Â¶Å“ Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def setUp(self):
        self.extractor = ImportExtractor(filter_stdlib=True)
    
    def test_import_statement(self):
        """ÃªÂ¸Â°Ã«Â³Â¸ import Ã«Â¬Â¸"""
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            f.write("import requests\nimport numpy as np\n")
            f.flush()
            
            imports = self.extractor.extract_file(Path(f.name))
            packages = {i.package for i in imports}
            self.assertIn('requests', packages)
            self.assertIn('numpy', packages)
    
    def test_from_import(self):
        """from ... import Ã«Â¬Â¸"""
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            f.write("from pandas import DataFrame\n")
            f.flush()
            
            imports = self.extractor.extract_file(Path(f.name))
            packages = {i.package for i in imports}
            self.assertIn('pandas', packages)
    
    def test_stdlib_filtered(self):
        """Python Ã­â€˜Å“Ã¬Â¤â‚¬ Ã«ÂÂ¼Ã¬ÂÂ´Ã«Â¸Å’Ã«Å¸Â¬Ã«Â¦Â¬ Ã­â€¢â€žÃ­â€žÂ°Ã«Â§Â"""
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            f.write("import os\nimport sys\nimport json\n")
            f.flush()
            
            imports = self.extractor.extract_file(Path(f.name))
            self.assertEqual(len(imports), 0)


class TestHybridManifest(unittest.TestCase):
    """Ã­â€¢ËœÃ¬ÂÂ´Ã«Â¸Å’Ã«Â¦Â¬Ã«â€œÅ“ Manifest Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_npm_only(self):
        """npm Ã­â€â€žÃ«Â¡Å“Ã¬Â ÂÃ­Å Â¸"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "package.json").write_text(json.dumps({
                "dependencies": {"react": "^18.0.0"},
                "devDependencies": {"jest": "^29.0.0"}
            }))
            
            manifest = load_hybrid_manifest(project)
            self.assertIn(Ecosystem.JAVASCRIPT, manifest.detected_ecosystems)
            self.assertIn("react", manifest.js_deps)
    
    def test_python_only(self):
        """Python Ã­â€â€žÃ«Â¡Å“Ã¬Â ÂÃ­Å Â¸"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "requirements.txt").write_text("requests>=2.28.0\n")
            
            manifest = load_hybrid_manifest(project)
            self.assertIn(Ecosystem.PYTHON, manifest.detected_ecosystems)
            self.assertIn("requests", manifest.py_deps)
    
    def test_hybrid_project(self):
        """Ã­â€¢ËœÃ¬ÂÂ´Ã«Â¸Å’Ã«Â¦Â¬Ã«â€œÅ“ Ã­â€â€žÃ«Â¡Å“Ã¬Â ÂÃ­Å Â¸"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "package.json").write_text(json.dumps({
                "dependencies": {"express": "^4.0.0"}
            }))
            (project / "requirements.txt").write_text("flask>=2.0.0\n")
            
            manifest = load_hybrid_manifest(project)
            self.assertIn(Ecosystem.JAVASCRIPT, manifest.detected_ecosystems)
            self.assertIn(Ecosystem.PYTHON, manifest.detected_ecosystems)
    
    def test_subdirectory_manifest(self):
        """Ã¬â€žÅ“Ã«Â¸Å’Ã«â€â€Ã«Â â€°Ã­â€ Â Ã«Â¦Â¬ manifest Ã­Æ’ÂÃ¬Â§â‚¬"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Ã«Â£Â¨Ã­Å Â¸Ã¬â€”Â package.json
            (project / "package.json").write_text(json.dumps({
                "dependencies": {"react": "^18.0.0"}
            }))
            
            # backend/ Ã¬â€žÅ“Ã«Â¸Å’Ã«â€â€Ã«Â â€°Ã­â€ Â Ã«Â¦Â¬Ã¬â€”Â requirements.txt
            backend = project / "backend"
            backend.mkdir()
            (backend / "requirements.txt").write_text("fastapi>=0.100.0\npydantic>=2.0\n")
            
            manifest = load_hybrid_manifest(project)
            
            self.assertIn("react", manifest.js_deps)
            self.assertIn("fastapi", manifest.py_deps)
            self.assertIn("pydantic", manifest.py_deps)
    
    def test_pyproject_toml_pep621(self):
        """pyproject.toml PEP 621 Ã­Å’Å’Ã¬â€¹Â±"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            (project / "pyproject.toml").write_text("""
[project]
name = "test-project"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=23.0",
]
""")
            
            manifest = load_hybrid_manifest(project)
            
            self.assertIn("fastapi", manifest.py_deps)
            self.assertIn("pydantic", manifest.py_deps)
            self.assertIn("pytest", manifest.py_dev_deps)
            self.assertIn("black", manifest.py_dev_deps)
    
    def test_pyproject_toml_poetry(self):
        """pyproject.toml Poetry Ã­Å’Å’Ã¬â€¹Â±"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            (project / "pyproject.toml").write_text("""
[tool.poetry]
name = "test-project"

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.100.0"
pydantic = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
""")
            
            manifest = load_hybrid_manifest(project)
            
            self.assertIn("fastapi", manifest.py_deps)
            self.assertIn("pydantic", manifest.py_deps)
            # pythonÃ¬Ââ‚¬ Ã¬Â Å“Ã¬â„¢Â¸Ã«ÂËœÃ¬â€“Â´Ã¬â€¢Â¼ Ã­â€¢Â¨
            self.assertNotIn("python", manifest.py_deps)
    
    def test_requirements_dev_txt(self):
        """requirements-dev.txt Ã¬Â§â‚¬Ã¬â€ºÂ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            (project / "requirements.txt").write_text("fastapi>=0.100.0\n")
            (project / "requirements-dev.txt").write_text("pytest>=7.0\nmypy>=1.0\n")
            
            manifest = load_hybrid_manifest(project)
            
            self.assertIn("fastapi", manifest.py_deps)
            self.assertIn("pytest", manifest.py_dev_deps)
            self.assertIn("mypy", manifest.py_dev_deps)
    
    def test_package_name_normalization(self):
        """Ã­Å’Â¨Ã­â€šÂ¤Ã¬Â§â‚¬Ã«Âªâ€¦ Ã¬Â â€¢ÃªÂ·Å“Ã­â„¢â€ (Ã«Â³â€žÃ¬Â¹Â­ Ã­ÂÂ¬Ã­â€¢Â¨)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            (project / "requirements.txt").write_text("pydantic-settings>=2.0\n")
            
            manifest = load_hybrid_manifest(project)
            
            # Ã«â€˜Ëœ Ã«â€¹Â¤ Ã­ÂÂ¬Ã­â€¢Â¨Ã«ÂËœÃ¬â€“Â´Ã¬â€¢Â¼ Ã­â€¢Â¨
            self.assertTrue(
                "pydantic-settings" in manifest.py_deps or 
                "pydantic_settings" in manifest.py_deps
            )


class TestPhantomDetection(unittest.TestCase):
    """Phantom Ã­Æ’ÂÃ¬Â§â‚¬ Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_js_phantom(self):
        """JS Phantom Ã­Æ’ÂÃ¬Â§â‚¬"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "package.json").write_text(json.dumps({
                "dependencies": {"react": "^18.0.0"}
            }))
            
            src = project / "src"
            src.mkdir()
            (src / "App.js").write_text(
                "import React from 'react';\n"
                "import axios from 'axios';\n"
            )
            
            detector = PhantomDetector(
                project_path=project,
                js_deps={"react"},
                verify=False
            )
            
            phantoms = detector.detect()
            js_phantoms = [p for p in phantoms if p.ecosystem == Ecosystem.JAVASCRIPT]
            phantom_packages = {p.package for p in js_phantoms}
            
            self.assertIn("axios", phantom_packages)
            self.assertNotIn("react", phantom_packages)
    
    def test_python_phantom(self):
        """Python Phantom Ã­Æ’ÂÃ¬Â§â‚¬"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "requirements.txt").write_text("requests>=2.28.0\n")
            
            src = project / "src"
            src.mkdir()
            (src / "main.py").write_text(
                "import requests\n"
                "import pandas as pd\n"
            )
            
            detector = PhantomDetector(
                project_path=project,
                py_deps={"requests"},
                verify=False
            )
            
            phantoms = detector.detect()
            py_phantoms = [p for p in phantoms if p.ecosystem == Ecosystem.PYTHON]
            phantom_packages = {p.package for p in py_phantoms}
            
            self.assertIn("pandas", phantom_packages)
            self.assertNotIn("requests", phantom_packages)
    
    def test_ecosystem_isolation(self):
        """Ã¬Æ’ÂÃ­Æ’Å“ÃªÂ³â€ž ÃªÂ²Â©Ã«Â¦Â¬ - JS importÃªÂ°â‚¬ Python depsÃ«Â¡Å“ ÃªÂ²â‚¬Ã¬Â¦ÂÃ«ÂËœÃ¬Â§â‚¬ Ã¬â€¢Å Ã¬ÂÅ’"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "requirements.txt").write_text("openai>=1.0.0\n")
            
            src = project / "src"
            src.mkdir()
            (src / "client.js").write_text("import OpenAI from 'openai';\n")
            
            detector = PhantomDetector(
                project_path=project,
                py_deps={"openai"},
                js_deps=set(),
                verify=False
            )
            
            phantoms = detector.detect()
            js_phantoms = [p for p in phantoms if p.ecosystem == Ecosystem.JAVASCRIPT]
            
            self.assertEqual(len(js_phantoms), 1)
            self.assertEqual(js_phantoms[0].package, "openai")
            self.assertTrue(js_phantoms[0].is_phantom)
    
    def test_normalized_package_matching(self):
        """Ã¬Â â€¢ÃªÂ·Å“Ã­â„¢â€Ã«ÂÅ“ Ã­Å’Â¨Ã­â€šÂ¤Ã¬Â§â‚¬Ã«Âªâ€¦ Ã«Â§Â¤Ã¬Â¹Â­"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "requirements.txt").write_text("pydantic-settings>=2.0\n")
            
            src = project / "src"
            src.mkdir()
            # importÃ«Å â€ Ã¬â€“Â¸Ã«Ââ€Ã¬Å Â¤Ã¬Â½â€Ã¬â€“Â´Ã«Â¡Å“
            (src / "main.py").write_text("from pydantic_settings import BaseSettings\n")
            
            detector = PhantomDetector(
                project_path=project,
                py_deps={"pydantic-settings", "pydantic_settings"},
                verify=False
            )
            
            phantoms = detector.detect()
            py_phantoms = [p for p in phantoms if p.ecosystem == Ecosystem.PYTHON]
            phantom_packages = {p.package for p in py_phantoms}
            
            # pydantic_settingsÃ«Å â€ PhantomÃ¬ÂÂ´ Ã¬â€¢â€žÃ«â€¹Ë†Ã¬â€“Â´Ã¬â€¢Â¼ Ã­â€¢Â¨
            self.assertNotIn("pydantic_settings", phantom_packages)


class TestRuntimeVerifier(unittest.TestCase):
    """Ã«Å¸Â°Ã­Æ’â‚¬Ã¬Å¾â€ž ÃªÂ²â‚¬Ã¬Â¦Â Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project = Path(self.temp_dir)
    
    def test_node_modules_scan(self):
        """node_modules Ã¬Å Â¤Ã¬Âºâ€"""
        nm = self.project / "node_modules" / "lodash"
        nm.mkdir(parents=True)
        (nm / "package.json").write_text(json.dumps({
            "name": "lodash", "version": "4.17.21"
        }))
        
        verifier = RuntimeVerifier(self.project)
        version = verifier._scan_node_modules("lodash")
        self.assertEqual(version, "4.17.21")
    
    def test_scoped_package_scan(self):
        """Scoped Ã­Å’Â¨Ã­â€šÂ¤Ã¬Â§â‚¬ Ã¬Å Â¤Ã¬Âºâ€"""
        nm = self.project / "node_modules" / "@babel" / "core"
        nm.mkdir(parents=True)
        (nm / "package.json").write_text(json.dumps({
            "name": "@babel/core", "version": "7.23.0"
        }))
        
        verifier = RuntimeVerifier(self.project)
        version = verifier._scan_node_modules("@babel/core")
        self.assertEqual(version, "7.23.0")


class TestGoAdapter(unittest.TestCase):
    """Go Ã¬â€“Â´Ã«Å’â€˜Ã­â€žÂ° Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project = Path(self.temp_dir)
    
    def test_detect(self):
        """Go Ã­â€â€žÃ«Â¡Å“Ã¬Â ÂÃ­Å Â¸ ÃªÂ°ÂÃ¬Â§â‚¬"""
        adapter = GoAdapter(self.project)
        self.assertFalse(adapter.detect())
        
        (self.project / "go.mod").write_text("module test\ngo 1.21\n")
        self.assertTrue(adapter.detect())
    
    def test_parse_go_mod(self):
        """go.mod Ã­Å’Å’Ã¬â€¹Â±"""
        (self.project / "go.mod").write_text("""
module github.com/user/myproject

go 1.21

require (
    github.com/gin-gonic/gin v1.9.0
)
""")
        adapter = GoAdapter(self.project)
        info = adapter.get_info()
        
        self.assertEqual(info.name, "github.com/user/myproject")
        self.assertIn("github.com/gin-gonic/gin", info.dependencies)


class TestCargoAdapter(unittest.TestCase):
    """Cargo Ã¬â€“Â´Ã«Å’â€˜Ã­â€žÂ° Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project = Path(self.temp_dir)
    
    def test_detect(self):
        """Cargo Ã­â€â€žÃ«Â¡Å“Ã¬Â ÂÃ­Å Â¸ ÃªÂ°ÂÃ¬Â§â‚¬"""
        adapter = CargoAdapter(self.project)
        self.assertFalse(adapter.detect())
        
        (self.project / "Cargo.toml").write_text(
            '[package]\nname = "test"\nversion = "0.1.0"\n'
        )
        self.assertTrue(adapter.detect())


class TestAnalyzer(unittest.TestCase):
    """Ã«Â¶â€žÃ¬â€žÂÃªÂ¸Â° Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project = Path(self.temp_dir)
    
    def test_npm_analysis(self):
        """npm Ã­â€â€žÃ«Â¡Å“Ã¬Â ÂÃ­Å Â¸ Ã«Â¶â€žÃ¬â€žÂ"""
        (self.project / "package.json").write_text(json.dumps({
            "name": "test-project",
            "dependencies": {"react": "^18.0.0", "lodash": "^4.17.0"},
            "devDependencies": {"jest": "^29.0.0"}
        }))
        
        src = self.project / "src"
        src.mkdir()
        (src / "App.tsx").write_text("""
        import React from 'react';
        import axios from 'axios';
        """)
        
        result = analyze(str(self.project), verify=False)
        
        self.assertEqual(result.ecosystem, "npm")
        self.assertGreater(result.summary.total_packages, 0)
        
        phantom_issues = [i for i in result.issues if i.type == IssueType.PHANTOM]
        phantom_packages = [i.locations[0].package for i in phantom_issues]
        self.assertIn("axios", phantom_packages)


class TestIntegration(unittest.TestCase):
    """Ã­â€ ÂµÃ­â€¢Â© Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_full_workflow(self):
        """Ã¬Â â€žÃ¬Â²Â´ Ã¬â€ºÅ’Ã­ÂÂ¬Ã­â€Å’Ã«Â¡Å“Ã¬Å¡Â°"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            (project / "package.json").write_text(json.dumps({
                "name": "test-project",
                "dependencies": {"react": "^18.0.0"},
                "devDependencies": {"tailwindcss": "^3.0.0"}
            }))
            
            src = project / "src"
            src.mkdir()
            (src / "App.tsx").write_text("""
            import React from 'react';
            import axios from 'axios';
            """)
            
            (project / "tailwind.config.js").write_text(
                "module.exports = require('tailwindcss');"
            )
            
            result = analyze(str(project), verify=False)
            
            phantom_pkgs = [
                i.locations[0].package
                for i in result.issues
                if i.type == IssueType.PHANTOM
            ]
            self.assertIn("axios", phantom_pkgs)
            self.assertNotIn("tailwindcss", phantom_pkgs)
            
            self.assertIsNotNone(result.mermaid_diagram)
    
    def test_hybrid_project_workflow(self):
        """Ã­â€¢ËœÃ¬ÂÂ´Ã«Â¸Å’Ã«Â¦Â¬Ã«â€œÅ“ Ã­â€â€žÃ«Â¡Å“Ã¬Â ÂÃ­Å Â¸ Ã¬â€ºÅ’Ã­ÂÂ¬Ã­â€Å’Ã«Â¡Å“Ã¬Å¡Â°"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Ã«Â£Â¨Ã­Å Â¸: package.json (frontend)
            (project / "package.json").write_text(json.dumps({
                "name": "frontend",
                "dependencies": {"react": "^18.0.0"}
            }))
            
            # backend/: pyproject.toml
            backend = project / "backend"
            backend.mkdir()
            (backend / "pyproject.toml").write_text("""
[project]
name = "backend"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic-settings>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0"]
""")
            
            # Ã¬â€ Å’Ã¬Å Â¤ Ã­Å’Å’Ã¬ÂÂ¼
            src = project / "src"
            src.mkdir()
            (src / "App.tsx").write_text("import React from 'react';\nimport axios from 'axios';")
            
            backend_src = backend / "src"
            backend_src.mkdir()
            (backend_src / "main.py").write_text("from fastapi import FastAPI\nfrom pydantic_settings import BaseSettings")
            
            result = analyze(str(project), verify=False)
            
            # Ã­â€¢ËœÃ¬ÂÂ´Ã«Â¸Å’Ã«Â¦Â¬Ã«â€œÅ“ Ã¬Æ’ÂÃ­Æ’Å“ÃªÂ³â€ž ÃªÂ°ÂÃ¬Â§â‚¬
            self.assertTrue("javascript" in result.ecosystem.lower() or "npm" in result.ecosystem.lower())
            
            # JS phantom: axios
            js_phantoms = [
                i for i in result.issues 
                if i.type == IssueType.PHANTOM and "axios" in str(i.locations)
            ]
            self.assertGreater(len(js_phantoms), 0)


class TestNodeBuiltinComprehensive(unittest.TestCase):
    """Node.js Ã«â€šÂ´Ã¬Å¾Â¥ Ã«ÂªÂ¨Ã«â€œË† Ã­ÂÂ¬ÃªÂ´â€ž Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_all_common_builtins(self):
        """Ã¬Å¾ÂÃ¬Â£Â¼ Ã¬â€œÂ°Ã¬ÂÂ´Ã«Å â€ Ã«â€šÂ´Ã¬Å¾Â¥ Ã«ÂªÂ¨Ã«â€œË†"""
        common_builtins = [
            'fs', 'path', 'http', 'https', 'url', 'util', 'os',
            'crypto', 'stream', 'events', 'child_process', 'buffer',
        ]
        
        for mod in common_builtins:
            self.assertTrue(
                is_stdlib(mod, Ecosystem.JAVASCRIPT),
                f"{mod} should be Node.js builtin"
            )


class TestPythonStdlibComprehensive(unittest.TestCase):
    """Python Ã­â€˜Å“Ã¬Â¤â‚¬ Ã«ÂÂ¼Ã¬ÂÂ´Ã«Â¸Å’Ã«Å¸Â¬Ã«Â¦Â¬ Ã­ÂÂ¬ÃªÂ´â€ž Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_all_common_stdlib(self):
        """Ã¬Å¾ÂÃ¬Â£Â¼ Ã¬â€œÂ°Ã¬ÂÂ´Ã«Å â€ Ã­â€˜Å“Ã¬Â¤â‚¬ Ã«ÂÂ¼Ã¬ÂÂ´Ã«Â¸Å’Ã«Å¸Â¬Ã«Â¦Â¬"""
        common_stdlib = [
            'os', 'sys', 'json', 're', 'datetime', 'collections',
            'itertools', 'functools', 'pathlib', 'typing', 'logging',
        ]
        
        for mod in common_stdlib:
            self.assertTrue(
                is_stdlib(mod, Ecosystem.PYTHON),
                f"{mod} should be Python stdlib"
            )


class TestLocalModuleFiltering(unittest.TestCase):
    """Ã«â€šÂ´Ã«Â¶â‚¬ Ã«ÂªÂ¨Ã«â€œË† Ã­â€¢â€žÃ­â€žÂ°Ã«Â§Â Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸"""
    
    def test_self_detection_filtered(self):
        """Ã«Ââ€žÃªÂµÂ¬ Ã¬Å¾ÂÃ¬â€¹Â Ã¬ÂËœ Ã¬â€ Å’Ã¬Å Â¤Ã¬Â½â€Ã«â€œÅ“ÃªÂ°â‚¬ PhantomÃ¬Å“Â¼Ã«Â¡Å“ Ã¬Å¾Â¡Ã­Å¾Ë†Ã¬Â§â‚¬ Ã¬â€¢Å Ã¬ÂÅ’"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Ã«â€šÂ´Ã«Â¶â‚¬ Ã«ÂªÂ¨Ã«â€œË† ÃªÂµÂ¬Ã¬Â¡Â° Ã¬Æ’ÂÃ¬â€žÂ±
            (project / "analyzer.py").write_text("# analyzer module\n")
            (project / "models.py").write_text("# models module\n")
            (project / "main.py").write_text(
                "import analyzer\n"
                "import models\n"
            )
            
            detector = PhantomDetector(project_path=project, verify=False)
            phantoms = detector.detect()
            
            phantom_packages = {p.package for p in phantoms}
            # Ã«â€šÂ´Ã«Â¶â‚¬ Ã«ÂªÂ¨Ã«â€œË†Ã¬Ââ‚¬ PhantomÃ¬Å“Â¼Ã«Â¡Å“ Ã¬Å¾Â¡Ã­Å¾Ë†Ã«Â©Â´ Ã¬â€¢Ë†Ã«ÂÂ¨
            self.assertNotIn("analyzer", phantom_packages)
            self.assertNotIn("models", phantom_packages)
    
    def test_package_self_detection_filtered(self):
        """Ã­Å’Â¨Ã­â€šÂ¤Ã¬Â§â‚¬ Ã­Ëœâ€¢Ã­Æ’Å“Ã¬ÂËœ Ã«â€šÂ´Ã«Â¶â‚¬ Ã«ÂªÂ¨Ã«â€œË† Ã­â€¢â€žÃ­â€žÂ°Ã«Â§Â"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Ã­Å’Â¨Ã­â€šÂ¤Ã¬Â§â‚¬ ÃªÂµÂ¬Ã¬Â¡Â°
            pkg = project / "mypackage"
            pkg.mkdir()
            (pkg / "__init__.py").write_text("# package init\n")
            (pkg / "utils.py").write_text("# utils\n")
            
            (project / "main.py").write_text("import mypackage\n")
            
            detector = PhantomDetector(project_path=project, verify=False)
            phantoms = detector.detect()
            
            phantom_packages = {p.package for p in phantoms}
            self.assertNotIn("mypackage", phantom_packages)


class TestASTBasedParsing(unittest.TestCase):
    """AST ÃªÂ¸Â°Ã«Â°Ëœ Ã­Å’Å’Ã¬â€¹Â± Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸ (Ã«Â¬Â¸Ã¬Å¾ÂÃ¬â€”Â´ Ã«â€šÂ´ import Ã¬ËœÂ¤Ã­Æ’Â Ã«Â°Â©Ã¬Â§â‚¬)"""
    
    def test_string_import_ignored(self):
        """Ã«Â¬Â¸Ã¬Å¾ÂÃ¬â€”Â´ Ã«â€šÂ´Ã¬ÂËœ import Ã«Â¬Â¸Ã¬Ââ‚¬ Ã«Â¬Â´Ã¬â€¹Å“Ã«ÂÂ¨"""
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            f.write('''
# Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸Ã¬Å¡Â© Ã«Â¬Â¸Ã¬Å¾ÂÃ¬â€”Â´
test_code = """
import react from 'react';
import axios from 'axios';
"""
# Ã¬â€¹Â¤Ã¬Â Å“ import
import json
''')
            f.flush()
            
            extractor = ImportExtractor(filter_stdlib=True)
            imports = extractor.extract_file(Path(f.name))
            
            packages = {i.package for i in imports}
            # Ã«Â¬Â¸Ã¬Å¾ÂÃ¬â€”Â´ Ã¬â€¢Ë†Ã¬ÂËœ react, axiosÃ«Å â€ Ã¬Å¾Â¡Ã­Å¾Ë†Ã«Â©Â´ Ã¬â€¢Ë†Ã«ÂÂ¨
            self.assertNotIn("react", packages)
            self.assertNotIn("axios", packages)
    
    def test_comment_import_ignored(self):
        """Ã¬Â£Â¼Ã¬â€žÂ Ã«â€šÂ´Ã¬ÂËœ import Ã¬â€“Â¸ÃªÂ¸â€°Ã¬Ââ‚¬ Ã«Â¬Â´Ã¬â€¹Å“Ã«ÂÂ¨"""
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            f.write('''
# import nonexistent_package
# from fake_module import something
import json  # Ã¬â€¹Â¤Ã¬Â Å“ import
''')
            f.flush()
            
            extractor = ImportExtractor(filter_stdlib=True)
            imports = extractor.extract_file(Path(f.name))
            
            packages = {i.package for i in imports}
            self.assertNotIn("nonexistent_package", packages)
            self.assertNotIn("fake_module", packages)


def run_tests():
    """Ã­â€¦Å’Ã¬Å Â¤Ã­Å Â¸ Ã¬â€¹Â¤Ã­â€“â€°"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestGraph,
        TestEcosystemDetection,
        TestStdlibFiltering,
        TestPackageNameNormalization,
        TestIgnoreConfig,
        TestImportExtractor,
        TestPythonImportExtraction,
        TestHybridManifest,
        TestPhantomDetection,
        TestRuntimeVerifier,
        TestGoAdapter,
        TestCargoAdapter,
        TestAnalyzer,
        TestIntegration,
        TestNodeBuiltinComprehensive,
        TestPythonStdlibComprehensive,
        TestLocalModuleFiltering,
        TestASTBasedParsing,
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
