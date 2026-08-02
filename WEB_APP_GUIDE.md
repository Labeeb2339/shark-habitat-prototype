# Web interface reference

The Streamlit interface is a viewer for deterministic prototype score
surfaces. It is designed for software experiments and demonstrations, not
wildlife tracking.

## Sidebar controls

- **Species** selects an illustrative parameter profile.
- **Study area** sets a bounding box. Presets are interface conveniences, not
  confirmed animal locations.
- **Date range** is recorded in the run settings. It does not currently alter
  the generated environmental values.
- **Generate Prototype Score** executes the scoring pipeline.

## Result panels

### Habitat map

Shows the relative heuristic score over the generated grid. It does not show
shark positions or presence probabilities.

### Distribution

Summarizes how many grid cells fall into each score band. “Excellent,” “good,”
and similar labels refer only to thresholds in this program.

### Component breakdown

Helps inspect how temperature, productivity, frontal-zone, depth, and other
hand-built factors contribute to the score.

### Detailed report

Exports the run settings and software output. It is not a scientific report or
evidence of ecological accuracy.

## What changes when you edit controls

The app recalculates a score surface after you submit a run. This is an
interactive recomputation, not a stream of current ocean or animal telemetry.

Changing the species profile can be useful for checking whether the code
responds differently to different parameter sets. It does not establish that
the profiles are biologically complete or calibrated.

## Data-status labels

The Streamlit workflow uses deterministic generated grids. Python callers can
opt into a NASA Common Metadata Repository (CMR) catalog lookup, but its results
remain separate metadata and do not populate the score grid.

Until a future data adapter records dataset identifiers, acquisition timestamps,
units, transformations, masks, and fallback status for every layer, treat every
public result as a software demonstration.

## Safe uses

- Explore a Streamlit and Plotly application
- Trace a heuristic from inputs to a score
- Test deterministic behavior
- Compare software changes under a fixed seed
- Design a future provenance-aware data adapter

## Unsupported uses

- Finding or tracking sharks
- Choosing dive, fishing, or navigation locations
- Conservation or policy decisions
- Claiming model accuracy, reliability, or ecological validation
- Publishing the generated map as an observational result

See [USER_GUIDE.md](USER_GUIDE.md) for setup and
[README.md](README.md) for the project evidence boundary.
