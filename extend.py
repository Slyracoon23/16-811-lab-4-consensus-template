"""The half that is yours: buy the topology that maximises lambda_2 under an edge budget.

Switches, not branches. The measure has to be the same one `reproduce.py` reports.
"""

from __future__ import annotations

import argparse
import json

VARIANTS = ["given", "max-fiedler", "spectral-layout", "live-rewire"]


def run(variant: str, seed: int) -> float:
    """Return the measured decay rate for this topology strategy."""
    raise NotImplementedError(f"Your idea: {variant}. See 'Past the paper' on the lab sheet.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--seeds", type=int, default=5)
    args = parser.parse_args()
    chosen = VARIANTS if args.all else [args.variant or "given"]
    records = [{"variant": v, "seed": s, "rate": run(v, s)} for v in chosen for s in range(args.seeds)]
    with open("extensions.json", "w") as handle:
        json.dump({"records": records}, handle, indent=2)
    print(f"{len(records)} records into extensions.json")


if __name__ == "__main__":
    main()
