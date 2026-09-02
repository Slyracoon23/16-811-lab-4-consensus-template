# 16-811 · Lab 4 · Make a fleet agree, at the speed its graph allows

Implement consensus over a robot network, measure how fast disagreement decays, and check the rate
against the second-smallest eigenvalue of the graph's Laplacian.

**Technique:** Olfati-Saber & Murray, *Consensus Problems in Networks of Agents with Switching
Topology and Time-Delays*, IEEE Trans. Automatic Control 49(9):1520–1533, 2004.
[doi:10.1109/TAC.2004.834113](https://doi.org/10.1109/TAC.2004.834113)
**Checked against:** [ROS2swarm](https://github.com/ROS2swarm/ROS2swarm).
**Built on:** [ROS 2 Jazzy](https://docs.ros.org/en/jazzy/index.html) — the fleet is real nodes on
real topics — and [Foxglove](https://foxglove.dev) to watch it converge.
**From the book:** Gallier & Quaintance ch. 18 (Laplacians), 16 (Rayleigh–Ritz), 19 (spectral drawing), 14 (eigenvalues).

## Start

```bash
make check        # 12 tests. 6 fail. Those 6 are the job.
make reproduce    # runs now, with a zero Laplacian. Every graph looks disconnected. Fix that.
```

Then, once the algebra is right, run it as an actual fleet:

```bash
python3 run_fleet.py --graph ring --robots 8      # eight rclpy nodes on real topics
ros2 run foxglove_bridge foxglove_bridge          # then open ws://localhost:8765 in Foxglove
```

The tests are NumPy and run anywhere. `fleet.py` needs the container, which is `ros:jazzy-ros-base`.

## What you write

```
L = D - A                                  degree matrix minus adjacency
λ₂ = second-smallest eigenvalue of L
```

Two lines. The claim they carry is the whole lab: **λ₂ is not a summary of the graph, it is the
rate** at which a fleet running `ẋ = -Lx` stops disagreeing. Chapter 18 is not background here —
the Laplacian is the controller.

Use `eigvalsh`, not `eigvals`. L is symmetric positive semi-definite, so the symmetric solver is
faster and gives you real eigenvalues in order instead of complex ones with 1e-17 imaginary parts.

## Why four graph families

Because their λ₂ is known in closed form, so you can be *sure* before you ever trust a solver on a
random graph:

| | λ₂ |
|---|---|
| complete `K_n` | `n` |
| star `S_n` | `1` |
| ring `C_n` | `2(1 − cos(2π/n))` |
| path `P_n` | `2(1 − cos(π/n))` |

## The files

| | |
|---|---|
| `method.py` | **Yours.** `laplacian` is one line when finished |
| `evaluate.py` | The ruler — it simulates the fleet and fits the decay rate. Never imports `method` |
| `synthetic.py` | The four families, a disconnected pair, and random connected graphs |
| `baselines.py` | Floors (zero, mean degree) and a ceiling (the closed form) |
| `reproduce.py` | Predicted against measured, per family → `results.json` |
| `extend.py` | Your own ideas, as switches |
| `tests/` | The to-do list |

One detail in the ruler worth reading: `decay_rate` discards the first 20% of the run. Fast modes
dominate early, and λ₂ predicts the *asymptotic* rate — fitting from t=0 gives a number that is too
large and looks like a flaw in the theory rather than a flaw in the fit.

## Past the paper

The paper takes the graph as given and tells you the rate. Turn it round: a fleet designer *chooses*
the topology, radios cost money and bandwidth, and nobody says which links to buy. Maximising λ₂
under a budget is the design question the theorem implies but does not answer.

1. Search for the topology maximising **λ₂ at a fixed edge count**, and test whether the predicted
   speed-up survives real ROS 2 transport.
2. Draw the fleet by its **Fiedler vector** (ch. 19) and check whether the layout predicts which
   robots straggle.
3. Add a link **during operation** and measure how quickly the new rate takes hold.

**How you would know:** the same fitted decay rate `reproduce.py` already reports — a topology
chosen by its spectrum has to actually converge faster, not merely on paper.

## Two layers, and the gap between them is the lesson

`evaluate.py` integrates `ẋ = -Lx` in NumPy. That is the right place to check your Laplacian: it is
fast and deterministic, and if λ₂ does not predict the rate there, the mistake is in your algebra.

But it assumes every robot reads every neighbour instantly and exactly — which is the assumption a
fleet breaks. `fleet.py` is the same protocol as `rclpy` nodes: each robot publishes its value,
subscribes to its neighbours', and steps a timer against whatever has actually arrived. Nothing is
shared in memory. The graph is realised as topics.

λ₂ should still predict the rate. Where it does not, the reason is in the transport rather than the
mathematics — a robot that has heard from nobody yet does not move, so the first steps of a real
fleet lag the prediction — and noticing that difference is most of what the lab is for.

`ros:jazzy-ros-base` is about 600MB, which is the one place in these four labs where the
environment is genuinely heavy. It is worth it: ROS 2 is the lane.
