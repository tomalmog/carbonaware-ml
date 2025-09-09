from __future__ import annotations

from dataclasses import dataclass
import time
import os
from typing import Callable, Iterable, Optional

import torch

from .providers.base import (
    CarbonIntensityProvider,
    AlwaysAllowCarbonProvider,
    PriceProvider,
)
from .utils import get_logger, sleep_seconds
from .logging_tb import TensorBoardLogger


@dataclass
class TrainingConfig:
    check_interval_s: int = 300
    region: Optional[str] = None


class CarbonAwareTrainer:
    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        dataloader: Iterable,
        region: Optional[str] = None,
        carbon_provider: Optional[CarbonIntensityProvider] = None,
        price_provider: Optional[PriceProvider] = None,
        device: Optional[str] = None,
        tb_log_dir: Optional[str] = None,
        price_log_interval_s: int = 60,
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.dataloader = dataloader
        self.region = region or os.environ.get("CARBONAWARE_REGION")
        self.carbon_provider = carbon_provider or AlwaysAllowCarbonProvider()
        self.price_provider = price_provider
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.logger = get_logger("carbonaware.trainer")
        self._tb = TensorBoardLogger(log_dir=tb_log_dir) if tb_log_dir else None
        self._global_step = 0
        self._last_intensity_value: Optional[float] = None
        self._last_price_cents: Optional[float] = None
        self._price_log_interval_s = max(1, int(price_log_interval_s))
        self._last_price_log_ts: float = 0.0

    def _is_green_enough(self, threshold: Optional[float]) -> bool:
        if threshold is None:
            return True
        intensity = self.carbon_provider.get_current_intensity(self.region)
        self.logger.info(
            f"Current carbon intensity: {intensity.grams_co2_per_kwh:.1f} gCO2/kWh; threshold {threshold}"
        )
        self._last_intensity_value = float(intensity.grams_co2_per_kwh)
        if self._tb is not None:
            self._tb.log_scalar("carbon/intensity_g_per_kwh", self._last_intensity_value, self._global_step)
        return intensity.grams_co2_per_kwh <= threshold

    def _is_cheap_enough(self, price_threshold_cents: Optional[float]) -> bool:
        if price_threshold_cents is None or self.price_provider is None:
            return True
        price = self.price_provider.get_current_price(self.region)
        now = time.time()
        if now - self._last_price_log_ts >= self._price_log_interval_s:
            self.logger.info(
                f"Current price: {price.cents_per_kwh:.2f} c/kWh; threshold {price_threshold_cents}"
            )
            self._last_price_log_ts = now
        self._last_price_cents = float(price.cents_per_kwh)
        if self._tb is not None:
            self._tb.log_scalar("price/cents_per_kwh", self._last_price_cents, self._global_step)
        return price.cents_per_kwh <= price_threshold_cents

    def train_until_green(
        self,
        threshold: float,
        num_epochs: int,
        check_interval_s: int = 300,
        loss_fn: Optional[Callable[[torch.Tensor, torch.Tensor], torch.Tensor]] = None,
        price_threshold_cents: Optional[float] = None,
    ) -> None:
        self.logger.info("Waiting for conditions to start training...")
        while not (self._is_green_enough(threshold) and self._is_cheap_enough(price_threshold_cents)):
            sleep_seconds(check_interval_s)
        self.logger.info("Conditions met. Starting training.")
        self.train(
            num_epochs=num_epochs,
            threshold=threshold,
            check_interval_s=check_interval_s,
            loss_fn=loss_fn,
            price_threshold_cents=price_threshold_cents,
        )

    def train(
        self,
        num_epochs: int,
        threshold: Optional[float] = None,
        check_interval_s: int = 300,
        loss_fn: Optional[Callable[[torch.Tensor, torch.Tensor], torch.Tensor]] = None,
        price_threshold_cents: Optional[float] = None,
    ) -> None:
        criterion = loss_fn or torch.nn.MSELoss()
        self.model.train()
        for epoch in range(num_epochs):
            for batch in self.dataloader:
                if (threshold is not None and not self._is_green_enough(threshold)) or (
                    price_threshold_cents is not None and not self._is_cheap_enough(price_threshold_cents)
                ):
                    self.logger.info("Pausing training due to conditions...")
                    while not (
                        (threshold is None or self._is_green_enough(threshold))
                        and (price_threshold_cents is None or self._is_cheap_enough(price_threshold_cents))
                    ):
                        sleep_seconds(check_interval_s)
                    self.logger.info("Resuming training under favorable conditions.")

                inputs, targets = batch
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

                self.optimizer.zero_grad(set_to_none=True)
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                self.optimizer.step()
                if self._tb is not None:
                    self._tb.log_scalar("train/loss", float(loss.detach().cpu().item()), self._global_step)
                self._global_step += 1

            self.logger.info(f"Epoch {epoch + 1}/{num_epochs} completed.")


