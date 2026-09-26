"""Run the workflow's actual immutable-ref gate with valid and moving refs."""

from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest


class VerificationRefTests(unittest.TestCase):
    def test_workflow_rejects_mutable_refs_before_starting_builds(self):
        workflow = (
            Path(__file__).resolve().parents[1] / ".github/workflows/verify.yml"
        ).read_text()
        code = textwrap.dedent(
            re.search(r"python - <<'PY'\n(.*?)\n          PY", workflow, re.S)[1]
        )
        for ref in ("main", "v0.8.6", "abc123", "a" * 40):
            with self.subTest(ref=ref), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "outputs"
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    env=dict(os.environ, REQUESTED_REF=ref, GITHUB_OUTPUT=str(output)),
                    capture_output=True,
                    text=True,
                )
                if len(ref) == 40:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(output.read_text(), "sha=" + ref + "\n")
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("full commit SHA", result.stderr)
                    self.assertFalse(output.exists())
