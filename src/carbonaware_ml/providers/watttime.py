from __future__ import annotations

import os
from typing import Optional

import requests

from .base import CarbonIntensity, CarbonIntensityProvider


WATTTIME_BASE = "https://api2.watttime.org/v2"


class WattTimeProvider(CarbonIntensityProvider):
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self._username = username or os.environ.get("WATTTIME_USERNAME")
        self._password = password or os.environ.get("WATTTIME_PASSWORD")

    def _auth(self) -> tuple[str, str]:
        if not self._username or not self._password:
            raise RuntimeError("WattTime credentials not set")
        return (self._username, self._password)

    def get_current_intensity(self, region: Optional[str] = None) -> CarbonIntensity:
        if not region:
            raise ValueError("region must be provided (e.g., 'CA-ON')")
        resp = requests.get(
            f"{WATTTIME_BASE}/index",
            params={"ba": region},
            auth=self._auth(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        grams = float(data.get("mi") or 0.0)
        return CarbonIntensity(grams_co2_per_kwh=grams, as_of_epoch_s=0)


