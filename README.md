### Carbon Aware ML

[![PyPI version](https://img.shields.io/pypi/v/carbonaware-ml.svg)](https://pypi.org/project/carbonaware-ml/)
[![Downloads](https://pepy.tech/badge/carbonaware-ml)](https://pepy.tech/project/carbonaware-ml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Carbon-aware training for PyTorch that pauses or schedules training based on real-time grid carbon intensity (and optionally electricity prices). Works in any region supported by Electricity Maps or WattTime. Each user supplies their own API credentials and region.

#### Installation

```bash
pip install 'carbonaware-ml[all]'         # includes scheduler + tensorboard extras
# or minimal
pip install carbonaware-ml

# zsh users: extras must be quoted
```

#### Configure environment

```bash
export CARBONAWARE_REGION="CA-ON"                 # your authorized zone (e.g., US-CAL-CISO, DE)
export ELECTRICITYMAPS_API_TOKEN="<your_token>"   # required for Electricity Maps
# Optional if your plan requires Basic Auth
export ELECTRICITYMAPS_EMAIL="you@example.com"

# Optional WattTime instead of Electricity Maps
# export WATTTIME_USERNAME="<user>"
# export WATTTIME_PASSWORD="<pass>"
```

#### Quickstart (Python)

```python
import os
from carbonaware_ml import CarbonAwareTrainer, providers

# model/optimizer/dataloader are your own objects
trainer = CarbonAwareTrainer(
    model=my_model,
    optimizer=my_optimizer,
    dataloader=my_dataloader,
    region=os.environ.get("CARBONAWARE_REGION"),
    carbon_provider=providers.ElectricityMapsProvider(),
)

# Start only when favorable
trainer.train_until_green(threshold=200, num_epochs=3)

# Or train now, pausing when conditions exceed thresholds
trainer.train(num_epochs=3, threshold=200, check_interval_s=300)
```

Providers:
- Electricity Maps (real-time/forecast carbon intensity)
  - Env: `ELECTRICITYMAPS_API_TOKEN` (required), `ELECTRICITYMAPS_EMAIL` (optional for Basic Auth)
- WattTime (alternative intensity source via `WATTTIME_USERNAME`/`WATTTIME_PASSWORD`)

If no external provider is configured, the trainer defaults to an "always-allow" mode.

#### CLI

```bash
# Use env region or pass explicitly
carbonaware intensity --region "$CARBONAWARE_REGION"
carbonaware price --region "$CARBONAWARE_REGION"
```

#### TensorBoard (optional)

```python
trainer = CarbonAwareTrainer(..., tb_log_dir="runs/demo")
```

#### Scheduler (optional)

```python
from carbonaware_ml.scheduler import run_when_favorable
sched = run_when_favorable(trainer, num_epochs=1, threshold=150, price_threshold_cents=12.0, check_interval_s=300)
```

#### Author

- Tom Almog (https://github.com/tomalmog)

#### License

MIT
