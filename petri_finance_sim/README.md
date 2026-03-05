# Petri Finance Simulator

A **scalable, interactive financial payment settlement system** modeled using Petri nets. This project simulates interbank payments, detects liquidity gridlocks, and supports Petri net state-equation analysis.

## Overview

### What are Petri Nets?

Petri nets are a mathematical notation for modeling concurrent systems. They consist of:
- **Places**: Token storage (like accounts holding funds)
- **Transitions**: Events that move tokens (like payments)
- **Arcs**: Directed connections with weights defining how many tokens are consumed/produced

### The State Equation

The fundamental Petri net equation is:

$$x_{next} = x + u \cdot A$$

Where:
- $x$ is the current **marking vector** (current tokens in each place)
- $u$ is the **firing vector** (how many times each transition fires)
- $A$ is the **incidence matrix** ($A = A^+ - A^-$)
  - $A^+$: tokens produced (output arc weights)
  - $A^-$: tokens consumed (input arc weights)

### Payment Settlement Model

Each bank has a **balance place**. Payments are modeled as:
1. **Payment Request Place**: Holds 1 token per pending payment
2. **Payment Transition**: 
   - Consumes: tokens from payer balance + 1 request token
   - Produces: tokens to payee balance

### Liquidity Gridlock

A **deadlock** occurs when no transitions can fire. In payment networks, this represents **liquidity gridlock**:
- No bank has enough funds to send its payment
- Funds are locked in a cycle (A waits for B, B waits for C, C waits for A)
- The system is stuck until liquidity is injected

## Features

✅ **Dynamic Configuration**: Define banks and payments via JSON or interactively  
✅ **Incidence Matrix**: Compute and display A = A+ - A−  
✅ **State Equation Prediction**: Algebraically predict marking after firings  
✅ **Simulation Engine**: Step-by-step or interactive firing  
✅ **Gridlock Detection**: Identify liquidity deadlocks and cycles  
✅ **Gridlock Resolution**: Suggest minimum liquidity injections  
✅ **Visualization**: Petri net structure and payment flow diagrams  
✅ **Extensible**: Clean architecture for frontend integration  

## Installation

```bash
pip install numpy networkx matplotlib
```

## Quick Start

```bash
python -m petri_finance_sim.main
```

Then choose:
1. **Default example** (banks A, B, C with cyclic payments)
2. **Load JSON** configuration
3. **Manual input** for custom networks

## Performance Evaluation

### Scalability Benchmarking

The simulator includes performance benchmarking tools to measure scalability across different network sizes.

Run the scalability benchmark:

```bash
python -m petri_finance_sim.benchmark
```

This tests networks with 5, 10, 20, and 50 banks, measuring:

- **Runtime**: Total time to generate, build, and simulate the network
- **Simulation steps**: How many steps until deadlock or completion
- **Payment success rate**: Percentage of payments that actually executed
- **Deadlock frequency**: Whether the system reached deadlock
- **Throughput**: Average enabled transitions per step

#### Example Benchmark Output

```
======================================================================
  PETRI FINANCE SIMULATOR - SCALABILITY BENCHMARK
======================================================================
  Testing 4 network sizes: [5, 10, 20, 50]

======================================================================
  Testing network with 5 banks...
======================================================================
  Configuration generated in 0.0003s
  Banks: 5, Payments: 10
  Petri net built in 0.0012s (16 places, 10 transitions)
  Running 100 simulation steps...

  RESULTS:
    Simulation runtime: 0.0089s
    Total runtime: 0.0104s
    Simulation steps: 14
    Payments completed: 6
    Payment success rate: 60.0%
    Deadlock reached: True
    Avg enabled transitions per step: 2.14

...

======================================================================
  BENCHMARK SUMMARY
======================================================================
Banks       Trans       Time (s)      Steps    Success    Deadlock  
----------------------------------------------------------------------
5          10         0.0104        14       60.0%      True
10         20         0.0215        18       65.0%      True
20         40         0.0487        22       70.0%      True
50         100        0.1823        28       72.0%      True
----------------------------------------------------------------------
  Total benchmark time: 0.26s

  SCALABILITY ANALYSIS:
    5 → 10 banks: time 2.07x (size 2.0x)
    10 → 20 banks: time 2.26x (size 2.0x)
    20 → 50 banks: time 3.74x (size 2.5x)
```

### Performance Metrics

Key metrics measured:

1. **Generation Time** - How quickly a random network is created
2. **Build Time** - Time to construct the Petri net from configuration
3. **Simulation Time** - Time to run N simulation steps
4. **Throughput** - Payments completed per step available
5. **Deadlock Rate** - Frequency of gridlock scenarios
6. **Success Rate** - Percentage of payments that executed (completed vs total)

### Programmatic Benchmarking

Use the benchmark API directly for custom experiments:

```python
from petri_finance_sim.benchmark import benchmark_network_sizes, benchmark_single_network

# Test specific sizes
results = benchmark_network_sizes(sizes=[10, 25, 50, 100], sim_steps=50)

# Single detailed test
result = benchmark_single_network(num_banks=20, max_balance=1000, 
                                 max_payment=300, connectivity=2.5)
```

### Scalability Results

**Observations from typical benchmarks:**

- **Linear to near-quadratic scaling**: Time grows roughly O(n log n) to O(n^1.5) with network size
- **Deadlock rates increase**: Larger networks are more prone to gridlock
- **Payment success rates plateau**: Typically 60-75% without liquidity injection
- **Simulation remains fast**: Even 50-bank networks complete in <200ms

### Connectivity Impact

Page more payments per bank → more deadlock risk:

```bash
python -c "
from petri_finance_sim.benchmark import benchmark_connectivity_impact
results = benchmark_connectivity_impact(num_banks=20, connectivities=[0.5, 1.0, 2.0, 4.0])
"
```

## Example: Default Configuration

```json
{
  "banks": {
    "A": 100,
    "B": 50,
    "C": 30
  },
  "payments": [
    {"from": "A", "to": "B", "amount": 40},
    {"from": "B", "to": "C", "amount": 70},
    {"from": "C", "to": "A", "amount": 20}
  ]
}
```

**Result**: A cycle! Bank B has 50 but needs 70. Bank C has 30 but needs 20. Bank A has 100 but needs 40.  
After A→B and C→A fire, B becomes the bottleneck.

## Project Structure

```
petri_finance_sim/
├── petri_net.py          # Core Petri net engine
├── financial_model.py    # Build payment networks (static & dynamic generation)
├── simulation.py         # Step-by-step or interactive simulation with metrics
├── analysis.py           # Cycle & gridlock detection, resolution suggestions
├── visualization.py      # Matplotlib/networkx visualizations with fire counts
├── benchmark.py          # Scalability benchmarking and performance analysis
├── main.py              # Interactive menu and demo
├── README.md            # This file
├── GUIDE.md             # Detailed usage guide
└── __init__.py          # Package marker
```

## Module Reference

### `petri_net.py`

```python
from petri_finance_sim.petri_net import Place, Transition, PetriNet

net = PetriNet()
net.add_place("A_balance", tokens=100)
net.add_transition("pay_A_B")
net.add_input("A_balance", "pay_A_B", weight=50)
net.add_output("pay_A_B", "B_balance", weight=50)

# Check if transition can fire
if net.enabled("pay_A_B"):
    net.fire("pay_A_B")

# Compute incidence matrix
A, places, transitions = net.incidence_matrix()

# Predict marking after firings
predicted = net.predict_marking([1, 0, 0])  # Fire first transition once
```

### `financial_model.py`

```python
from petri_finance_sim.financial_model import build_financial_net, generate_random_network

# Static configuration
config = {
    "banks": {"Alice": 100, "Bob": 50},
    "payments": [{"from": "Alice", "to": "Bob", "amount": 60}]
}
net = build_financial_net(config)

# Dynamic random generation for benchmarking
config = generate_random_network(num_banks=20, max_balance=500, 
                                max_payment=200, connectivity=2.0)
net = build_financial_net(config)

# Get network statistics
from petri_finance_sim.financial_model import network_stats
stats = network_stats(config)
print(f"Total liquidity: {stats['total_liquidity']}")
print(f"Liquidity ratio: {stats['liquidity_ratio']:.2f}x demand")
```

### `simulation.py`

```python
from petri_finance_sim.simulation import run_simulation, SimulationState

state = run_simulation(net, steps=20, seed=42, verbose=True)
print(f"Payments completed: {len(state.completed_payments)}")
print(f"Final balances: {state.get_balances()}")
```

### `analysis.py`

```python
from petri_finance_sim import analysis

# Detect cycles
cycles = analysis.detect_cycles(net)

# Detect gridlock
is_gridlock, cycles = analysis.detect_gridlock(net)

# Get comprehensive analysis
info = analysis.analyze_gridlock(net)
print(info['missing_liquidity'])  # Dict of place -> tokens needed

# Get resolution suggestion
suggestion = analysis.suggest_gridlock_resolution(net)
print(suggestion)
```

### `visualization.py`

```python
from petri_finance_sim import visualization

# Visualize Petri net structure (places & transitions)
visualization.visualize_petri_net(net, show_fire_count=True)

# Visualize payment flow graph
visualization.visualize_payment_flow(net)

# Plot balance evolution over simulation steps
visualization.visualize_simulation_history(state.balance_history, state.enabled_history)
```

### `benchmark.py`

```python
from petri_finance_sim.benchmark import benchmark_network_sizes, benchmark_single_network

# Run standard scalability benchmark (5, 10, 20, 50 banks)
results = benchmark_network_sizes(sizes=[5, 10, 20, 50], sim_steps=100)

# Single detailed benchmark
result = benchmark_single_network(num_banks=20, max_balance=1000, 
                                 max_payment=300, connectivity=2.5, 
                                 sim_steps=100)

# Access metrics
print(f"Runtime: {result['time_total']:.4f}s")
print(f"Success rate: {result['success_rate']:.1%}")
print(f"Deadlock: {result['deadlock']}")
```

## Examples

### Example 1: Simple Two-Bank Payment

```json
{
  "banks": {"A": 100, "B": 0},
  "payments": [{"from": "A", "to": "B", "amount": 50}]
}
```

**Outcome**: Single transition fires, A loses 50, B gains 50. No deadlock.

### Example 2: Circular Dependency (Gridlock Risk)

```json
{
  "banks": {"A": 50, "B": 30, "C": 20},
  "payments": [
    {"from": "A", "to": "B", "amount": 100},
    {"from": "B", "to": "C", "amount": 100},
    {"from": "C", "to": "A", "amount": 100}
  ]
}
```

**Outcome**: Immediate deadlock. No bank has 100 tokens. System is gridlocked. Simulation suggests injecting 50 tokens into A, 70 into B, or 80 into C.

### Example 3: Partial Settlement

```json
{
  "banks": {"A": 60, "B": 20, "C": 10},
  "payments": [
    {"from": "A", "to": "B", "amount": 50},
    {"from": "B", "to": "C", "amount": 20},
    {"from": "C", "to": "A", "amount": 10}
  ]
}
```

**Outcome**: A→B fires (A:10, B:70, C:10), then B→C fires (A:10, B:50, C:30), then C→A fires (A:40, B:50, C:20). System settles successfully.

## Interactive Menu Options

```
1. Run automatic simulation      → Random transition firing
2. Run interactive simulation    → You choose which transition fires at each step
3. Check for gridlock            → Detects deadlocks and cycles
4. Suggest gridlock resolution   → Recommends liquidity injection
5. Visualize Petri net           → Draw structure (places, transitions, arcs)
6. Visualize payment flows       → Show dependency graph between banks
7. Reset network                 → Start over with same config
8. Exit
```

## Architecture & Extensibility

The project is designed for:
- **Backend-only use** (analyze networks, detect gridlocks)
- **REST API integration** (endpoints for config upload, simulation, analysis)
- **Frontend visualization** (export data to d3.js or plotly)
- **Further expansion** (add liquidity policies, multi-asset support, time-varying demands)

### File Organization

```
├── Core Engine        → petri_net.py (Place, Transition, PetriNet)
├── Domain Model       → financial_model.py (config → net)
├── Dynamics           → simulation.py (step-by-step execution)
├── Analysis           → analysis.py (cycles, gridlocks, solutions)
├── Presentation       → visualization.py (matplotlib/networkx)
└── Integration        → main.py (interactive CLI)
```

## Advanced Usage

### Programmatic API

```python
from petri_finance_sim.financial_model import build_financial_net, generate_random_network
from petri_finance_sim.simulation import run_simulation
from petri_finance_sim.analysis import analyze_gridlock

# Define network
config = {
    "banks": {"X": 100, "Y": 50, "Z": 30},
    "payments": [
        {"from": "X", "to": "Y", "amount": 80},
        {"from": "Y", "to": "Z", "amount": 60},
        {"from": "Z", "to": "X", "amount": 40}
    ]
}

net = build_financial_net(config)

# Run simulation with full metrics
state = run_simulation(net, steps=50, seed=123, verbose=False)
metrics = state.metrics()
print(f"Success rate: {metrics['success_rate']:.1%}")
print(f"Deadlock: {metrics['deadlock']}")

# Analyze result
analysis = analyze_gridlock(net)
if analysis['is_gridlock']:
    print("Liquidity needed:", analysis['missing_liquidity'])
```

### Large-Scale Benchmarking

```python
from petri_finance_sim.financial_model import generate_random_network
from petri_finance_sim.benchmark import benchmark_network_sizes

# Generate and test random networks of increasing size
for num_banks in [10, 20, 50, 100]:
    config = generate_random_network(num_banks, max_balance=1000, 
                                     max_payment=300, connectivity=2.0)
    # ... build and test
    
# Or use the built-in benchmark:
results = benchmark_network_sizes(sizes=[10, 20, 50, 100], sim_steps=100)
```

### Load from JSON File

```json
{
  "banks": {...},
  "payments": [...]
}
```

```bash
python -m petri_finance_sim.main
# Select option 2: Load JSON file
# Enter: path/to/config.json
```

## Theory Deep Dive

### Incidence Matrix Construction

For a Petri net with $m$ places and $n$ transitions:

$$A\_ij = A^+\_ij - A^-\_ij$$

Where:
- $A^+\_ij$ = weight of output arc (transition $j$ → place $i$)
- $A^-\_ij$ = weight of input arc (place $i$ → transition $j$)

### Reachability via State Equation

Given a marking $x$ and a sequence of firings $u$:

$$x_{reachable} = x_0 + u \cdot A^T$$

This provides a quick check: if the predicted marking has any negative component, that firing sequence is **forbidden** (violates nonnegativity).

### Deadlock Characterization

- **Structural deadlock**: A cycle exists in the dependency graph
- **Behavioral deadlock**: No enabled transitions (sufficient enabled places)
- **Liquidity gridlock**: Both structural + behavioral + all cycle nodes are starved

## Limitations & Future Work

- Currently assumes **non-preemptive** transition firings (no cancellations)
- **Single-asset** only (no multi-currency or exchange rates)
- **Deterministic configuration** (no dynamic demand)
- Visualization limited to small networks (~20 nodes)

### Planned Features

- [ ] Multi-asset/currency support
- [ ] Time delays on transitions
- [ ] Stochastic demand patterns
- [ ] Rest API server (Flask/FastAPI)
- [ ] React frontend with live visualization
- [ ] Liquidity policy optimization (find minimal injections)
- [ ] Export to PNML (Petri Net Markup Language)

## Testing

Run the default example:

```bash
python -m petri_finance_sim.main
# Select option 1: Use default example
# View incidence matrix, run 20 steps, check for gridlock
```

## License

Educational/GPL. Use freely for learning and demonstrations.

## Contact & Contributions

For questions, optimizations, or feature requests, please open an issue or submit a PR.

---

**Built for scalability, clarity, and extensibility.**
