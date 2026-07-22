# Shark Habitat Prototype

I built this Python and Streamlit prototype to explore how environmental
variables might be combined into a shark-habitat suitability score.

This repository is a **learning prototype**, not a wildlife-tracking system, validated ecological model, or research product.

## What it currently demonstrates

- A Streamlit interface for selecting species and study settings
- Species-specific preference tables and heuristic suitability scoring
- Map and chart generation with pandas, NumPy, Plotly, and related tools
- An early workflow shaped around sea-surface temperature, chlorophyll, and bathymetry inputs

## Important limits

- The current environmental layers used by the main prototype are simulated or generated in code.
- Generated paths use a fixed default seed (`2339`) so the same workflow is reproducible.
- The repository does not provide live shark locations or confirm that sharks are present in a suggested area.
- The habitat scores have not been validated against tagged-animal observations, field surveys, or peer-reviewed ecological benchmarks.
- No claim of professional accuracy, research-grade quality, real-time satellite ingestion, or conservation suitability is made.
- Some older guide files describe the intended live-data direction more strongly than the implemented and verified behaviour. Treat them as historical prototype notes, not evidence.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The runtime dependency list contains only packages imported by the application or its optional data paths. TensorFlow, scikit-learn, and Matplotlib are not required.

Authenticated NASA Earthdata requests require your own runtime token. See [NASA_TOKEN_SETUP.md](NASA_TOKEN_SETUP.md); the application reads only `EARTHDATA_TOKEN` and does not need a credential committed to the repository.

## Verify the checkout

The repository includes dependency-free checks for Python syntax and current-tree secret hygiene:

```bash
python -m compileall -q app.py automatic_nasa_framework.py tests
python -m unittest discover -s tests -v
```

GitHub Actions runs the same checks for every push and pull request.
It also installs the declared runtime dependencies, starts Streamlit, and checks the health endpoint.

## License

The code is available under the [MIT License](LICENSE). Documentation and external datasets may have their own terms.

## Security note

NASA Earthdata credentials must be supplied at runtime through a local environment variable or another untracked secret store. Never place an access token in source code, examples, screenshots, issues, or commits.

Before any future public release that enables live ingestion:

1. rotate any credential that was previously committed through the provider;
2. decide separately whether to rewrite Git history;
3. add tests that distinguish real ingestion from simulated fallback data; and
4. record dataset names, timestamps, units, transformations, and failure modes.

## Sensible next steps

- Replace generated layers with a documented public dataset adapter
- Add deterministic fixtures and unit tests for every scoring component
- Compare scores against a named observation dataset
- Attach provenance and uncertainty to every map layer
- Review species parameters with a qualified marine scientist

Until those steps are complete, use this repository only as a software and visualization prototype.
