import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from envscope.cli import main


class EnvScopeTests(unittest.TestCase):
    def test_missing_and_unused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "app.py").write_text('import os\nos.getenv("API_KEY")\nos.environ["PORT"]\n')
            (root / "web.ts").write_text('process.env["BASE_URL"]')
            (root / ".env.example").write_text("PORT=3000\nOLD_FLAG=\n")
            output = StringIO()
            with redirect_stdout(output):
                status = main([str(root), "--json"])
            result = json.loads(output.getvalue())
            self.assertEqual(status, 1)
            self.assertEqual(set(result["missing"]), {"API_KEY", "BASE_URL"})
            self.assertEqual(result["unused"], ["OLD_FLAG"])

    def test_clean(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "app.py").write_text('import os\nos.getenv("PORT")\n')
            (root / ".env.example").write_text("PORT=3000\n")
            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(root)]), 0)


if __name__ == "__main__":
    unittest.main()
