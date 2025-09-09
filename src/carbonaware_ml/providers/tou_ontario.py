from __future__ import annotations

from datetime import datetime
from typing import Optional

from .base import PriceProvider, PriceSignal


class OntarioTOUPriceProvider(PriceProvider):
    def __init__(self) -> None:
        self.off_peak = 8.7
        self.mid_peak = 12.2
        self.on_peak = 18.2

    def get_current_price(self, region: Optional[str] = None) -> PriceSignal:
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()
        if weekday >= 5:
            price = self.off_peak
        else:
            if 7 <= hour < 11 or 17 <= hour < 19:
                price = self.on_peak
            elif 11 <= hour < 17:
                price = self.mid_peak
            else:
                price = self.off_peak
        return PriceSignal(cents_per_kwh=price, as_of_epoch_s=int(now.timestamp()))


