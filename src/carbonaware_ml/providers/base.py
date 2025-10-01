from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class CarbonIntensity:
    grams_co2_per_kwh: float
    as_of_epoch_s: int


class CarbonIntensityProvider(Protocol):
    def get_current_intensity(self, region: Optional[str] = None) -> CarbonIntensity:
        ...


@dataclass
class PriceSignal:
    cents_per_kwh: float
    as_of_epoch_s: int


class PriceProvider(Protocol):
    def get_current_price(self, region: Optional[str] = None) -> PriceSignal:
        ...


class AlwaysAllowCarbonProvider:
    def get_current_intensity(self, region: Optional[str] = None) -> CarbonIntensity:
        return CarbonIntensity(grams_co2_per_kwh=0.0, as_of_epoch_s=0)


class StaticPriceProvider:
    def __init__(self, cents_per_kwh: float = 10.0) -> None:
        self._cents_per_kwh = cents_per_kwh

    def get_current_price(self, region: Optional[str] = None) -> PriceSignal:
        return PriceSignal(cents_per_kwh=self._cents_per_kwh, as_of_epoch_s=0)


