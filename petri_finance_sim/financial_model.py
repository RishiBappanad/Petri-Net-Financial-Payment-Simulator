"""Build a scalable interbank payment Petri net.

Banks: dynamically defined. Each bank has a balance place and payment request places.
Payment transitions implement transfers between banks using settlement requests.

This model accepts a JSON/dict configuration and builds the corresponding Petri net.
Also supports random network generation for benchmarking and scalability testing.
"""
from typing import Dict, List, Any, Optional, Tuple
import random
from .petri_net import PetriNet


def build_financial_net(config: Optional[Dict[str, Any]] = None) -> PetriNet:
    """Constructs and returns a PetriNet modeling an interbank system from config.

    Args:
        config: Dict with keys:
            - 'banks': Dict[bank_name] = initial_balance (int)
            - 'payments': List of dicts with 'from', 'to', 'amount' keys

    If config is None, uses a default example (A, B, C with cyclic payments).

    Each bank balance is a place holding tokens representing monetary units.
    Payment requests are separate places; a payment transition consumes
    tokens from payer balance + one request token, produces to receiver balance.
    """
    if config is None:
        # Default example
        config = {
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

    net = PetriNet()
    banks = config.get("banks", {})
    payments = config.get("payments", [])

    # Add balance places for each bank
    for bank_name, initial_balance in banks.items():
        net.add_place(f"{bank_name}_balance", tokens=initial_balance)

    # Add payment request places and transitions
    for i, payment in enumerate(payments):
        payer = payment.get("from")
        payee = payment.get("to")
        amount = payment.get("amount", 1)

        if not payer or not payee:
            raise ValueError(f"Payment {i} missing 'from' or 'to' field")

        # Create a request place for this payment
        request_place = f"{payer}_to_{payee}_request_{i}"
        net.add_place(request_place, tokens=1)

        # Create a transition for this payment
        transition_name = f"pay_{payer}_{payee}_{i}"
        net.add_transition(transition_name)

        # Wire up the transition:
        # Inputs: payer balance (amount) + request (1)
        net.add_input(f"{payer}_balance", transition_name, weight=amount)
        net.add_input(request_place, transition_name, weight=1)

        # Output: payee balance (amount)
        net.add_output(transition_name, f"{payee}_balance", weight=amount)

    return net


def build_financial_net_default() -> PetriNet:
    """Convenience function: builds the default example network."""
    return build_financial_net()


def generate_random_network(num_banks: int, max_balance: int = 500, 
                           max_payment: int = 200, connectivity: float = 2.0,
                           seed: Optional[int] = None) -> Dict[str, Any]:
    """Generate a random financial network configuration for benchmarking.

    Args:
        num_banks: Number of banks to create (e.g., 5, 10, 20, 50)
        max_balance: Maximum initial balance for any bank
        max_payment: Maximum payment amount between banks
        connectivity: Average number of outgoing payments per bank
        seed: Random seed for reproducibility

    Returns:
        A configuration dict with 'banks' and 'payments' keys suitable for build_financial_net()

    Example:
        >>> config = generate_random_network(10, max_balance=1000, max_payment=300)
        >>> net = build_financial_net(config)
    """
    if seed is not None:
        random.seed(seed)

    # Create bank names and random initial balances
    banks = {}
    for i in range(1, num_banks + 1):
        balance = random.randint(50, max_balance)
        banks[f"Bank{i}"] = balance

    # Generate payment relationships
    payments = []
    num_payments = max(int(num_banks * connectivity), num_banks)
    
    for _ in range(num_payments):
        # Random payer and payee
        payer = random.choice(list(banks.keys()))
        payee = random.choice(list(banks.keys()))
        
        # Avoid self-payments
        if payer == payee:
            continue
        
        # Avoid duplicate payments (check if similar edge already exists)
        if any(p['from'] == payer and p['to'] == payee for p in payments):
            continue
        
        amount = random.randint(10, max_payment)
        payments.append({
            "from": payer,
            "to": payee,
            "amount": amount
        })

    return {
        "banks": banks,
        "payments": payments
    }


def network_stats(config: Dict[str, Any]) -> Dict[str, Any]:
    """Compute statistics about a network configuration.

    Args:
        config: Configuration dict with 'banks' and 'payments'

    Returns:
        Dict with metrics like num_banks, num_payments, total_liquidity, etc.
    """
    banks = config.get("banks", {})
    payments = config.get("payments", [])
    
    total_liquidity = sum(banks.values())
    total_payment_demand = sum(p.get("amount", 0) for p in payments)
    avg_balance = total_liquidity / len(banks) if banks else 0
    avg_payment = total_payment_demand / len(payments) if payments else 0
    
    return {
        "num_banks": len(banks),
        "num_payments": len(payments),
        "total_liquidity": total_liquidity,
        "total_payment_demand": total_payment_demand,
        "avg_balance": avg_balance,
        "avg_payment": avg_payment,
        "liquidity_ratio": total_liquidity / total_payment_demand if total_payment_demand > 0 else 0
    }
