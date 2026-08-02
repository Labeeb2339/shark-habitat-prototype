import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_GUIDES = (
    "README.md",
    "USER_GUIDE.md",
    "WEB_APP_GUIDE.md",
    "WHAT_YOU_GET.md",
    "NASA_TOKEN_SETUP.md",
    "SPECIES_GUIDE.md",
)


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

    def test_retired_fake_validation_code_is_absent(self):
        source = (ROOT / "automatic_nasa_framework.py").read_text(
            encoding="utf-8"
        ).casefold()

        retired_identifiers = (
            "_initialize_telemetry_validator",
            "validate_with_telemetry",
            "cross_validate_model",
            "tag_locations",
            "fisheries_cpue",
            "10/10 accuracy",
        )

        for identifier in retired_identifiers:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, source)

    def test_public_guides_do_not_repeat_retired_product_claims(self):
        source = "\n".join(
            (ROOT / name).read_text(encoding="utf-8") for name in PUBLIC_GUIDES
        ).casefold()

        retired_claims = (
            "not fake or simulated",
            "actual satellite measurements",
            "updated every few hours",
            "validated accuracy",
            "professional-grade data",
            "professional-quality figures",
            "predict where sharks are",
            "scientific predictions",
            "used by researchers",
        )

        for claim in retired_claims:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, source)

    def test_each_primary_guide_states_the_prototype_boundary(self):
        for name in ("README.md", "USER_GUIDE.md", "WEB_APP_GUIDE.md", "WHAT_YOU_GET.md"):
            with self.subTest(name=name):
                source = (ROOT / name).read_text(encoding="utf-8").casefold()
                self.assertIn("prototype", source)
                self.assertTrue(
                    "not" in source or "unsupported" in source,
                    f"{name} must state what the prototype cannot establish",
                )


if __name__ == "__main__":
    unittest.main()
