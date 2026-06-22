# ATLAS Plotter

This directory contains a lightweight plotter for ROOT files produced by the
`atlas` analyzer. It follows the HNWR plotter layout but reads the ATLAS-like
histogram paths directly below `Central`.

Default input:

```bash
/gv0/Users/achihwan/SKNanoOutput/atlas/2023
```

Run the representative plot set:

```bash
cd /data6/Users/achihwan/SKNanoAnalyzer-v13/plots/atlas
bash run_atlas_plots.sh
```

Override the input or signal overlay:

```bash
DATA_PATH=/gv0/Users/achihwan/SKNanoOutput/atlas/2022 \
SIGNALS=WR2000N1100 \
bash run_atlas_plots.sh
```

Single plot example:

```bash
python atlas_plotter.py \
  --data-path /gv0/Users/achihwan/SKNanoOutput/atlas/2023 \
  --hist Resolved/rCROS2mu/mlljj \
  --output resolved_rCROS2mu_mlljj
```

SR regions are blinded automatically when the histogram path contains `bSR` or
`rSR`. The uncertainty band is MC statistical uncertainty only.
