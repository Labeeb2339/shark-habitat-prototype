import unittest


try:
    from automatic_nasa_framework import AutomaticNASAFramework
except ModuleNotFoundError:
    AutomaticNASAFramework = None


@unittest.skipIf(
    AutomaticNASAFramework is None,
    "runtime dependencies are not installed in the dependency-free CI job",
)
class FrameworkRuntimeTests(unittest.TestCase):
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
