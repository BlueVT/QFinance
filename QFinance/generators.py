import numpy as np
from qiskit.circuit.library import RealAmplitudes

class QuantumMarketGenerator:
    """
    Quantum-based Market Simulator generating synthetic market moves for multiple assets.

    This class uses a parameterized quantum circuit (ansatz) with entanglement to simulate 
    correlated market movements across multiple tickers. It leverages a quantum sampler to 
    generate probabilistic 'Market Day' outcomes.

    Attributes
    ----------
    tickers : list
        List of asset ticker symbols.
    num_assets : int
        Number of assets (length of tickers).
    sampler : QuantumSampler
        Quantum sampler used to run quantum circuits.
    ansatz : RealAmplitudes
        Variational quantum circuit with full entanglement between assets.

    Methods
    -------
    simulate_next_move()
        Executes the ansatz circuit with random parameters, measures, and 
        interprets the result as market moves for each ticker.
    """

    def __init__(self, tickers, sampler):
        self.tickers = tickers
        self.num_assets = len(tickers)
        self.sampler = sampler
        # RealAmplitudes creates entanglement between the tickers
        self.ansatz = RealAmplitudes(num_qubits=self.num_assets, reps=1, entanglement='full')

    def simulate_next_move(self):
        """
        Simulates the next market day by executing a parameterized quantum circuit.

        The method assigns random parameters to the ansatz circuit to generate a quantum state 
        with entanglement, measures the qubits, and interprets the measurement outcomes as 
        market moves: 'UP (+1%)' or 'DOWN (-1%)' for each asset.

        Returns:
        - dict: A mapping from each ticker to its simulated market move, e.g.,
        {'AAPL': 'UP (+1%)', 'GOOG': 'DOWN (-1%)', ...}
        """
        weights = np.random.uniform(-np.pi, np.pi, self.ansatz.num_parameters)
        qc = self.ansatz.assign_parameters(weights)
        qc.measure_all()
        
        # FIX: Wrap qc in a list [] for the V2 Sampler
        job = self.sampler.run([qc], shots=1)
        result = job.result()
        
        # FIX: Access the bitstring from the first PUB result
        pub_result = result[0]
        # Get the first (and only) bitstring result
        bitstrings = pub_result.data.meas.get_bitstrings()
        bitstring = bitstrings[0] 
        
        # Map: '1' = Up Day (+1%), '0' = Down Day (-1%)
        # Note: bitstring is usually a string like "101"
        moves = ["UP (+1%)" if b == '1' else "DOWN (-1%)" for b in bitstring]
        
        # Ensure we return a dictionary mapping to your tickers
        return dict(zip(self.tickers, moves))
