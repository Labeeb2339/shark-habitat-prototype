# User guide

Shark Habitat Prototype is an educational software demo. It lets you inspect
how a configurable heuristic turns environmental inputs into a relative
suitability score.

It does **not** locate sharks, estimate the probability of shark presence, or
provide a validated ecological result.

## Run the app

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local address printed by Streamlit, usually
`http://localhost:8501`.

## Try the workflow

1. Select one of the prototype species profiles.
2. Choose a preset bounding box or enter coordinates.
3. Choose a date range.
4. Run the scoring workflow.
5. Compare the score surface and component charts.

The useful question is: “How did the software respond to these inputs?” The
output cannot answer: “Are sharks present here?”

## Input and provenance boundary

| Item | What it currently means |
| --- | --- |
| Species profile | An illustrative parameter set implemented in code |
| Date and bounds | Run settings; bounds shape the generated grid, while dates do not currently alter its values |
| NASA CMR result | Optional catalog metadata when `lookup_metadata=True` is used in Python |
| SST/chlorophyll grid | Deterministic generated values in the main workflow |
| Bathymetry grid | A generated prototype layer |
| HSI | A relative heuristic software score, not a calibrated probability |

A successful opt-in CMR search does not change the displayed grid or prove that
it contains retrieved satellite measurements.

## Reading the output

- Use high and low scores to compare cells within the same prototype run.
- Use component charts to understand which heuristic affected the result.
- Keep the seed fixed when comparing code or parameter changes.
- Do not compare a score to a real animal sighting as if it were a model
  prediction.
- Do not use the maps for navigation, conservation, safety, fieldwork, or
  policy decisions.

Labels such as “excellent” and “poor” are score bands in the interface. They
are not ecological quality grades.

## Earthdata token

The generated Streamlit prototype does not require a credential. Experimental
Earthdata request paths read `EARTHDATA_TOKEN` from the current process. See
[NASA_TOKEN_SETUP.md](NASA_TOKEN_SETUP.md).

Supplying a token does not turn the application into a live-data or validated
system.

## Troubleshooting

### The app starts but a run fails

- Confirm the dependencies installed successfully.
- Check the coordinate order: west, south, east, north.
- Try the default study area and a smaller date range.
- If you explicitly enabled the metadata lookup, check the network connection.

### Results differ between runs

Generated values are deterministic only when the same seed and call sequence
are used. The default seed is `2339`.

### I need ecological results

This repository is not the right tool yet. A credible ecological workflow
would need named observation datasets, documented transformations, spatially
appropriate train/test splits, uncertainty analysis, and domain review.

## Verify the checkout

```bash
python -m compileall -q app.py automatic_nasa_framework.py tests
python -m unittest discover -s tests -v
python tools/render_readme_assets.py --check
```
