import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JWT_PREFIX = re.compile(r"eyJ[A-Za-z0-9_-]+\.")


class SecretHygieneTests(unittest.TestCase):
    def test_framework_reads_earthdata_token_from_environment(self):
        tree = ast.parse(
            (ROOT / "automatic_nasa_framework.py").read_text(encoding="utf-8")
        )

        assignments = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Attribute)
                and target.attr == "jwt_token"
                for target in node.targets
            )
        ]

        self.assertEqual(len(assignments), 1)
        value = assignments[0].value
        self.assertIsInstance(value, ast.Call)
        self.assertIsInstance(value.func, ast.Attribute)
        self.assertEqual(value.func.attr, "get")
        self.assertEqual(value.args[0].value, "EARTHDATA_TOKEN")

    def test_current_tree_contains_no_jwt_shaped_string(self):
        included_suffixes = {".py", ".md", ".txt", ".yml", ".yaml", ".toml"}
        ignored_directories = {".git", ".venv", ".pytest_cache", "__pycache__"}
        offenders = []

        for path in ROOT.rglob("*"):
            if ignored_directories.intersection(path.parts) or not path.is_file():
                continue
            if path.suffix.lower() not in included_suffixes:
                continue
            if JWT_PREFIX.search(path.read_text(encoding="utf-8", errors="ignore")):
                offenders.append(str(path.relative_to(ROOT)))

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
