import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClaimBoundaryTests(unittest.TestCase):
    def test_public_app_does_not_restore_unvalidated_accuracy_claims(self):
        source = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("app.py", "automatic_nasa_framework.py")
        ).casefold()

        forbidden = (
            "maximum accuracy",
            "competition-winning",
            "fully automatic nasa data integration",
            "real-time nasa satellite data",
            "framework accuracy level: maximum",
        )

        for claim in forbidden:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, source)

    def test_welcome_screen_states_the_evidence_boundary(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")

        self.assertIn("not satellite measurements", source)
        self.assertIn("not a tracking system", source)
        self.assertIn("Scientific, conservation, or policy evidence", source)


if __name__ == "__main__":
    unittest.main()
