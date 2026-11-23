# Blender models

Every model in `models/*.glb` is built by these scripts in Blender (tested with 5.3). The game loads them at start-up and falls back to its code-built shapes for any model that fails to load.

Rebuild all models and their preview renders into `tools/blender/out/`:

```bash
blender -b --factory-startup --python tools/blender/build.py
```

Pass model names (and/or `lineups`) after `--` to rebuild only those, for example `-- turtle coin`. Then copy the new `.glb` files into `models/`.

Conventions the game relies on:

- Units are game metres and forward is three.js -Z (Blender +Y).
- Named nodes are the parts the game animates or swaps: rider `Board`, `Stance`, `Pack`, `ArmL`/`ArmR`, `Head` (with `HelmetMesh`, `VisorMesh`, `FinMesh`), `Scarf`; walkers `LegL`/`LegR`/`ArmL`/`ArmR`; turtle flippers, pufferfish `Tail`, whale `Tail`/`Flukes`, UFO `Craft`/`LightRing`, boulder `RockMesh`; outfits `HeadMesh`/`PackMesh`/`FeetMesh`/`PropMesh`.
- Materials named `*_body`, `*_acc`, `ped_*`, `shell`, `puffer`, `whale`, `rock`, `anemone`, `octopus` and `seahorse` are recoloured per instance in the game.
