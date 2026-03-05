# Petri Finance Simulator - Complete Guide

## Quick Start (30 seconds)

```bash
# Install dependencies
pip install numpy networkx matplotlib

# Run the interactive demo
python -m petri_finance_sim.main
```

Select option 1 (default) to run the example.

## Usage Guide

### Option 1: Command Line (Interactive Mode)

```bash
python -m petri_finance_sim.main
```

The menu offers:
1. **Automatic Simulation** - Fires random transitions until deadlock/completion
2. **Interactive Simulation** - You choose which transition to fire at each step
3. **Check for Gridlock** - Instantly detects if system is stuck
4. **Suggest Resolution** - Recommends how to inject liquidity
5. **Visualize Structure** - Shows Petri net diagram
6. **Visualize Flows** - Shows payment dependency graph
7. **Reset** - Start over with same config
8. **Exit** - Quit

### Option 2: Load a JSON Configuration

Create a `config.json`:

```json
{
  "banks": {
    "Alice": 1000,
    "Bob": 500,
    "Charlie": 250
  },
  "payments": [
    {"from": "Alice", "to": "Bob", "amount": 300},
    {"from": "Bob", "to": "Charlie", "amount": 200},
    {"from": "Charlie", "to": "Alice", "amount": 100}
  ]
}
```

Run the simulator and select option 2, then enter the path to your file.

### Option 3: Programmatic API

```python
from petri_finance_sim.financial_model import build_financial_net
from petri_finance_sim.simulation import run_simulation
from petri_finance_sim.analysis import analyze_gridlock

# Define your network
my_config = {
    "banks": {
        "Bank1": 200,
        "Bank2": 150,
        "Bank3": 100
    },
    "payments": [
        {"from": "Bank1", "to": "Bank2", "amount": 80},
        {"from": "Bank2", "to": "Bank3", "amount": 120},
        {"from": "Bank3", "to": "Bank1", "amount": 50}
    ]
}

# Build the Petri net
net = build_financial_net(my_config)

# Run simulation
state = run_simulation(net, steps=50, seed=42, verbose=True)

# Check for issues
result = analyze_gridlock(net)
print(f"Gridlock: {result['is_gridlock']}")
print(f"Missing liquidity: {result['missing_liquidity']}")

# Print summary
print(state.summary())
```

### Option 4: Analyze Without Simulation

```python
from petri_finance_sim.financial_model import build_financial_net
from petri_finance_sim.analysis import detect_cycles, suggest_gridlock_resolution

net = build_financial_net(my_config)

# Find cycles
cycles = detect_cycles(net)
print("Payment cycles:", cycles)

# Get resolution suggestion
suggestion = suggest_gridlock_resolution(net)
print(suggestion)
```

## Understanding the Output

### Initial Balances
```
Bank Balances: {'A_balance': 100, 'B_balance': 50, 'C_balance': 30}
Pending Requests: {'A_to_B_request_0': 1, 'B_to_C_request_1': 1, 'C_to_A_request_2': 1}
```

### Incidence Matrix
```
Places:      ['A_balance', 'B_balance', 'C_balance', 'A_to_B_request_0', ...]
Transitions: ['pay_A_B_0', 'pay_B_C_1', 'pay_C_A_2']

Matrix A:
[[-40   0  20]
 [ 40 -70   0]
 [  0  70 -10]
 [-1   0   0]
 [  0  -1   0]
 [  0   0  -1]]
```

Row interpretation:
- Row 0 (A_balance): A loses 40 tokens when pay_A_B fires, gains 20 when pay_C_A fires
- Row 3 (A_to_B_request): 1 request consumed when pay_A_B fires

### Simulation Output
```
Step 1: Fired pay_A_B_0
  Balances: {'A_balance': 60, 'B_balance': 90, 'C_balance': 30}
Step 2: Fired pay_C_A_2
  Balances: {'A_balance': 80, 'B_balance': 90, 'C_balance': 20}
Step 3: No enabled transitions. Stopping.
```

### Gridlock Report
```
=== Gridlock Resolution Suggestions ===
Cycles detected: [['A_balance', 'B_balance', 'C_balance']]
Blocked transitions: ['pay_B_C_1']

Minimum liquidity injection needed:
  B_balance: +40 tokens
  (or inject 70 into B to unblock all payments)
```

## Example Scenarios

### Scenario 1: Successful Settlement
```
Bank A: 100, Bank B: 0
Payment: A → B (50 units)
Result: A: 50, B: 50 ✓
```

### Scenario 2: Partial Success
```
Bank A: 60, Bank B: 20, Bank C: 10
Payments: A → B (50), B → C (20), C → A (10)
Step 1: A → B fires (A: 10, B: 70, C: 10)
Step 2: B → C fires (A: 10, B: 50, C: 30)
Step 3: C → A fires (A: 40, B: 50, C: 20)
Final: All payments completed ✓
```

### Scenario 3: Gridlock
```
Bank X: 50, Bank Y: 30, Bank Z: 20
Payments: X → Y (100), Y → Z (100), Z → X (100)
Result: No bank has 100 units. All transitions blocked. ✗
Suggestion: Inject 50 into X (or 70 into Y, or 80 into Z)
```

## Code Quality & Extensions

The codebase is structured for:

### 1. **Backend Integration** (REST API)
```python
# Example: Flask app
from flask import Flask, request, jsonify
from petri_finance_sim import build_financial_net
from petri_finance_sim.analysis import analyze_gridlock

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    config = request.json
    net = build_financial_net(config)
    result = analyze_gridlock(net)
    return jsonify(result)
```

### 2. **Frontend Visualization** (React/D3.js)
Export simulation state to JSON:
```python
import json
state = run_simulation(net, steps=20)
export = {
    "balance_history": state.balance_history,
    "enabled_history": state.enabled_history,
    "payments": state.completed_payments
}
print(json.dumps(export))  # Send to frontend
```

### 3. **Custom Policies** (extend simulation)
```python
# Add time delays, probabilistic failures, etc.
def custom_simulation(net, policy_func):
    for step in range(100):
        enabled = net.enabled_transitions()
        choice = policy_func(enabled)  # Your logic here
        net.fire(choice)
```

## Troubleshooting

### "No module named 'petri_finance_sim'"
Make sure you're running from the project directory:
```bash
cd PetriNetsFinancialSystem
python -m petri_finance_sim.main
```

### "Matplotlib not found"
Install matplotlib:
```bash
pip install matplotlib
```

### Visualization window doesn't open
Try using a different backend:
```bash
export MPLBACKEND=TkAgg  # or Agg, Qt5Agg, etc.
python -m petri_finance_sim.main
```

### JSON file not found
Use absolute paths or ensure the file is in your current directory.

## Performance

- **Full simulation** (100 steps, 20 places, 50 transitions): <100ms
- **Gridlock analysis**: <10ms
- **Visualization**: 1-3 seconds (depends on network size)

## Further Reading

- **Petri Nets**: [Introduction to Petri Nets](https://en.wikipedia.org/wiki/Petri_net)
- **State Equation Theory**: Invariants and reachability analysis
- **Financial Systems**: Interbank settlement, liquidity management

## License

Educational, GPL-compatible. Free to use for learning and research.

---

**Questions?** Check the main README.md for architecture details and theory explanations.
