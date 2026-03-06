# Petri Net Financial Simulator

A financial payment settlement simulator using Petri nets to model and analyze payment flows between banks in a network.

## What It Does

This project simulates how payments flow through a network of banks, tracking whether transactions complete successfully or get stuck due to insufficient liquidity. It can detect liquidity deadlocks, identify circular dependencies, and suggest resolution strategies.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Project

Run the main simulation:

```bash
python main.py
```

To run all examples demonstrating the simulator's features:

```bash
python examples_scalable.py
```

## Project Structure

- `petri_net.py` - Core Petri net engine with places and transitions
- `financial_model.py` - Financial network modeling and random network generation
- `simulation.py` - Simulation engine for step-by-step transaction processing
- `analysis.py` - Gridlock detection and analysis tools
- `visualization.py` - Visualization utilities for networks and payment flows
- `main.py` - Example usage of the simulator
- `benchmark.py` - Performance benchmarking tools

## Dependencies

- `numpy` - Numerical computations
- `networkx` - Graph analysis
- `matplotlib` - Visualization (optional)
