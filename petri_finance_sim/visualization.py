"""Petri net and financial network visualizer using networkx + matplotlib.

Places are drawn as circles, transitions as squares. Token counts and payments
are annotated.
"""
from typing import Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from .petri_net import PetriNet
from .analysis import build_dependency_graph


def visualize_petri_net(net: PetriNet, figsize: Tuple[int, int] = (12, 8), 
                       title: str = "Petri Net", show_fire_count: bool = True) -> None:
    """Visualize the Petri net structure.

    Places (circles) on left, transitions (squares) on right. Edges labeled
    with arc weights. Token counts displayed on places. Fire counts on transitions.

    Args:
        net: The PetriNet to visualize
        figsize: Figure size (width, height)
        title: Plot title
        show_fire_count: Whether to show how many times each transition fired
    """
    G = nx.DiGraph()

    # Add nodes with metadata
    for pname, p in net.places.items():
        G.add_node(pname, kind='place', tokens=p.tokens)
    for tname, t in net.transitions.items():
        G.add_node(tname, kind='transition', fire_count=t.fire_count)

    # Add edges with weights
    for tname, t in net.transitions.items():
        for pl, w in t.input_arcs.items():
            G.add_edge(pl, tname, weight=w)
        for pl, w in t.output_arcs.items():
            G.add_edge(tname, pl, weight=w)

    # Layout: places on left, transitions on right
    places = [n for n, d in G.nodes(data=True) if d.get('kind') == 'place']
    trans = [n for n, d in G.nodes(data=True) if d.get('kind') == 'transition']
    pos = {}
    for i, p in enumerate(places):
        pos[p] = (0, -i * 2)
    for j, t in enumerate(trans):
        pos[t] = (3, -j * 2)

    plt.figure(figsize=figsize)
    ax = plt.gca()

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, nodelist=places, node_shape='o', 
                          node_color='lightblue', node_size=1000, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=trans, node_shape='s', 
                          node_color='lightcoral', node_size=1000, ax=ax)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)

    # Draw edges
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=15, 
                          connectionstyle="arc3,rad=0.1", ax=ax)

    # Edge labels (only show if weight != 1)
    edge_labels = {(u, v): d.get('weight', 1) for u, v, d in G.edges(data=True) 
                   if d.get('weight', 1) != 1}
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7, ax=ax)

    # Annotate token counts on places
    for pname in places:
        tokens = G.nodes[pname].get('tokens', 0)
        xy = pos[pname]
        ax.text(xy[0] - 0.5, xy[1] - 0.3, f"t={tokens}", fontsize=8, 
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Annotate fire counts on transitions
    if show_fire_count:
        for tname in trans:
            fire_count = G.nodes[tname].get('fire_count', 0)
            xy = pos[tname]
            ax.text(xy[0] - 0.5, xy[1] - 0.3, f"fired={fire_count}", fontsize=7,
                   bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    plt.show()


def visualize_payment_flow(net: PetriNet, figsize: Tuple[int, int] = (10, 8)) -> None:
    """Visualize the payment dependency graph (which bank pays which).

    Shows only balance places and edges between them (payment flows).
    """
    G = build_dependency_graph(net)

    # Get current balances for node labels
    balances = {node: net.places[node].tokens for node in G.nodes()}

    plt.figure(figsize=figsize)
    ax = plt.gca()

    # Use spring layout for better aesthetics
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Draw nodes with colors based on balance amount
    node_colors = [balances[node] for node in G.nodes()]
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                   node_size=2000, cmap='RdYlGn', ax=ax)

    # Draw edges with arrows
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20, 
                          connectionstyle="arc3,rad=0.1", ax=ax, width=2)

    # Labels: bank_balance -> balance amount
    labels = {node: f"{node.replace('_balance', '')}\n({balances[node]})" 
             for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold', ax=ax)

    ax.set_title("Payment Flow Network\n(Node color = balance; lighter = more funds)", 
                fontsize=12, fontweight='bold')
    ax.axis('off')
    plt.colorbar(nodes, label="Token Balance")
    plt.tight_layout()
    plt.show()


def visualize_simulation_history(history_balances, history_enabled, figsize: Tuple[int, int] = (12, 6)) -> None:
    """Plot balance evolution over simulation steps.

    Args:
        history_balances: List[Dict] of balance snapshots
        history_enabled: List[List] of enabled transition lists per step
    """
    if not history_balances:
        print("No history to plot.")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

    # Get all banks
    banks = set()
    for snapshot in history_balances:
        banks.update(snapshot.keys())
    banks = sorted(list(banks))

    # Plot 1: Balance evolution
    for bank in banks:
        balances_over_time = [snapshot.get(bank, 0) for snapshot in history_balances]
        ax1.plot(balances_over_time, marker='o', label=bank.replace('_balance', ''))

    ax1.set_xlabel('Step')
    ax1.set_ylabel('Balance (tokens)')
    ax1.set_title('Bank Balance Evolution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Number of enabled transitions
    num_enabled = [len(enabled) for enabled in history_enabled]
    ax2.plot(num_enabled, marker='s', color='orange', linewidth=2)
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Number of Enabled Transitions')
    ax2.set_title('Transaction Availability Over Time')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
