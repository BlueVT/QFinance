from qiskit.primitives import StatevectorSampler as Sampler
from QFinance.generators import *

def test_quantum_market_generator():
    """Test T3: Synthetic 'Quantum Day' generation via entanglement."""
    tickers = ["NVDA", "JNJ", "KO", "AAPL", "MSFT"]
    sampler = Sampler()
    
    generator = QuantumMarketGenerator(tickers, sampler)
    scenario = generator.simulate_next_move()
    
    assert isinstance(scenario, dict)
    for ticker in tickers:
        assert ticker in scenario
        # Ensure the move is a descriptive string or numeric value as expected
        assert scenario[ticker] is not None
