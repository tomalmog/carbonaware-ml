from __future__ import annotations

import os
from typing import Iterable, Tuple
import sys

import torch
from torch.utils.data import DataLoader, TensorDataset

from carbonaware_ml import CarbonAwareTrainer
from carbonaware_ml import providers


def make_dummy_data(n: int = 1024) -> DataLoader:
    x = torch.randn(n, 10)
    w = torch.randn(10, 1)
    y = x @ w + 0.1 * torch.randn(n, 1)
    ds = TensorDataset(x, y)
    return DataLoader(ds, batch_size=64, shuffle=True)


def main() -> None:
    model = torch.nn.Sequential(torch.nn.Linear(10, 32), torch.nn.ReLU(), torch.nn.Linear(32, 1))
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    dataloader = make_dummy_data()

    carbon = None
    token = os.environ.get("ELECTRICITYMAPS_API_TOKEN")
    if token:
        carbon = providers.ElectricityMapsProvider(api_token=token)

    region = os.environ.get("CARBONAWARE_REGION")
    if not region:
        print("Error: CARBONAWARE_REGION is not set. Set it to your authorized zone (e.g., CA-ON).", file=sys.stderr)
        raise SystemExit(2)

    trainer = CarbonAwareTrainer(
        model=model,
        optimizer=optimizer,
        dataloader=dataloader,
        region=region,
        carbon_provider=carbon,
        price_provider=providers.OntarioTOUPriceProvider(),
    )

    trainer.train_until_green(threshold=200, num_epochs=3, check_interval_s=300, price_threshold_cents=13.0)


if __name__ == "__main__":
    main()


