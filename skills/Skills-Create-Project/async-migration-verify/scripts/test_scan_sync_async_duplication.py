import pathlib
import subprocess
import tempfile


SCRIPT = pathlib.Path(__file__).with_name("scan_sync_async_duplication.sh")


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


def test_reports_sync_async_pairs_and_validation_helpers():
    output = run_scan(
        "function readThingSync() {}\n"
        "async function readThingAsync() {}\n"
        "function parseThing() {}\n"
        "function validateThing() {}\n"
    )
    assert "readThingSync" in output
    assert "readThingAsync" in output
    assert "parseThing" in output
    assert "validateThing" in output
