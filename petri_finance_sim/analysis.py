"""Graph analysis for the financial Petri net using networkx.

Builds a dependency graph between balance places and detects cycles, gridlocks,
and computes minimum liquidity injections to break gridlocks.
"""
from typing import Tuple, List, Dict, Set
import networkx as nx
from .petri_net import PetriNet


def build_dependency_graph(net: PetriNet) -> nx.DiGraph:
    """Builds a directed graph where nodes are balance places and edges indicate
    that a payment transition moves funds from one balance to another.

    Returns a directed graph where an edge (A, B) means there exists a payment
    from A to B.
    """
    G = nx.DiGraph()
    # consider only balance places
    balance_places = [name for name in net.places if name.endswith("_balance")]
    G.add_nodes_from(balance_places)

    # For each transition, if it consumes from a balance and produces to a balance,
    # add an edge from payer -> payee.
    for tname, t in net.transitions.items():
        payers = [p for p in t.input_arcs if p.endswith("_balance")]
        payees = [p for p in t.output_arcs if p.endswith("_balance")]
        for payer in payers:
            for payee in payees:
                if not G.has_edge(payer, payee):
                    G.add_edge(payer, payee, transitions=[tname])
                else:
                    G[payer][payee]["transitions"].append(tname)
    return G


def detect_cycles(net: PetriNet) -> List[List[str]]:
    """Detect directed cycles among balances, return list of cycles (lists of nodes).
    Uses networkx.simple_cycles on the dependency graph.
    """
    G = build_dependency_graph(net)
    cycles = list(nx.simple_cycles(G))
    return cycles


def detect_gridlock(net: PetriNet) -> Tuple[bool, List[List[str]]]:
    """Detect liquidity gridlock: no enabled transitions AND there exists a cycle.

    Returns (is_gridlock, cycles_found)
    """
    enabled = net.enabled_transitions()
    cycles = detect_cycles(net)
    is_gridlock = (len(enabled) == 0) and (len(cycles) > 0)
    return is_gridlock, cycles


def analyze_gridlock(net: PetriNet) -> Dict:
    """Comprehensive gridlock analysis.

    Returns dict with:
        - 'is_gridlock': bool
        - 'cycles': list of cycles
        - 'blocked_transitions': list of transitions that are not enabled
        - 'missing_liquidity': dict of bank -> tokens needed to enable payments
    """
    enabled = net.enabled_transitions()
    all_trans = list(net.transitions.keys())
    blocked = [t for t in all_trans if t not in enabled]
    cycles = detect_cycles(net)
    is_gridlock = (len(enabled) == 0) and (len(cycles) > 0)

    # Compute missing liquidity for each blocked transition
    missing_liquidity = {}
    for trans_name in blocked:
        trans = net.transitions[trans_name]
        for place_name, weight in trans.input_arcs.items():
            current = net.places[place_name].tokens
            if current < weight:
                deficit = weight - current
                if place_name not in missing_liquidity:
                    missing_liquidity[place_name] = 0
                missing_liquidity[place_name] += deficit

    return {
        "is_gridlock": is_gridlock,
        "cycles": cycles,
        "blocked_transitions": blocked,
        "missing_liquidity": missing_liquidity,
        "num_enabled": len(enabled),
        "num_total_transitions": len(all_trans)
    }


def compute_minimum_injection(net: PetriNet) -> Dict[str, int]:
    """Compute minimum liquidity injection to unblock the most restrictive transition.

    Returns dict of place_name -> tokens_to_inject
    """
    analysis = analyze_gridlock(net)
    return analysis.get("missing_liquidity", {})


def suggest_gridlock_resolution(net: PetriNet) -> str:
    """Suggest how to resolve gridlock by injecting liquidity.

    Returns a human-readable recommendation.
    """
    analysis = analyze_gridlock(net)

    if not analysis["is_gridlock"]:
        return "No gridlock detected."

    lines = ["=== Gridlock Resolution Suggestions ==="]
    lines.append(f"Cycles detected: {analysis['cycles']}")
    lines.append(f"Blocked transitions: {analysis['blocked_transitions']}")

    if analysis["missing_liquidity"]:
        lines.append("\nMinimum liquidity injection needed:")
        for place, amount in analysis["missing_liquidity"].items():
            lines.append(f"  {place}: +{amount} tokens")
    else:
        lines.append("\nNo immediate token deficit; may be a structural deadlock.")

    return "\n".join(lines)
