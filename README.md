# SCALE-Sim-PREMA

A fork of [SCALE-Sim v1](https://github.com/ARM-software/SCALE-Sim) (2019), a cycle-accurate systolic CNN accelerator simulator, implementing [PREMA](#references), a preemption-aware multi-task scheduler for NPUs. Built as part of an undergraduate research program.

![A running task getting preempted mid-layer, styled bold red-inverse in the console output](.github/assets/preemption.png)

## What this adds

On top of SCALE-Sim's single-task, cycle-accurate CNN accelerator simulator, this fork adds a multi-task scheduling layer:

- A `Scheduler` that dispatches between concurrently-arriving tasks, with mid-layer preemption and checkpointed resume — state is saved and restored inside SCALE-Sim's own trace-generation loop.
- All three algorithms from the PREMA paper: the inference-time prediction model, the token-based priority scheduler, and the dynamic CHECKPOINT/DRAIN preemption-mechanism selector.
- Five baseline schedulers for comparison: FCFS, round robin (RRB), highest-priority-first (HPF), shortest-job-first (SJF), and token-only (TOKEN).

## Notes

- Preemption is checkpointed below the layer level: `Task.Layer` carries a small context table (`load_var`/`store_var`/`clear_var`) that the original trace-generation loop (`sram_traffic_ws.py`) now saves into and restores from mid-loop, so a task can be paused and resumed inside a single layer.
- `prediction_layer_time.py` estimates each layer's runtime analytically instead of by running the real simulation, using the same cycle-counting logic as `sram_traffic_ws.py`. Comparing its estimates against SCALE-Sim's actual cycle counts surfaced a floor-omission bug in the original partial IFMAP trace path (`e2_BUG`), which the estimator deliberately reproduces for cycle parity.

  > **Retrospective note (2026):** The same bug had already been reported upstream in SCALE-Sim ([PR #47](https://github.com/ARM-software/SCALE-Sim/pull/47), opened January 2021 but never merged into the v1 master); I found that prior report only while revisiting this project years later.
- The default time quota is 100,000 cycles. PREMA reports 0.25 ms at 700 MHz, or 175,000 cycles. The 2021 code comment instead computes 175,000,000, while the origin of the 100,000-cycle default is unclear.
- Test scenarios (`task_list.csv`, `task_list_.csv`) mix real CNNs (AlexNet, GoogLeNet, MobileNet) with synthetic ones at different priorities and arrival times.
- The default `PREMA` config exercises the full preempt → checkpoint → resume path at runtime: it produces a task whose executed timeline splits into two disjoint cycle ranges (e.g. `[[209394, 611238], [1051488, 1565604]]`), confirming preemption actually happens.
- Uses its own ANSI color/style helpers to keep multi-task console output legible.

## Limitations

- No consolidated results exist across runs — each run still produces SCALE-Sim's own per-layer CSV logs, but there's no comparison table or plot showing PREMA against the baseline schedulers the way the paper's own evaluation does. The infrastructure to produce that comparison exists, but it hasn't been run to completion.
- Token thresholds (`12`, `9`, `6`, `3`) are hardcoded rather than config-driven, which makes sweeping them for experiments awkward.
- Comments are a mix of Korean and English.
- Commit history is left as-is: most messages are just a timestamp (e.g. `211011-1512`), redundant with the commit's own authored date, and a cluster of them have the month mistyped (`211118-...`/`211119-...` on commits actually made in October).

## Getting Started

```bash
git clone https://github.com/canplane/SCALE-Sim-PREMA.git
cd SCALE-Sim-PREMA
pip install -r requirements.txt
```

Requires Python 3 and `tqdm`. Run a multi-task simulation with:

```
python scale.py -a architectures/eyeriss.cfg -t task_list.csv -s PREMA -q 100000
```

- `-s`: `FCFS`, `RRB`, `HPF`, `TOKEN`, `SJF`, or `PREMA`
- `-t`: a task list CSV — network name, network CSV path, priority, arrival time (in cycles), e.g.:
  ```
  Network, Network path, Priority, Arrival time,
  "Net_0", "./networks/conv_nets/_foonet_2.csv", 3, 0,
  ```
- `-q`: time quota in cycles (see Notes above)
- `-a`: architecture config — presets are in `architectures/`

See [README.upstream.md](README.upstream.md) for the base SCALE-Sim setup, motivation, and single-task usage.

## References

This project builds on the following works:

```
@article{samajdar2018scale,
  title={SCALE-Sim: Systolic CNN Accelerator Simulator},
  author={Samajdar, Ananda and Zhu, Yuhao and Whatmough, Paul and Mattina, Matthew and Krishna, Tushar},
  journal={arXiv preprint arXiv:1811.02883},
  year={2018}
}

@inproceedings{choi2020prema,
  title={PREMA: A Predictive Multi-task Scheduling Algorithm For Preemptible Neural Processing Units},
  author={Choi, Yujeong and Rhu, Minsoo},
  booktitle={2020 IEEE International Symposium on High Performance Computer Architecture (HPCA)},
  pages={220--233},
  year={2020},
  organization={IEEE},
  doi={10.1109/HPCA47549.2020.00027}
}
```

## About

- **Based on:** [SCALE-Sim v1](https://github.com/ARM-software/SCALE-Sim) (2019), Arm Research / Georgia Institute of Technology / University of Rochester — archived in 2023, superseded by SCALE-Sim v2; see [README.upstream.md](README.upstream.md) for the original project
- **Implements:** [PREMA](https://doi.org/10.1109/HPCA47549.2020.00027) (HPCA 2020), Yujeong Choi and Minsoo Rhu, KAIST
- **Context:** undergraduate research program
- **Timeline:** 2021-10-11 – 2021-11-13
- **Language:** Python
- **License:** MIT (inherited from SCALE-Sim)

---
[github.com/canplane/SCALE-Sim-PREMA](https://github.com/canplane/SCALE-Sim-PREMA)
