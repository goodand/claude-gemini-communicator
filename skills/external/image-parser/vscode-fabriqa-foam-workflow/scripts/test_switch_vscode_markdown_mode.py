#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("switch_vscode_markdown_mode.py")
SPEC = importlib.util.spec_from_file_location("switch_vscode_markdown_mode", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class StripJsoncTests(unittest.TestCase):
    def test_strip_jsonc_removes_comments_but_preserves_patterns_in_strings(self):
        raw = """
        {
          // line comment
          "files.exclude": {
            "**/*.md": true /* block comment */
          },
          "note": "keep // this text",
          "glob": "**/*.md"
        }
        """
        cleaned = MODULE.strip_jsonc(raw)
        self.assertIn('"**/*.md": true', cleaned)
        self.assertIn('"note": "keep // this text"', cleaned)
        self.assertIn('"glob": "**/*.md"', cleaned)
        self.assertNotIn("line comment", cleaned)
        self.assertNotIn("block comment", cleaned)


class SettingsModeSwitchTests(unittest.TestCase):
    def test_load_settings_returns_empty_for_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".vscode" / "settings.json"
            self.assertEqual(MODULE.load_settings(path), {})

    def test_load_settings_parses_jsonc_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".vscode" / "settings.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                '{\n'
                '  // comment\n'
                '  "workbench.editorAssociations": {\n'
                '    "*.md": "default"\n'
                '  }\n'
                '}\n',
                encoding="utf-8",
            )
            data = MODULE.load_settings(path)
            self.assertEqual(data["workbench.editorAssociations"]["*.md"], "default")

    def test_save_settings_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".vscode" / "settings.json"
            MODULE.save_settings(path, {"workbench.editorAssociations": {"*.md": "default"}})
            self.assertIn('"*.md": "default"', path.read_text(encoding="utf-8"))

    def test_fabriqa_mode_sets_editor_association(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / ".vscode" / "settings.json"
            data = {}
            associations = data.get("workbench.editorAssociations") or {}
            associations["*.md"] = MODULE.FABRIQA_VIEW_TYPE
            data["workbench.editorAssociations"] = associations
            MODULE.save_settings(settings_path, data)

            written = MODULE.load_settings(settings_path)
            self.assertEqual(
                written["workbench.editorAssociations"]["*.md"],
                MODULE.FABRIQA_VIEW_TYPE,
            )

    def test_text_mode_sets_default_editor_association(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / ".vscode" / "settings.json"
            data = {}
            associations = data.get("workbench.editorAssociations") or {}
            associations["*.md"] = "default"
            data["workbench.editorAssociations"] = associations
            MODULE.save_settings(settings_path, data)

            written = MODULE.load_settings(settings_path)
            self.assertEqual(
                written["workbench.editorAssociations"]["*.md"],
                "default",
            )

    def test_clear_mode_removes_empty_association_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / ".vscode" / "settings.json"
            MODULE.save_settings(
                settings_path,
                {"workbench.editorAssociations": {"*.md": "default"}},
            )
            data = MODULE.load_settings(settings_path)
            associations = data["workbench.editorAssociations"]
            associations.pop("*.md", None)
            if associations:
                data["workbench.editorAssociations"] = associations
            else:
                data.pop("workbench.editorAssociations", None)
            MODULE.save_settings(settings_path, data)

            written = MODULE.load_settings(settings_path)
            self.assertNotIn("workbench.editorAssociations", written)

    def test_load_settings_rejects_non_object_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".vscode" / "settings.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('["not-an-object"]\n', encoding="utf-8")
            with self.assertRaises(SystemExit) as ctx:
                MODULE.load_settings(path)
            self.assertIn("Settings root must be an object", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
