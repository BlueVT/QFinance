from QFinance.pricer import QuantumPricer
from QFinance.applications import QuantumAnalytics
from QFinance.monte_carlo import QuantumMonteCarloPricer

def test_quantum_pricing_and_analytics():
    """Test T1: Standard Pricing, Monte Carlo, and Advanced Analytics."""
    tickers = [("NVDA", 170), ("JNJ", 250), ("KO", 70)]
    EXPIRY_DAYS = 30

    for t, k in tickers:
        # 1. Initialize Standard Pricer
        qp = QuantumPricer(t, k, EXPIRY_DAYS)
        assert qp.spot > 0
        
        # 2. Initialize and Run Monte Carlo
        qmc = QuantumMonteCarloPricer(qp.spot, qp.strike, qp.vol, qp.r, qp.T)
        m_price = qmc.price_qmc(qubits=9)
        assert m_price is not None
        
        # 3. Compare (Visual Output)
        qp.compare_all(qmc_price=m_price)

        # 4. Advanced Analytics
        analytics = QuantumAnalytics(t, k, EXPIRY_DAYS)
        analytics.calculate_quantum_greeks()
        analytics.run_stress_test()
        # analytics.visualize_payoff_grid()                 # In a CI environment, skip 3D visualization
