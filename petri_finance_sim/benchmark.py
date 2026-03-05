"""Performance benchmarking script for the Petri finance simulator.

Tests scalability across different network sizes and generates metrics
suitable for resume/portfolio evaluation.
"""
import time
from typing import List, Dict, Any
from petri_finance_sim.financial_model import generate_random_network, network_stats, build_financial_net
from petri_finance_sim.simulation import run_simulation


def benchmark_single_network(num_banks: int, max_balance: int = 500, 
                            max_payment: int = 200, connectivity: float = 2.0,
                            sim_steps: int = 100, seed: int = 42) -> Dict[str, Any]:
    """Benchmark a single network configuration.

    Args:
        num_banks: Number of banks in the network
        max_balance: Maximum initial account balance
        max_payment: Maximum payment amount
        connectivity: Average outgoing payments per bank
        sim_steps: Number of simulation steps to run
        seed: Random seed for reproducibility

    Returns:
        Dict with benchmark metrics
    """
    print(f"\n{'='*70}")
    print(f"  Testing network with {num_banks} banks...")
    print(f"{'='*70}")

    # Generate network
    start_gen = time.time()
    config = generate_random_network(num_banks, max_balance, max_payment, 
                                      connectivity, seed=seed)
    time_generate = time.time() - start_gen

    # Get network stats
    stats = network_stats(config)
    print(f"  Configuration generated in {time_generate:.4f}s")
    print(f"  Banks: {stats['num_banks']}, Payments: {stats['num_payments']}")
    print(f"  Total liquidity: {stats['total_liquidity']}, Demand: {stats['total_payment_demand']}")
    print(f"  Liquidity ratio: {stats['liquidity_ratio']:.2f}x")

    # Build Petri net
    start_build = time.time()
    net = build_financial_net(config)
    time_build = time.time() - start_build
    print(f"  Petri net built in {time_build:.4f}s ({len(net.places)} places, {len(net.transitions)} transitions)")

    # Run simulation
    print(f"  Running {sim_steps} simulation steps...")
    start_sim = time.time()
    state = run_simulation(net, steps=sim_steps, seed=seed, verbose=False)
    time_sim = time.time() - start_sim

    # Extract metrics
    metrics = state.metrics()
    print(f"\n  RESULTS:")
    print(f"    Simulation runtime: {time_sim:.4f}s")
    print(f"    Total runtime: {time_generate + time_build + time_sim:.4f}s")
    print(f"    Simulation steps: {metrics['steps']}")
    print(f"    Payments completed: {metrics['completed_payments']}")
    print(f"    Payment success rate: {metrics['success_rate']:.1%}")
    print(f"    Deadlock reached: {metrics['deadlock']}")
    print(f"    Avg enabled transitions per step: {metrics['avg_enabled_per_step']:.2f}")

    return {
        "num_banks": num_banks,
        "time_generate": time_generate,
        "time_build": time_build,
        "time_simulate": time_sim,
        "time_total": time_generate + time_build + time_sim,
        "places": len(net.places),
        "transitions": len(net.transitions),
        "payments": stats['num_payments'],
        "liquidity_ratio": stats['liquidity_ratio'],
        **metrics
    }


def benchmark_network_sizes(sizes: List[int] = None, sim_steps: int = 100,
                            max_balance: int = 500, max_payment: int = 200,
                            connectivity: float = 2.0) -> List[Dict[str, Any]]:
    """Run benchmarks on multiple network sizes.

    Args:
        sizes: List of bank counts to test (default: [5, 10, 20, 50])
        sim_steps: Number of simulation steps per test
        max_balance: Max initial balance
        max_payment: Max payment amount
        connectivity: Average outgoing edges per bank

    Returns:
        List of benchmark results
    """
    if sizes is None:
        sizes = [5, 10, 20, 50]

    results = []
    print("\n" + "="*70)
    print("  PETRI FINANCE SIMULATOR - SCALABILITY BENCHMARK")
    print("="*70)
    print(f"  Testing {len(sizes)} network sizes: {sizes}")
    print(f"  Simulation steps per test: {sim_steps}")

    start_total = time.time()

    for num_banks in sizes:
        try:
            result = benchmark_single_network(
                num_banks, max_balance, max_payment, connectivity,
                sim_steps=sim_steps, seed=42
            )
            results.append(result)
        except Exception as e:
            print(f"  ERROR with {num_banks} banks: {e}")
            continue

    total_time = time.time() - start_total

    # Summary table
    print("\n" + "="*70)
    print("  BENCHMARK SUMMARY")
    print("="*70)
    print(f"{'Banks':<10} {'Trans':<10} {'Time (s)':<12} {'Steps':<8} {'Success':<10} {'Deadlock':<10}")
    print("-" * 70)

    for r in results:
        print(f"{r['num_banks']:<10} {r['transitions']:<10} {r['time_total']:<12.4f} "
              f"{r['steps']:<8} {r['success_rate']:<10.1%} {str(r['deadlock']):<10}")

    print("-" * 70)
    print(f"  Total benchmark time: {total_time:.2f}s")
    
    # Scalability analysis
    if len(results) >= 2:
        print("\n  SCALABILITY ANALYSIS:")
        for i in range(1, len(results)):
            prev = results[i-1]
            curr = results[i]
            size_ratio = curr['num_banks'] / prev['num_banks']
            time_ratio = curr['time_total'] / prev['time_total']
            print(f"    {prev['num_banks']} → {curr['num_banks']} banks: "
                  f"time {time_ratio:.2f}x (size {size_ratio:.1f}x)")

    print("\n" + "="*70)
    return results


def benchmark_connectivity_impact(num_banks: int = 20, connectivities: List[float] = None) -> Dict[str, Any]:
    """Test how payment connectivity affects deadlock rates and performance.

    Args:
        num_banks: Number of banks
        connectivities: List of connectivity values to test

    Returns:
        Dict mapping connectivity -> results
    """
    if connectivities is None:
        connectivities = [0.5, 1.0, 2.0, 4.0]

    print("\n" + "="*70)
    print(f"  CONNECTIVITY IMPACT ANALYSIS ({num_banks} banks)")
    print("="*70)

    results = {}
    for conn in connectivities:
        print(f"\n  Testing connectivity: {conn:.1f}")
        result = benchmark_single_network(num_banks, connectivity=conn, sim_steps=50, seed=42)
        results[f"conn_{conn}"] = result
        print(f"  Deadlock rate: {result['deadlock']}")

    return results


def print_report(results: List[Dict[str, Any]]) -> None:
    """Print a formatted report of benchmark results."""
    print("\n" + "="*70)
    print("  DETAILED PERFORMANCE REPORT")
    print("="*70)

    for r in results:
        print(f"\nNetwork Size: {r['num_banks']} banks, {r['transitions']} transitions")
        print(f"  Generation time:    {r['time_generate']:.4f}s")
        print(f"  Petri net build:    {r['time_build']:.4f}s")
        print(f"  Simulation time:    {r['time_simulate']:.4f}s")
        print(f"  Total time:         {r['time_total']:.4f}s")
        print(f"  Simulation steps:   {r['steps']}")
        print(f"  Payments completed: {r['completed_payments']} / {r['total_transitions']}")
        print(f"  Success rate:       {r['success_rate']:.1%}")
        print(f"  Deadlock:           {r['deadlock']}")
        print(f"  Avg enabled trans:  {r['avg_enabled_per_step']:.2f}")
        print(f"  Liquidity ratio:    {r['liquidity_ratio']:.2f}x demand")

    print("\n" + "="*70)


if __name__ == "__main__":
    # Run default scalability benchmark
    results = benchmark_network_sizes(sizes=[5, 10, 20, 50], sim_steps=100)
    print_report(results)

    # Optional: test connectivity impact
    # connectivity_results = benchmark_connectivity_impact(num_banks=20)
