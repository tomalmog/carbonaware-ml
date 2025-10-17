from __future__ import annotations

from typing import Optional


class TensorBoardLogger:
    """Lightweight wrapper that is a no-op if tensorboard is not installed."""

    def __init__(self, log_dir: Optional[str] = None) -> None:
        self._writer = None
        try:
            from torch.utils.tensorboard import SummaryWriter  # type: ignore

            self._writer = SummaryWriter(log_dir=log_dir)
        except Exception:
            self._writer = None

    def log_scalar(self, tag: str, value: float, step: int) -> None:
        if self._writer is not None:
            try:
                self._writer.add_scalar(tag, value, step)
            except Exception:
                pass

    def close(self) -> None:
        if self._writer is not None:
            try:
                self._writer.close()
            except Exception:
                pass


