### Carbon Aware ML (multi-region)

Carbon-aware training for PyTorch that pauses or schedules training based on real-time grid carbon intensity (and optionally electricity prices). Works in any region supported by Electricity Maps or WattTime. Users supply their own API credentials and desired region.

#### Installation

```bash
pip install -e .
# Optional extras
pip install -e '.[scheduler]'
pip install -e '.[tensorboard]'
pip install -e '.[all]'
```

#### Quickstart

```python
from carbonaware_ml import CarbonAwareTrainer, providers

trainer = CarbonAwareTrainer(
    model=my_model,
    optimizer=my_optimizer,
    dataloader=my_dataloader,
    region=os.environ.get("CARBONAWARE_REGION", "CA-ON"),
    carbon_provider=providers.ElectricityMapsProvider(),
)

# Block until grid intensity is green enough, then train
trainer.train_until_green(threshold=200, num_epochs=3)

# Or always-on training but pausing when above threshold
trainer.train(num_epochs=3, threshold=200, check_interval_s=300)
```

You can also import via `carbonaware_ml`:

```python
from carbonaware_ml import CarbonAwareTrainer
```

Providers:
- Electricity Maps (real-time/forecast carbon intensity)
  - Set credentials via environment:
    - `ELECTRICITYMAPS_API_TOKEN` (required)
    - `ELECTRICITYMAPS_EMAIL` (optional; enables Basic Auth fallback if your plan requires it)
- WattTime (alternative intensity source)
- Ontario TOU price provider (demo, no API key)

If no external provider is configured, the trainer defaults to an "always-allow" mode.

#### Environment

- `CARBONAWARE_REGION`: your region/zone (e.g., `CA-ON`, `US-CAL-CISO`, `DE`)
- `ELECTRICITYMAPS_API_TOKEN`: Electricity Maps API token
- `ELECTRICITYMAPS_EMAIL`: your Electricity Maps account email (if Basic Auth is needed)

#### License

MIT

#### CLI

```bash
carbonaware intensity --region CA-ON          # or set CARBONAWARE_REGION
carbonaware price --region CA-ON
```

#### TensorBoard

```python
trainer = CarbonAwareTrainer(..., tb_log_dir="runs/demo")
```

#### Scheduler (optional)

```python
from carbonaware_ontario.scheduler import run_when_favorable
sched = run_when_favorable(trainer, num_epochs=1, threshold=150, price_threshold_cents=12.0, check_interval_s=300)
```


