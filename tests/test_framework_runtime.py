import unittest
from unittest.mock import patch


try:
    from automatic_nasa_framework import AutomaticNASAFramework
except ModuleNotFoundError:
    AutomaticNASAFramework = None


@unittest.skipIf(
    AutomaticNASAFramework is None,
    "runtime dependencies are not installed in the dependency-free CI job",
)
class FrameworkRuntimeTests(unittest.TestCase):
    def test_ui_and_framework_species_keys_match(self):
        from app import load_species_data

        framework = AutomaticNASAFramework(seed=2339)
        self.assertEqual(
            set(load_species_data()),
            set(framework.shark_species_params),
        )

    def test_default_prototype_mode_is_offline_and_explicitly_generated(self):
        framework = AutomaticNASAFramework(seed=2339)
        study_area = {
            "name": "Offline fixture",
            "bounds": [-125.0, 32.0, -117.0, 42.0],
        }

        with patch(
            "automatic_nasa_framework.requests.get",
            side_effect=AssertionError("default prototype mode must not use network"),
        ):
            environmental_data, metadata_status = framework.auto_download_nasa_data(
                study_area,
                ("2024-01-01", "2024-01-31"),
            )

        self.assertEqual(metadata_status["metadata_lookup"], "skipped")
        self.assertEqual(
            environmental_data["sst"]["source"],
            "Deterministic generated prototype",
        )
        self.assertEqual(
            environmental_data["chlorophyll"]["source"],
            "Deterministic generated prototype",
        )
        self.assertEqual(
            environmental_data["bathymetry"]["source"],
            "Prototype bathymetry input",
        )

    def test_fake_validation_api_is_not_exposed(self):
        framework = AutomaticNASAFramework(seed=2339)

        self.assertFalse(hasattr(framework, "telemetry_validator"))
        self.assertFalse(hasattr(framework, "validate_with_telemetry"))
        self.assertFalse(hasattr(framework, "cross_validate_model"))

    def test_generated_sst_grid_is_deterministic_for_the_same_seed(self):
        bounds = [-125.0, 32.0, -117.0, 42.0]
        granules = [{"title": "SST metadata fixture"}]

        first = AutomaticNASAFramework(seed=2339)
        second = AutomaticNASAFramework(seed=2339)

        self.assertEqual(
            first._process_sst_granules(granules, bounds, 5),
            second._process_sst_granules(granules, bounds, 5),
        )

    def test_generated_sst_grid_changes_with_seed(self):
        bounds = [-125.0, 32.0, -117.0, 42.0]
        granules = [{"title": "SST metadata fixture"}]

        first = AutomaticNASAFramework(seed=2339)
        second = AutomaticNASAFramework(seed=2340)

        self.assertNotEqual(
            first._process_sst_granules(granules, bounds, 5),
            second._process_sst_granules(granules, bounds, 5),
        )


if __name__ == "__main__":
    unittest.main()
