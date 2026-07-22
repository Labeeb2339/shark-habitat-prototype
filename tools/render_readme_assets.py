#!/usr/bin/env python3
"""Render a deterministic README plot from the prototype's scoring code."""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automatic_nasa_framework import AutomaticNASAFramework  # noqa: E402


OUTPUT = ROOT / "assets" / "temperature-response.svg"
SPECIES = (
    ("great_white", "Great white", "#184e77"),
    ("tiger_shark", "Tiger shark", "#e76f51"),
    ("whale_shark", "Whale shark", "#2a9d8f"),
)
TEMPERATURES = tuple(value / 2 for value in range(16, 69))


def x_position(temperature: float) -> float:
    return 86 + (temperature - 8) / 26 * 744


def y_position(suitability: float) -> float:
    return 486 - suitability * 330


def render() -> str:
    curves = []
    legends = []
    ranges = []
    for index, (key, label, color) in enumerate(SPECIES):
        with contextlib.redirect_stdout(io.StringIO()):
            framework = AutomaticNASAFramework(species=key, seed=2339)
        values = [framework._bioenergetic_temperature_model(temp)[0] for temp in TEMPERATURES]
        path = " ".join(
            f"{'M' if point_index == 0 else 'L'} {x_position(temp):.2f} {y_position(value):.2f}"
            for point_index, (temp, value) in enumerate(zip(TEMPERATURES, values, strict=True))
        )
        curves.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="5" stroke-linejoin="round"/>')
        legends.append(
            f'<circle cx="922" cy="{211 + index * 54}" r="7" fill="{color}"/>'
            f'<text x="942" y="{217 + index * 54}" class="legend">{label}</text>'
        )
        low, high = framework.shark_params["temp_range"]
        ranges.append(
            f'<line x1="{x_position(low):.2f}" y1="{132 + index * 8}" x2="{x_position(high):.2f}" y2="{132 + index * 8}" '
            f'stroke="{color}" stroke-width="5" stroke-linecap="round" opacity="0.75"/>'
        )

    x_ticks = []
    for temperature in (10, 15, 20, 25, 30):
        x = x_position(temperature)
        x_ticks.append(
            f'<path d="M{x:.2f} 486 V496" stroke="#7891a3"/>'
            f'<text x="{x:.2f}" y="520" text-anchor="middle" class="axis">{temperature}°C</text>'
        )

    y_ticks = []
    for value in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = y_position(value)
        y_ticks.append(
            f'<path d="M86 {y:.2f} H830" stroke="#d7e5ec"/>'
            f'<text x="67" y="{y + 5:.2f}" text-anchor="end" class="axis">{value:.2f}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="620" viewBox="0 0 1280 620" role="img" aria-labelledby="title desc">
  <title id="title">Unvalidated shark habitat prototype temperature response</title>
  <desc id="desc">Line chart generated from the current heuristic temperature function for great white, tiger, and whale sharks. It is a software-behaviour visualization and is not evidence of shark presence or ecological accuracy.</desc>
  <style>
    .title {{ font: 800 34px system-ui, sans-serif; fill: #11344a; }}
    .subtitle {{ font: 16px system-ui, sans-serif; fill: #547181; }}
    .axis {{ font: 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #547181; }}
    .axis-title {{ font: 700 15px system-ui, sans-serif; fill: #315b70; }}
    .panel-kicker {{ font: 800 13px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; letter-spacing: 2px; fill: #77d6c8; }}
    .panel-title {{ font: 750 21px system-ui, sans-serif; fill: #f1fbff; }}
    .legend {{ font: 16px system-ui, sans-serif; fill: #e9f5f8; }}
    .note {{ font: 14px system-ui, sans-serif; fill: #bdd1d9; }}
  </style>
  <rect width="1280" height="620" rx="30" fill="#f3f9fb"/>
  <path d="M0 96 H1280" stroke="#c7dce5"/>
  <text x="56" y="50" class="title">HEURISTIC TEMPERATURE RESPONSE</text>
  <text x="56" y="78" class="subtitle">Generated from the current scoring function · software behaviour, not ecological validation</text>

  <g>
    {''.join(y_ticks)}
    {''.join(x_ticks)}
    <path d="M86 156 V486 H830" fill="none" stroke="#7891a3" stroke-width="2"/>
    {''.join(ranges)}
    {''.join(curves)}
    <text x="458" y="563" text-anchor="middle" class="axis-title">SEA-SURFACE TEMPERATURE INPUT</text>
    <text x="24" y="321" text-anchor="middle" class="axis-title" transform="rotate(-90 24 321)">HEURISTIC SUITABILITY</text>
    <text x="86" y="119" class="axis">declared temperature ranges</text>
  </g>

  <g transform="translate(868 126)">
    <rect width="356" height="404" rx="24" fill="#10384b"/>
    <text x="32" y="43" class="panel-kicker">PROTOTYPE BOUNDARY</text>
    <text x="32" y="77" class="panel-title">What this figure means</text>
    {''.join(legends)}
    <path d="M32 267 H324" stroke="#315b70"/>
    <text x="32" y="299" class="note">✓ current code path</text>
    <text x="32" y="328" class="note">✓ deterministic inputs</text>
    <text x="32" y="357" class="note">✕ tagged-animal validation</text>
    <text x="32" y="386" class="note">✕ evidence of shark presence</text>
  </g>

  <rect x="86" y="578" width="1138" height="1" fill="#c7dce5"/>
  <text x="86" y="602" class="axis">Curves are unvalidated model responses. They must not be used for conservation, navigation, or wildlife claims.</text>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when the committed SVG is stale")
    args = parser.parse_args()
    expected = render()

    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale generated asset: {OUTPUT.relative_to(ROOT)}")
        print(f"up to date: {OUTPUT.relative_to(ROOT)}")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
