# Repository scope

This repository packages a runnable shark-habitat **software prototype**. Its
value is in the interface, deterministic scoring workflow, and explicit path
toward a better data pipeline—not in a claim that it can find sharks.

## Included

- A Streamlit interface for species, area, and date controls
- Illustrative species parameter profiles
- A deterministic heuristic suitability calculation
- Generated SST, chlorophyll, and bathymetry fallback layers
- An opt-in NASA CMR catalog lookup, kept separate from generated grids
- Plotly maps, charts, and downloadable prototype reports
- Unit tests for determinism, runtime startup, secret hygiene, and claim
  boundaries

## Not included

- Live animal telemetry
- A tagged-shark or field-observation dataset
- A trained or calibrated ecological model
- Measured accuracy, reliability, or cross-validation results
- Guaranteed ingestion of satellite measurements
- A basis for safety, conservation, navigation, or policy decisions

The previous hard-coded telemetry example and pseudo-validation routine were
removed because generated locations and random spatial error cannot provide
evidence of model quality.

## What the score means

The Habitat Suitability Index (HSI) is a relative output of hand-built rules.
It is useful for inspecting software behavior. It is not a probability that a
shark is present and it has not been calibrated against observations.

## Verification

Run the checks from the repository root:

```bash
python -m compileall -q app.py automatic_nasa_framework.py tests
python -m unittest discover -s tests -v
python tools/render_readme_assets.py --check
```

## What would make it research-capable

1. Choose named, licensed environmental and animal-observation datasets.
2. Record provenance, units, timestamps, transformations, and fallback status
   for every grid cell.
3. Replace illustrative parameters with a documented model specification.
4. Freeze spatial and temporal evaluation splits before measuring results.
5. Report baselines, uncertainty, failure cases, and negative results.
6. Obtain review from a marine scientist before making ecological claims.

Until then, present the project as a transparent learning prototype.
