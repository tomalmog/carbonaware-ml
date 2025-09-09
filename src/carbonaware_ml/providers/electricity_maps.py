from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

import requests

from .base import CarbonIntensity, CarbonIntensityProvider


ELECTRICITYMAPS_BASE = "https://api.electricitymaps.com/v3"


class ElectricityMapsProvider(CarbonIntensityProvider):
    def __init__(
        self,
        api_token: Optional[str] = None,
        email: Optional[str] = None,
        emission_factor_type: str = "lifecycle",
        disable_estimations: bool = False,
        temporal_granularity: str = "hourly",
    ) -> None:
        self._api_token = api_token or os.environ.get("ELECTRICITYMAPS_API_TOKEN")
        self._email = email or os.environ.get("ELECTRICITYMAPS_EMAIL")
        self.emission_factor_type = emission_factor_type
        self.disable_estimations = disable_estimations
        self.temporal_granularity = temporal_granularity

    def get_current_intensity(self, region: Optional[str] = None) -> CarbonIntensity:
        if not self._api_token:
            raise RuntimeError("Electricity Maps API token not set")
        if not region:
            raise ValueError("region must be provided, e.g., 'CA-ON'")

        url = f"{ELECTRICITYMAPS_BASE}/carbon-intensity/latest"
        headers = {"auth-token": self._api_token}
        params = {
            "zone": region,
            "emissionFactorType": self.emission_factor_type,
            "disableEstimations": str(self.disable_estimations).lower(),
            "temporalGranularity": self.temporal_granularity,
        }
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 401 and self._email:
            resp = requests.get(url, params=params, timeout=15, auth=(self._email, self._api_token))
        resp.raise_for_status()
        data = resp.json()
        intensity = float(data.get("carbonIntensity", 0.0))
        return CarbonIntensity(grams_co2_per_kwh=intensity, as_of_epoch_s=0)

    def get_history_intensity(
        self,
        region: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not self._api_token:
            raise RuntimeError("Electricity Maps API token not set")
        if not region:
            raise ValueError("region must be provided, e.g., 'CA-ON'")

        url = f"{ELECTRICITYMAPS_BASE}/carbon-intensity/history"
        headers = {"auth-token": self._api_token}
        params: Dict[str, Any] = {
            "zone": region,
            "emissionFactorType": self.emission_factor_type,
            "disableEstimations": str(self.disable_estimations).lower(),
            "temporalGranularity": self.temporal_granularity,
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 401 and self._email:
            resp = requests.get(url, params=params, timeout=15, auth=(self._email, self._api_token))
        resp.raise_for_status()
        data = resp.json()
        results = data.get("history") or data.get("data") or []
        return results  # type: ignore[return-value]


