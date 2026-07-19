import unittest


try:
    from streamlit.testing.v1 import AppTest
except ModuleNotFoundError:
    AppTest = None


@unittest.skipIf(
    AppTest is None,
    "Streamlit is not installed in the dependency-free CI job",
)
class StreamlitRuntimeTests(unittest.TestCase):
    def test_welcome_screen_renders_without_exceptions(self):
        app = AppTest.from_file("app.py").run(timeout=20)

        self.assertEqual(list(app.exception), [])
        rendered = "\n".join(block.value for block in app.markdown)
        self.assertIn("Shark Habitat Suitability Explorer", rendered)
        self.assertIn("not a tracking system", rendered)
        self.assertNotIn("maximum accuracy", rendered.casefold())


if __name__ == "__main__":
    unittest.main()
