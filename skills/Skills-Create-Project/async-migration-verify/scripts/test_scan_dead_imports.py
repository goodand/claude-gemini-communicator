import pathlib
import subprocess
import tempfile


SCRIPT = pathlib.Path(__file__).with_name("scan_dead_imports.sh")


def run_scan(contents: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        target = pathlib.Path(tmpdir) / "sample.js"
        target.write_text(contents, encoding="utf-8")
        result = subprocess.run(
            ["bash", str(SCRIPT), tmpdir],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout


def test_reports_bare_and_node_prefixed_fs_imports():
    output = run_scan(
        "const fs = require('fs');\n"
        "const nodeFs = require('node:fs');\n"
        "fs.readFileSync('x');\n"
    )
    assert "require('fs')" in output
    assert "require('node:fs')" in output
    assert "readFileSync" in output
