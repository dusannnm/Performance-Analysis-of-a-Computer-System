# Performance Analysis of an Open Queueing Network

University project for **Computer Systems Performance** (Faculty of Electrical Engineering, University of Belgrade, 2025/2026). The assignment is described in [`info/projekat_2526.pdf`](info/projekat_2526.pdf).

A multiprogramming computer is modeled as an **open queueing network**: a Poisson stream of jobs (rate α) arrives at a CPU, then moves between 3 system disks and K user disks according to fixed routing probabilities, and leaves after a user disk. The system is analyzed in two independent ways and the results are compared:

1. **Analytical solution**: matrix method for visit ratios + Jackson's theorem.
2. **Discrete-event simulation**: 100 repetitions per configuration, averaged.

Everything is computed for **K = 2..5** user disks and **r ∈ {0.30, 0.55, 0.80, 1.00}**, where the arrival rate is α = r · α_max(K).

## How it works

| Step | What it does |
|---|---|
| Topology | Builds the routing matrix **P** and service times for a given K |
| Visit ratios | Solves `v · (I − P) = e` to get the visit ratio of every node (X_i / α) |
| Stability | `α_max = min_i 1 / (v_i · S_i)`; the node achieving the minimum is the critical resource |
| Jackson's theorem | Each node behaves as an independent M/M/1 queue, giving utilization, average number of jobs and response time |
| Simulation | Event-driven (future-event heap, one FCFS queue per node), simulated time is configurable (default 30 min) |
| Comparison | Relative deviation of the single and the averaged simulation from the analytical results, plus 12 diagrams |

## Project structure

```
src/
  konstante.py               system parameters (service times, probabilities, K and r ranges)
  topologija.py              routing matrix P, node names, service times
  vektor_poseta.py           matrix method for visit ratios
  stabilnost.py              alpha_max and critical resource
  dzeksonova_teorema.py      utilization, jobs in node, response time (Jackson)
  simulacija.py              class Simulacija: one simulation run
  poredjenje.py              relative deviations analytic vs. simulation
  iscrtavanje.py             plotting
  ulaz_izlaz.py              reading / writing result files
  main_analiticki.py         runs the analytical part
  main_simulacija.py         runs the simulation (100 repetitions per K and r)
  main_poredjenje.py         comparison tables + diagrams
  generisi_dokumentaciju.py  builds docs/dokumentacija.docx
output/                      result files (.txt)
plots/                       generated diagrams (.png)
docs/                        final documentation (.docx / .pdf)
info/                        assignment and the professor's reference notebook
```

## Setup

Requires Python 3.12 or newer.

```bash
pip install -r requirements.txt
```

In PyCharm, mark `src/` as **Sources Root** (modules import each other without a package prefix).

## Running the project

Run the scripts from inside `src/`, in this order:

```bash
python main_analiticki.py       # seconds
python main_simulacija.py       # slow: roughly 60-90 minutes at default settings
python main_poredjenje.py       # needs the simulation output files
python generisi_dokumentaciju.py  # needs the plots from the previous step
```

To try the simulation quickly, call `pokreni_simulaciju(trajanje_min=2, broj_ponavljanja=3)` from `main_simulacija.py` instead of using the defaults.

## Results

| File | Content |
|---|---|
| `output/protoci_analiticki.txt` | Visit ratios (X_i / α) per K |
| `output/alfa_max_i_kriticni_resurs.txt` | α_max and critical resource per K |
| `output/rezultati_analiticki.txt` | Utilization, throughput, jobs, response time per K and r |
| `output/rezultati_simulacija.txt` | Results of a single simulation run |
| `output/rezultati_simulacija_usrednjeno.txt` | Average over 100 runs |
| `output/izvestaj_odstupanja.txt` | Relative deviations from the analytical results |

Main findings:

- Averaging 100 runs cuts the average deviation from the analytical results from about **0.78 %** (single run) to about **0.11 %**.
- The critical resource depends only on K, not on r: user disks for K = 2, 3; an exact tie between CPU and user disks at K = 4; CPU for K = 5.
- At r = 1.00 the critical resource sits exactly on the stability boundary, so the analytical response time is infinite, while the finite-horizon simulation shows a very large but finite queue.

## Worth mentioning

Identifiers are in Serbian. Rates are reported in jobs/s and times in ms.


## Author

Dušan Milivojević, 2025/26.
