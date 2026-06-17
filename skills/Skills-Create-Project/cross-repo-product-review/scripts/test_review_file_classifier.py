from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("review_file_classifier.py")
SPEC = importlib.util.spec_from_file_location("review_file_classifier", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ReviewFileClassifierTests(unittest.TestCase):
    def test_classifies_canonical_buckets(self) -> None:
        cases = {
            "package.json": "host_entry",
            "src/extension.js": "host_entry",
            "src/decision/decision-contract.js": "data_contract",
            "src/decision/slide-shell.js": "feature_seam",
            "src/decision/webview-client.js": "webview_render",
            "src/decision/host-document-state.js": "host_state",
            "src/test/suite/smoke.test.js": "tests",
        }
        for path, expected in cases.items():
            self.assertEqual(MODULE.classify_review_file(path), expected)

    def test_marks_unknown_as_unclassified(self) -> None:
        self.assertEqual(MODULE.classify_review_file("README.md"), "unclassified")


if __name__ == "__main__":
    unittest.main()
