#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("build_obsidian_caption_review.py")
SPEC = importlib.util.spec_from_file_location("build_obsidian_caption_review", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CommandBuilderTests(unittest.TestCase):
    def setUp(self):
        self._old_root_script = MODULE.ROOT_SCRIPT
        self.tempdir = tempfile.TemporaryDirectory()
        self.root_script = Path(self.tempdir.name) / "root_review_builder.py"
        self.root_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        MODULE.ROOT_SCRIPT = self.root_script

    def tearDown(self):
        MODULE.ROOT_SCRIPT = self._old_root_script
        self.tempdir.cleanup()

    def make_args(self, **overrides):
        base = dict(
            ledger_glob="control/project_agent_ops/registry/jobs/image_caption_jobs/*.json",
            exclude_glob=["*smoke*"],
            output=str(Path(self.tempdir.name) / "reports" / "review.md"),
            review_title="Caption Review",
            mode="canonical-copy",
            asset_dir=None,
            source_root=None,
            embed_prefix=None,
        )
        base.update(overrides)
        return Namespace(**base)

    def test_default_asset_dir(self):
        output = Path("/tmp/example/reports/review.md")
        expected = Path("/tmp/example/reports/review_assets/review")
        self.assertEqual(MODULE.default_asset_dir(output), expected)

    def test_canonical_copy_uses_default_asset_dir(self):
        args = self.make_args(mode="canonical-copy")
        command = MODULE.build_root_command(args)
        self.assertIn("--copy-assets", command)
        self.assertIn("--asset-dir", command)
        self.assertIn(
            str(Path(args.output).resolve().parent / "review_assets" / Path(args.output).stem),
            command,
        )

    def test_canonical_copy_honors_explicit_asset_dir(self):
        asset_dir = Path(self.tempdir.name) / "custom_assets"
        args = self.make_args(mode="canonical-copy", asset_dir=str(asset_dir))
        command = MODULE.build_root_command(args)
        self.assertIn(str(asset_dir.resolve()), command)

    def test_direct_mode_rejects_extra_path_args(self):
        args = self.make_args(mode="direct", asset_dir=str(Path(self.tempdir.name) / "assets"))
        with self.assertRaises(SystemExit) as ctx:
            MODULE.build_root_command(args)
        self.assertIn("--mode direct does not accept", str(ctx.exception))

    def test_prefixed_mode_requires_both_path_args(self):
        args = self.make_args(mode="prefixed", source_root=str(Path(self.tempdir.name) / "src"))
        with self.assertRaises(SystemExit) as ctx:
            MODULE.build_root_command(args)
        self.assertIn("--mode prefixed requires both --source-root and --embed-prefix", str(ctx.exception))

    def test_prefixed_mode_adds_source_root_and_embed_prefix(self):
        source_root = Path(self.tempdir.name) / "source"
        args = self.make_args(
            mode="prefixed",
            source_root=str(source_root),
            embed_prefix="img/pptx_jobs",
        )
        command = MODULE.build_root_command(args)
        self.assertIn("--source-root", command)
        self.assertIn(str(source_root.resolve()), command)
        self.assertIn("--embed-prefix", command)
        self.assertIn("img/pptx_jobs", command)


if __name__ == "__main__":
    unittest.main()
