"""Core Petri net engine.

Provides lightweight Place, Transition and PetriNet classes.

Petri nets are a bipartite graph of places (holding tokens) and transitions
that move tokens between places. The incidence matrix A = A_plus - A_minus
is useful to compute the state equation x_next = x + u A where u is the
transition firing vector.
"""
from typing import Dict, List, Tuple
import numpy as np


class Place:
    """A Petri net place holding integer tokens."""

    def __init__(self, name: str, tokens: int = 0):
        self.name = name
        self.tokens = int(tokens)

    def __repr__(self):
        return f"Place({self.name!r}, tokens={self.tokens})"


class Transition:
    """A Petri net transition with weighted input and output arcs.

    Tracks the number of times it has fired for performance analysis.

    input_arcs/output_arcs are dicts mapping place_name -> weight
    (the number of tokens consumed/produced).
    """

    def __init__(self, name: str):
        self.name = name
        self.input_arcs: Dict[str, int] = {}
        self.output_arcs: Dict[str, int] = {}
        self.fire_count: int = 0  # Track how many times this transition has fired

    def add_input(self, place_name: str, weight: int = 1):
        self.input_arcs[place_name] = int(weight)

    def add_output(self, place_name: str, weight: int = 1):
        self.output_arcs[place_name] = int(weight)

    def __repr__(self):
        return f"Transition({self.name!r}, fired={self.fire_count})"


class PetriNet:
    """Simple Petri net container with incidence matrix support.

    Places are stored in insertion order to keep matrix rows deterministic.
    Transitions are stored in insertion order to keep matrix columns deterministic.
    """

    def __init__(self):
        self.places: Dict[str, Place] = {}
        self.transitions: Dict[str, Transition] = {}

    # --- Place / Transition building helpers ---
    def add_place(self, name: str, tokens: int = 0) -> Place:
        if name in self.places:
            raise ValueError(f"Place '{name}' already exists")
        p = Place(name, tokens)
        self.places[name] = p
        return p

    def add_transition(self, name: str) -> Transition:
        if name in self.transitions:
            raise ValueError(f"Transition '{name}' already exists")
        t = Transition(name)
        self.transitions[name] = t
        return t

    def add_input(self, place_name: str, transition_name: str, weight: int = 1):
        if place_name not in self.places:
            raise KeyError(place_name)
        if transition_name not in self.transitions:
            raise KeyError(transition_name)
        self.transitions[transition_name].add_input(place_name, weight)

    def add_output(self, transition_name: str, place_name: str, weight: int = 1):
        if place_name not in self.places:
            raise KeyError(place_name)
        if transition_name not in self.transitions:
            raise KeyError(transition_name)
        self.transitions[transition_name].add_output(place_name, weight)

    # --- Core dynamics ---
    def enabled(self, transition_name: str) -> bool:
        """Return True if the transition can fire under current marking."""
        if transition_name not in self.transitions:
            raise KeyError(transition_name)
        t = self.transitions[transition_name]
        for pname, w in t.input_arcs.items():
            if self.places[pname].tokens < w:
                return False
        return True

    def fire(self, transition_name: str) -> bool:
        """Attempt to fire a transition. Returns True if fired."""
        if not self.enabled(transition_name):
            return False
        t = self.transitions[transition_name]
        # consume
        for pname, w in t.input_arcs.items():
            self.places[pname].tokens -= w
        # produce
        for pname, w in t.output_arcs.items():
            self.places[pname].tokens += w
        # Track that this transition fired
        t.fire_count += 1
        return True

    def enabled_transitions(self) -> List[str]:
        return [name for name in self.transitions if self.enabled(name)]

    def marking_vector(self) -> np.ndarray:
        """Return marking as numpy column vector (1D array) ordered by places."""
        return np.array([p.tokens for p in self.places.values()], dtype=int)

    # --- Incidence matrix / state equation ---
    def incidence_matrix(self) -> Tuple[np.ndarray, List[str], List[str]]:
        """Build incidence matrix A = A_plus - A_minus.

        Rows correspond to places, columns to transitions. Returns (A, places, transitions).
        """
        place_names = list(self.places.keys())
        trans_names = list(self.transitions.keys())
        A_plus = np.zeros((len(place_names), len(trans_names)), dtype=int)
        A_minus = np.zeros_like(A_plus)
        for j, tname in enumerate(trans_names):
            t = self.transitions[tname]
            for pname, w in t.output_arcs.items():
                i = place_names.index(pname)
                A_plus[i, j] = w
            for pname, w in t.input_arcs.items():
                i = place_names.index(pname)
                A_minus[i, j] = w
        A = A_plus - A_minus
        return A, place_names, trans_names

    def predict_marking(self, firing_vector: List[int]) -> np.ndarray:
        """Predict marking after firing_vector (u) using state equation x_next = x + A u.

        firing_vector length must match number of transitions.
        """
        A, place_names, trans_names = self.incidence_matrix()
        u = np.array(firing_vector, dtype=int)
        if u.shape[0] != A.shape[1]:
            raise ValueError("firing_vector length must match number of transitions")
        x = self.marking_vector()
        x_next = x + A.dot(u)
        return x_next

    def simulate_batch(self, firing_counts: List[int]) -> np.ndarray:
        """Predict marking after multiple firings (non-sequential) using state equation.

        This does NOT check intermediate enabling constraints; it is a purely
        algebraic prediction using the incidence matrix.
        """
        return self.predict_marking(firing_counts)
