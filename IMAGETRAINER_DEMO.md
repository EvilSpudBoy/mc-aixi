# Running the ImageTrainer Demo

This short article walks you through building the project and running the ImageTrainer demo from scratch. It assumes no prior familiarity with this repository.

## What the Demo Does
ImageTrainer is a simple supervised “label guessing” environment used to sanity‑check the agent loop, logging, and plotting.
- Each step, the environment produces an observation: a label ID in `[0 .. image-classes-1]`.
- The agent chooses an action: its predicted label.
- Reward is `1` if the prediction matches the label, otherwise `0`.
Because labels are sampled uniformly at random, there is no learnable pattern here; the theoretical long‑run average reward tends toward `1 / image-classes` (e.g., ~0.25 for 4 classes). This makes it a good smoke test: you should see stable behavior and sensible logs.

## Prerequisites
- A C++ toolchain: `g++` and `make` on your PATH.
- Optional for plots: Python with `matplotlib` and `numpy` (used by `graph.py`).

## 1) Build the Project
- From the repo root, run:
```
make
```
- This compiles sources in `src/` and produces the binary `./aixi`.
- If you need to clean up objects or recompile, run `make clean`.

## 2) Review the Demo Config
Open `conf/imagetrainer.conf`. Key options:
- `environment = image-trainer`: selects the ImageTrainer environment.
- `image-classes = 4`: number of labels (valid actions/observations are `0..3`).
- `image-max-steps = 0`: environment never self‑terminates (use `terminate-age`).
- Usual agent knobs: `exploration`, `explore-decay`, `agent-horizon`, `ct-depth`, `mc-simulations`, `terminate-age`.
Tip: For fast runs, set `verbose = false` and `terminate-age = 500`.

## 3) Run the Demo
- Execute the agent with the config and a log destination:
```
./aixi conf/imagetrainer.conf log/imagetrainer.csv
```
- You’ll see option echoes and periodic summaries at powers of two (if `verbose=true`).
- CSV logs are written to `log/imagetrainer.csv`.

## 4) Inspect the Output
The log contains per‑cycle telemetry:
```
cycle, observation, reward, action, explored, explore_rate, total reward, average reward, time, model size
```
Quick peek:
```
head -n 5 log/imagetrainer.csv
```
Expect the average reward to drift near `1 / image-classes` as cycles grow.

## 5) Visualize (Optional)
Generate plots from logs:
```
python graph.py
```
Graphs are saved under `graph/imagetrainer.csv/` (e.g., `average reward.png`, `model size.png`).

## 6) Experiment
- Change difficulty: set `image-classes = 2` or `5` and rerun; note how average reward trends toward `1/classes`.
- Exploration schedule: increase `exploration` and adjust `explore-decay` to see its effect on early behavior.
- Planning/model depth: try larger `mc-simulations`, `agent-horizon`, or `ct-depth` and compare runtime vs. performance.
- Reproducibility: add `random-seed = <int>` to the config to get repeatable runs.

## Troubleshooting
- “no '='” warnings: harmless for comment/blank lines in `.conf` files.
- Long runs: lower `terminate-age` or set `image-max-steps` to cap runtime.
- Build issues: ensure a recent `g++` and that `make` is available; on macOS install Xcode Command Line Tools.

Happy experimenting! If you want ImageTrainer to read real images or use a different reward scheme, open an issue or PR describing the desired behavior.
