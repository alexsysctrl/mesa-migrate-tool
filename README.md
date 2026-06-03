# mesa-migrate-tool

Small utilities for migrating Mesa 2.x models to Mesa 3.x/4.x.

## Tools included

### 1. `patch_property_layer.py`

Converts models using patch agents as state containers to use PropertyLayer instead.

```bash
python patch_property_layer.py path/to/your/model.py
```

### 2. `patch_schedule.py`

Converts `RandomActivation` / `Activation` schedulers to the new `Schedule` API.

### 3. `patch_agent_init.py`

Fixes the new `Agent(model, ...)` constructor pattern (removed `unique_id` parameter).

## What it fixes

| Mesa 2.x | Mesa 3.x/4.x |
|----------|-------------|
| `RandomActivation` | `Schedule` |
| `Agent(unique_id, model)` | `Agent(model, ...)` |
| `self.grid.get_neighbors(pos, moore=True)` | same |
| `self.all_cells` | `self.grid.all_cells` |
| `BatchRunner` | `model.batch_run()` |
| `self.dc` | `self.datacollector` |
| `mesa.visualization.ModularServer` | `SolaraViz` |

## Credits

Created to help the Mesa community with issue #368 and #358.
