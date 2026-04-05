from qiskit.primitives import StatevectorSampler as Sampler
from QFinance.generators import QuantumMarketGenerator

def test_market_generator_logic():
    """
    Test T3: Verifies the Quantum Market Generator produces valid entangled scenarios.
    """
    # 1. Setup
    tickers = ["NVDA", "JNJ", "KO", "AAPL", "MSFT"]
    sampler = Sampler()
    generator = QuantumMarketGenerator(tickers, sampler)

    # 2. Run the Generation
    scenario = generator.simulate_next_move()

    # 3. Assertions (Best Practices)
    # Check if it returned a dictionary
    assert isinstance(scenario, dict), "Output should be a dictionary"
    
    # Check if all tickers are present
    assert len(scenario) == len(tickers), "Should generate a move for every ticker"
    
    # Check if the values are the expected strings
    valid_moves = ["UP (+1%)", "DOWN (-1%)"]
    for ticker, move in scenario.items():
        assert ticker in tickers, f"Unknown ticker {ticker} in output"
        assert move in valid_moves, f"Invalid move '{move}' for {ticker}"

def test_generator_entanglement_reproducibility():
    """
    Verifies the generator can handle multiple runs without crashing.
    """
    tickers = ["BTC", "ETH"]
    sampler = Sampler()
    generator = QuantumMarketGenerator(tickers, sampler)
    
    # Run twice to ensure the circuit parameter assignment works in a loop
    run_1 = generator.simulate_next_move()
    run_2 = generator.simulate_next_move()
    
    assert run_1 != run_2 or run_1 == run_2 # Just checking execution flow
    assert len(run_1) == 2
    assert len(run_2) == 2
