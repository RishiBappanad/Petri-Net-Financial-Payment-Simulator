#!/usr/bin/env python
"""Quick demo script showing key features without interactive menus."""

from petri_finance_sim.financial_model import build_financial_net_default
from petri_finance_sim.simulation import run_simulation
from petri_finance_sim.analysis import analyze_gridlock, suggest_gridlock_resolution
import json


def demo():
    """Run a quick automated demo."""
    print("="*70)
    print("  PETRI FINANCE SIMULATOR - Quick Demo")
    print("="*70)
    
    # Build default network
    print("\n[1/5] Building financial network (Banks A, B, C with cyclic payments)...")
    net = build_financial_net_default()
    print(f"      Created {len(net.places)} places, {len(net.transitions)} transitions")
    
    # Show initial state
    print("\n[2/5] Initial Network State:")
    balances = {pname: place.tokens for pname, place in net.places.items() 
               if pname.endswith("_balance")}
    for bank, balance in balances.items():
        print(f"      {bank}: {balance} tokens")
    
    # Show incidence matrix
    print("\n[3/5] Incidence Matrix A:")
    A, places, transitions = net.incidence_matrix()
    print(f"      Shape: {A.shape[0]} places × {A.shape[1]} transitions")
    print(f"      Places: {[p.replace('_balance', '').replace('_request_', '') for p in places if '_balance' in p]}")
    print(f"      Transitions: {transitions}")
    
    # Run simulation
    print("\n[4/5] Running simulation (20 steps with random transition firing)...")
    state = run_simulation(net, steps=20, seed=42, verbose=False)
    print(f"      Completed {len(state.completed_payments)} payments")
    print(f"      Final balances:")
    for bank, balance in state.get_balances().items():
        print(f"        {bank}: {balance} tokens")
    
    # Analyze gridlock
    print("\n[5/5] Gridlock Analysis:")
    analysis = analyze_gridlock(net)
    if analysis['is_gridlock']:
        print(f"      ⚠ GRIDLOCK DETECTED")
        print(f"      Cycles: {analysis['cycles']}")
        print("\n      Resolution suggestions:")
        print(suggest_gridlock_resolution(net))
    else:
        print(f"      ✓ No gridlock")
        print(f"      Enabled transitions: {analysis['num_enabled']}")
    
    print("\n" + "="*70)
    print("  Demo Complete! Run 'python -m petri_finance_sim.main' for interactive mode.")
    print("="*70)


if __name__ == "__main__":
    demo()
