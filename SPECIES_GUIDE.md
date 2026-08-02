# Species profile reference

The prototype contains 24 named shark profiles. Each profile is a collection of
constants used to exercise the scoring code; it is not a reviewed ecological
dataset or evidence that a species occupies a location.

## Current profile keys

- `great_white`
- `tiger_shark`
- `bull_shark`
- `hammerhead`
- `mako`
- `blue_shark`
- `whale_shark`
- `basking_shark`
- `thresher_shark`
- `nurse_shark`
- `reef_shark`
- `lemon_shark`
- `blacktip_shark`
- `sandbar_shark`
- `spinner_shark`
- `dusky_shark`
- `silky_shark`
- `porbeagle_shark`
- `longfin_mako`
- `salmon_shark`
- `sand_tiger`
- `scalloped_hammerhead`
- `smooth_hammerhead`
- `bonnethead_shark`

Read scoring values from the framework implementation:

```python
from automatic_nasa_framework import AutomaticNASAFramework

framework = AutomaticNASAFramework(seed=2339)

for key, profile in framework.shark_species_params.items():
    print(
        key,
        profile["name"],
        profile["optimal_temp"],
        profile["depth_preference"],
    )
```

`app.py` also contains display labels for the interface. Those labels do not
change the scoring parameters and should be kept key-for-key aligned with the
framework profiles.

## How parameters affect the prototype

Profiles can contain values such as:

- preferred temperature and temperature tolerance;
- depth range and depth-response settings;
- productivity and frontal-zone weights;
- coastal affinity and migration tendency;
- prey, water-quality, and temporal heuristic settings.

The scoring functions combine these constants with generated environmental
grids. A changed score means the software responded to a changed parameter. It
does not demonstrate biological correctness.

## Useful experiments

- Hold the generated grid and seed fixed, then compare two profiles.
- Change one parameter at a time and plot the score delta.
- Add a unit test for the expected direction of a response.
- Check that every profile produces finite values in the `[0, 1]` range.

Do not use the profiles to choose a dive, fishing, navigation, conservation, or
fieldwork location.

## Path to evidence-backed profiles

Before describing any profile as ecological evidence:

1. cite an authoritative source for every parameter;
2. record units, population, geography, life stage, and date range;
3. separate fitted parameters from fixed assumptions;
4. evaluate against a named animal-observation dataset with frozen spatial and
   temporal splits; and
5. obtain domain review.

Until that work is complete, the profiles are transparent software fixtures.
