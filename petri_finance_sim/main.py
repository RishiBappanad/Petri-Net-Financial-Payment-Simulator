"""Interactive demo runner for the Petri-finance simulation.

Loads a financial network (default or user-defined), shows incidence matrix,
runs simulation, detects gridlocks, and optionally visualizes results.
"""
import json
import sys
from typing import Optional, Dict, Any

from petri_finance_sim.financial_model import build_financial_net, build_financial_net_default
from petri_finance_sim import simulation, analysis, visualization
import numpy as np


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_incidence_matrix(net):
    """Print the incidence matrix with place and transition labels."""
    A, places, transitions = net.incidence_matrix()
    print("\nIncidence Matrix A (rows=places, cols=transitions):")
    print(f"  Places:      {places}")
    print(f"  Transitions: {transitions}")
    print("\nMatrix A:")
    print(A)
    return A, places, transitions


def print_initial_state(net):
    """Print initial balances and payment requests."""
    print("\nInitial Network State:")
    balances = {pname: place.tokens for pname, place in net.places.items() 
               if pname.endswith("_balance")}
    requests = {pname: place.tokens for pname, place in net.places.items() 
               if pname.endswith("_request")}
    print("  Bank Balances:", balances)
    print("  Pending Requests:", requests)
    return balances, requests


def demonstrate_state_equation(net, A, places):
    """Demonstrate state equation prediction."""
    print_header("State Equation Prediction")
    print("Using x_next = x + uA, predict marking after one transition fires...")
    
    transitions = list(net.transitions.keys())
    if len(transitions) > 0:
        # Fire first transition
        u = [0] * len(transitions)
        u[0] = 1
        predicted = net.predict_marking(u)
        print(f"\nFiring {transitions[0]} once (u={u}):")
        print(f"  Predicted marking: {predicted}")
        print(f"  Which corresponds to:")
        for pname, val in zip(places, predicted):
            print(f"    {pname}: {val}")


def load_user_config() -> Optional[Dict[str, Any]]:
    """Prompt user to load a custom configuration or use default."""
    print_header("Configuration")
    print("""
Options:
  1. Use default example (banks A, B, C with cyclic payments)
  2. Load JSON file
  3. Enter configuration manually
  4. Quickstart (default)
    """)
    
    choice = input("Enter choice (1-4, default=4): ").strip() or "4"
    
    if choice == "1":
        print("Using default configuration...")
        return None
    elif choice == "2":
        filepath = input("Enter JSON file path: ").strip()
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
                print(f"Loaded config from {filepath}")
                return config
        except Exception as e:
            print(f"Error loading file: {e}. Using default.")
            return None
    elif choice == "3":
        print("Entering manual configuration...")
        banks = {}
        print("Enter banks (name and initial balance). Type 'done' to finish.")
        while True:
            name = input("Bank name (or 'done'): ").strip()
            if name.lower() == 'done':
                break
            try:
                balance = int(input(f"Initial balance for {name}: ").strip())
                banks[name] = balance
            except ValueError:
                print("Invalid balance. Try again.")
        
        payments = []
        print("\nEnter payments. Type 'done' to finish.")
        while True:
            frm = input("From bank (or 'done'): ").strip()
            if frm.lower() == 'done':
                break
            to = input("To bank: ").strip()
            try:
                amt = int(input("Amount: ").strip())
                payments.append({"from": frm, "to": to, "amount": amt})
            except ValueError:
                print("Invalid amount. Try again.")
        
        return {"banks": banks, "payments": payments}
    else:
        return None


def interactive_menu():
    """Main interactive menu."""
    print_header("Financial Payment Settlement System using Petri Nets")
    
    # Load configuration
    config = load_user_config()
    
    try:
        net = build_financial_net(config)
    except Exception as e:
        print(f"Error building network: {e}")
        return
    
    print(f"\nNetwork built with {len(net.places)} places and {len(net.transitions)} transitions.")
    
    # Initial state
    print_header("Network Analysis")
    balances, requests = print_initial_state(net)
    
    # Incidence matrix
    A, places, transitions = print_incidence_matrix(net)
    
    # Demonstrate state equation
    demonstrate_state_equation(net, A, places)
    
    # Show dependency graph analysis
    print_header("Payment Dependency Analysis")
    cycles = analysis.detect_cycles(net)
    if cycles:
        print(f"Cycles detected: {cycles}")
        print("  (This indicates potential for gridlock if liquidity is tight)")
    else:
        print("No cycles in payment dependencies.")
    
    # Interactive options
    while True:
        print_header("Simulation Options")
        print("""
  1. Run automatic simulation (random firing)
  2. Run interactive simulation (you choose each fire)
  3. Check for gridlock
  4. Suggest gridlock resolution
  5. Visualize Petri net structure
  6. Visualize payment flows
  7. Reset network
  8. Exit
        """)
        
        choice = input("Enter choice (1-8): ").strip()
        
        if choice == "1":
            steps = input("Number of steps (default=20): ").strip() or "20"
            try:
                steps = int(steps)
                state = simulation.run_simulation(net, steps=steps, seed=None, verbose=True)
                print("\n" + state.summary())
            except ValueError:
                print("Invalid input.")
        
        elif choice == "2":
            state = simulation.run_simulation_interactive(net, steps=100)
            print("\n" + state.summary())
        
        elif choice == "3":
            is_gridlock, cycles = analysis.detect_gridlock(net)
            if is_gridlock:
                print("⚠ GRIDLOCK DETECTED!")
                print(f"  Cycles: {cycles}")
                print(f"  No payments can proceed.")
            else:
                enabled = net.enabled_transitions()
                print(f"✓ No gridlock. {len(enabled)} transition(s) enabled.")
        
        elif choice == "4":
            print(analysis.suggest_gridlock_resolution(net))
        
        elif choice == "5":
            try:
                visualization.visualize_petri_net(net)
            except Exception as e:
                print(f"Visualization failed: {e}")
        
        elif choice == "6":
            try:
                visualization.visualize_payment_flow(net)
            except Exception as e:
                print(f"Visualization failed: {e}")
        
        elif choice == "7":
            net = build_financial_net(config)
            print("Network reset.")
        
        elif choice == "8":
            print("Exiting. Thank you!")
            break
        
        else:
            print("Invalid choice. Try again.")


def main():
    """Entry point."""
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)


if __name__ == '__main__':
    main()
