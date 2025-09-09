from __future__ import annotations

from typing import Optional

from .trainer import CarbonAwareTrainer


def run_when_favorable(
    trainer: CarbonAwareTrainer,
    *,
    num_epochs: int,
    threshold: Optional[float] = None,
    price_threshold_cents: Optional[float] = None,
    check_interval_s: int = 300,
):
    """
    Requires APScheduler installed via extras. Periodically checks conditions and
    starts training once favorable. Returns the BackgroundScheduler so callers can keep it alive.
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "APScheduler not installed. Install with `pip install carbonaware-ml[scheduler]`."
        ) from exc

    scheduler = BackgroundScheduler()
    started = {"value": False}

    def _check_and_start():
        if started["value"]:
            return
        green = trainer._is_green_enough(threshold) if threshold is not None else True
        cheap = trainer._is_cheap_enough(price_threshold_cents) if price_threshold_cents is not None else True
        if green and cheap:
            started["value"] = True
            # Run training in a separate job and then shutdown scheduler
            scheduler.add_job(
                lambda: (trainer.train(num_epochs=num_epochs, threshold=threshold, price_threshold_cents=price_threshold_cents), scheduler.shutdown(wait=False)),
                trigger="date",
                run_date=None,
            )

    scheduler.add_job(_check_and_start, "interval", seconds=max(1, check_interval_s))
    scheduler.start()
    return scheduler


