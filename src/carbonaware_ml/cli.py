from __future__ import annotations

import argparse
import os

from .providers import ElectricityMapsProvider, OntarioTOUPriceProvider


def cmd_intensity(args: argparse.Namespace) -> int:
    region = args.region or os.environ.get("CARBONAWARE_REGION")
    if not region:
        raise SystemExit("Region is required. Pass --region or set CARBONAWARE_REGION.")
    provider = ElectricityMapsProvider()
    ci = provider.get_current_intensity(region=region)
    print(f"{region} intensity: {ci.grams_co2_per_kwh:.1f} gCO2/kWh")
    return 0


def cmd_price(args: argparse.Namespace) -> int:
    region = args.region or os.environ.get("CARBONAWARE_REGION")
    if not region:
        raise SystemExit("Region is required. Pass --region or set CARBONAWARE_REGION.")
    provider = OntarioTOUPriceProvider()
    price = provider.get_current_price(region=region)
    print(f"{region} price: {price.cents_per_kwh:.2f} c/kWh")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="carbonaware", description="Carbon-aware ML utilities")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_int = sub.add_parser("intensity", help="Print current carbon intensity")
    p_int.add_argument("--region", default=None, help="e.g., CA-ON; or set CARBONAWARE_REGION")
    p_int.set_defaults(func=cmd_intensity)

    p_price = sub.add_parser("price", help="Print current price (TOU demo)")
    p_price.add_argument("--region", default=None, help="e.g., CA-ON; or set CARBONAWARE_REGION")
    p_price.set_defaults(func=cmd_price)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


