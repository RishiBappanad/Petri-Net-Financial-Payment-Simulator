"""Simulation loop for the financial Petri net.

Provides a discrete-event loop that fires transitions step-by-step,
tracking payments and detecting deadlocks. Returns detailed metrics for analysis.
"""
import random
from typing import Optional, Dict, List, Tuple, Any
from .petri_net import PetriNet


class SimulationState:
    """Tracks simulation progress, payments completed, and balances over time."""

    def __init__(self, net: PetriNet):
        self.net = net
        self.step = 0
        self.completed_payments: List[str] = []
        self.balance_history: List[Dict[str, int]] = []
        self.enabled_history: List[List[str]] = []

    def get_balances(self) -> Dict[str, int]:
        """Return dict of current bank balances."""
        return {pname: place.tokens for pname, place in self.net.places.items() 
                if pname.endswith("_balance")}

    def record(self):
        """Record current state."""
        self.balance_history.append(self.get_balances())
        self.enabled_history.append(self.net.enabled_transitions())

    def summary(self) -> str:
        """Return a summary of the simulation."""
        lines = [
            f"Simulation completed at step {self.step}",
            f"Payments completed: {len(self.completed_payments)}",
            f"Final balances: {self.get_balances()}"
        ]
        return "\n".join(lines)

    def metrics(self) -> Dict[str, Any]:
        """Return metrics dictionary for benchmarking/analysis.

        Returns:
            Dict with keys: steps, completed_payments, total_transitions, 
                     success_rate, deadlock, avg_enabled_per_step, 
                     transition_fire_counts
        """
        total_transitions = len(self.net.transitions)
        fire_counts = {tname: t.fire_count for tname, t in self.net.transitions.items()}
        total_fires = sum(fire_counts.values())
        
        avg_enabled = (len(self.enabled_history) / max(1, len(self.enabled_history))) if self.enabled_history else 0
        if self.enabled_history:
            avg_enabled = sum(len(e) for e in self.enabled_history) / len(self.enabled_history)
        
        return {
            "steps": self.step,
            "completed_payments": len(self.completed_payments),
            "total_transitions": total_transitions,
            "success_rate": len(self.completed_payments) / max(1, total_transitions),
            "deadlock": len(self.enabled_history[-1]) == 0 if self.enabled_history else False,
            "avg_enabled_per_step": avg_enabled,
            "transition_fire_counts": fire_counts,
            "total_fires": total_fires
        }


def run_simulation(net: PetriNet, steps: int = 100, seed: Optional[int] = None, 
                   verbose: bool = True) -> SimulationState:
    """Run simulation of the Petri net.

    Each step picks a random enabled transition and fires it. Records state
    and optionally prints updates. Stops when no transitions are enabled or step limit reached.

    Args:
        net: The PetriNet to simulate
        steps: Maximum number of steps
        seed: Random seed for reproducibility
        verbose: Whether to print detailed output (default True; set False for benchmarks)

    Returns:
        SimulationState object with full history and metrics
    """
    if seed is not None:
        random.seed(seed)

    state = SimulationState(net)
    state.record()

    if verbose:
        print("=== Simulation Started ===")
        print(f"Initial balances: {state.get_balances()}\n")

    for step_num in range(1, steps + 1):
        state.step = step_num
        enabled = net.enabled_transitions()

        if not enabled:
            if verbose:
                print(f"\nStep {step_num}: No enabled transitions. Stopping.")
            return state

        tname = random.choice(enabled)
        fired = net.fire(tname)

        if fired:
            state.completed_payments.append(tname)
            if verbose:
                print(f"Step {step_num}: Fired {tname}")
                print(f"  Balances: {state.get_balances()}")

        state.record()

    if verbose:
        print(f"\nReached step limit ({steps}) without deadlock.")

    return state


def run_simulation_interactive(net: PetriNet, steps: int = 100, 
                               seed: Optional[int] = None) -> SimulationState:
    """Run simulation with user prompts at each step (useful for demos)."""
    if seed is not None:
        random.seed(seed)

    state = SimulationState(net)
    state.record()

    print("=== Interactive Simulation ===")
    print(f"Initial balances: {state.get_balances()}\n")

    for step_num in range(1, steps + 1):
        state.step = step_num
        enabled = net.enabled_transitions()

        if not enabled:
            print(f"\nStep {step_num}: No enabled transitions. Gridlock!")
            return state

        print(f"\nStep {step_num}. Enabled transitions: {enabled}")
        choice = input("Enter transition name or 'q' to quit: ").strip()

        if choice.lower() == 'q':
            return state

        if choice not in enabled:
            print("Invalid choice. Try again.")
            step_num -= 1
            continue

        fired = net.fire(choice)
        if fired:
            state.completed_payments.append(choice)
            print(f"Fired {choice}")
            print(f"Balances: {state.get_balances()}")

        state.record()

    return state
