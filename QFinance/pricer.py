import numpy as np
from typing import Tuple
import yfinance as yf
from scipy.stats import norm
import warnings
warnings.filterwarnings("ignore")

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.primitives import StatevectorSampler as Sampler
from qiskit_finance.circuit.library import LogNormalDistribution
from qiskit_finance.applications.estimation import EuropeanCallPricing
from qiskit_algorithms import IterativeAmplitudeEstimation, AmplitudeEstimatorResult, EstimationProblem, QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.circuit.library import WeightedAdder, IntegerComparator, LinearAmplitudeFunction
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

def black_scholes_value(S, K, T, r, vol, option_type='call'):
    """
    Calculate the Black-Scholes price for European options.

    Parameters:
    - S (float): Current stock price.
    - K (float): Strike price of the option.
    - T (float): Time to expiration in years.
    - r (float): Risk-free interest rate.
    - vol (float): Volatility of the underlying asset.
    - option_type (str): 'call' or 'put'. Defaults to 'call'.

    Returns:
    - float: The theoretical price of the option.
    """
    if T <= 0: return max(S - K, 0) if option_type == 'call' else max(K - S, 0)
    d1 = (np.log(S / K) + (r + 0.5 * vol**2) * T) / (vol * np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

class ManualEuropeanPricing:
    """
    Manual implementation of the IBM Qiskit Finance European Call Pricing application.
    
    This class constructs a quantum circuit that encodes the payoff function and uncertainty distribution,
    enabling quantum amplitude estimation to price European options manually.

    Attributes:
    - num_state_qubits (int): Number of qubits representing the asset price distribution.
    - strike_price (float): The strike price of the option.
    - rescaling_factor (float): Factor used for amplitude rescaling.
    - bounds (Tuple[float, float]): Domain bounds for the distribution.
    - uncertainty_model (QuantumCircuit): Quantum circuit modeling the underlying uncertainty.

    Methods:
    - to_estimation_problem(): Converts the circuit setup into an EstimationProblem for QAE.
    - interpret(result): Processes the result from QAE to produce an estimated option price.
    """
    def __init__(
        self,
        num_state_qubits: int,
        strike_price: float,
        rescaling_factor: float,
        bounds: Tuple[float, float],
        uncertainty_model: QuantumCircuit,
    ) -> None:
        # 1. Logic from EuropeanCallPricingObjective
        # Create piecewise linear amplitude function segments
        breakpoints = [bounds[0], strike_price]
        slopes = [0, 1]
        offsets = [0, 0]
        f_min = 0
        f_max = bounds[1] - strike_price
        
        # This is the core 'Objective' circuit that handles the payoff logic
        self._objective = LinearAmplitudeFunction(
            num_state_qubits,
            slopes,
            offsets,
            domain=bounds,
            image=(f_min, f_max),
            breakpoints=breakpoints,
            rescaling_factor=rescaling_factor,
        )

        # 2. Logic from the EuropeanCallPricing Application
        # Prepare the state: Distribution + Objective
        self._state_preparation = QuantumCircuit(self._objective.num_qubits)
        
        # Compose uncertainty model (Distribution)
        self._state_preparation.compose(
            uncertainty_model, range(uncertainty_model.num_qubits), inplace=True
        )
        
        # Compose objective (Payoff)
        self._state_preparation.compose(
            self._objective, range(self._objective.num_qubits), inplace=True
        )
        
        # The objective qubit is the target qubit of the LinearAmplitudeFunction
        self._objective_qubits = uncertainty_model.num_qubits

    def to_estimation_problem(self) -> EstimationProblem:
        """
        Convert to EstimationProblem using the internal objective's post-processing.
        """
        return EstimationProblem(
            state_preparation=self._state_preparation,
            objective_qubits=[self._objective_qubits],
            post_processing=self._objective.post_processing,
        )

    def interpret(self, result: AmplitudeEstimatorResult) -> float:
        """
        Return the result processed by the internal objective logic.
        """
        return result.estimation_processed

class QuantumPricer:
    """
    Quantum-based pricer for European, Asian, and American options using Qiskit.

    This class fetches real market data and performs quantum algorithms to estimate option prices.

    Attributes:
    - ticker (str): Stock ticker symbol.
    - strike (float): Option strike price.
    - expiry_days (int): Days until expiration.
    - spot (float): Current stock price.
    - vol (float): Estimated volatility.
    - T (float): Time to expiration in years.
    - r (float): Risk-free interest rate.
    - sampler (Sampler): Quantum sampler for amplitude estimation.

    Methods:
    - price_euro_norm(qubits=5): Prices European call option using quantum amplitude estimation with normalized distribution.
    - price_euro_manual(qubits=5): Manual implementation of European call pricing with custom circuit.
    - price_asian_norm(qubits_per_step=3, steps=2): Prices Asian options with quantum approach.
    - price_american_quantum(steps=5): Prices American options via quantum optimization.
    - compare_all(qmc_price=None): Compares all methods' prices and outputs a summary.
    """
    def __init__(self, ticker: str, strike: float, expiry_days: int):
        self.ticker, self.strike = ticker, strike
        self.T, self.r = expiry_days / 365.0, 0.05
        stock = yf.Ticker(ticker)
        self.spot = stock.fast_info['last_price']
        hist = stock.history(period="1mo")['Close'].pct_change().std() * np.sqrt(252)
        self.vol = hist if not np.isnan(hist) and hist > 0 else 0.3
        self.scale_factor = self.spot
        self.norm_spot = 1.0
        self.norm_strike = self.strike / self.scale_factor        
        self.sampler = Sampler()

    def price_euro_norm(self, qubits=5):
        """
        Prices a European call option using quantum amplitude estimation with a normalized distribution.

        Parameters:
        - qubits (int): Number of qubits for the distribution circuit.

        Returns:
        - float: Estimated option price.
        """
        mu = np.log(self.norm_spot) + (self.r - 0.5 * self.vol**2) * self.T
        sigma = self.vol**2 * self.T
        # Dynamic bounds to ensure the strike is always included
        low = min(0.7, self.norm_strike * 0.9)
        high = max(1.3, self.norm_strike * 1.1)
        
        dist = LogNormalDistribution(qubits, mu=mu, sigma=sigma, bounds=(low, high))
        european_pricing = EuropeanCallPricing(qubits, self.norm_strike, 0.25, (low, high), dist)
        
        problem = european_pricing.to_estimation_problem()
        ae = IterativeAmplitudeEstimation(0.01, 0.05, sampler=self.sampler)
        result = ae.estimate(problem)
        return float(european_pricing.interpret(result) * self.scale_factor)

    def price_euro_manual(self, qubits=5):
        """
        Prices a European call option using a manual quantum circuit implementation 
        and amplitude estimation.

        This method constructs a custom quantum circuit encoding the log-normal distribution 
        of the underlying asset and the payoff function, then applies iterative amplitude 
        estimation to compute the option price.

        Parameters:
        - qubits (int): Number of qubits used to represent the underlying asset distribution.

        Returns:
        - float: Estimated European call option price in monetary units.
        """
        mu = np.log(self.norm_spot) + (self.r - 0.5 * self.vol**2) * self.T
        sigma = self.vol**2 * self.T
        bounds = (min(0.7, self.norm_strike * 0.9), max(1.3, self.norm_strike * 1.1))
        
        # Uncertainty model (LogNormal Distribution)
        dist = LogNormalDistribution(qubits, mu=mu, sigma=sigma, bounds=bounds)
        
        # Initialize the manual class
        european_pricing = ManualEuropeanPricing(qubits, self.norm_strike, 0.25, bounds, dist)
        
        # AE Setup
        ae = IterativeAmplitudeEstimation(0.01, 0.05, sampler=self.sampler)
        result = ae.estimate(european_pricing.to_estimation_problem())
        
        # Scale by spot and discount to present value
        return float(european_pricing.interpret(result) * self.scale_factor * np.exp(-self.r * self.T))

    def price_asian_norm(self, qubits_per_step=3, steps=2):
        """
        Prices an Asian average price option using quantum amplitude estimation.

        This method models the underlying asset's average price over multiple steps, 
        constructs the relevant quantum circuit with distribution, aggregation, and comparison 
        components, then performs amplitude estimation to derive the price.

        Parameters:
        - qubits_per_step (int): Number of qubits per step to encode the distribution.
        - steps (int): Number of averaging steps in the Asian option.

        Returns:
        - float: Estimated Asian option price in monetary units.
        """
        # 1. Distribution & Parameters (Focus on 10% range around strike)
        mu = [(np.log(self.norm_spot) + (self.r - 0.5*self.vol**2)*self.T/steps) for _ in range(steps)]
        cov = np.eye(steps) * (self.vol**2 * self.T / steps + 1e-4)
        low, high = self.norm_strike * 0.9, self.norm_strike * 1.1
        dist = LogNormalDistribution([qubits_per_step]*steps, mu=mu, sigma=cov, bounds=[(low, high)]*steps)
        agg = WeightedAdder(qubits_per_step * steps, [2**i for i in range(qubits_per_step)] * steps)
        
        # 2. Map Strike to Integer Grid
        max_sum = 2**agg.num_sum_qubits - 1
        mapped_strike = (self.norm_strike * steps - steps * low) / (steps * (high - low)) * max_sum
        # Round to nearest integer for the Comparator
        int_strike = int(np.clip(np.round(mapped_strike), 1, max_sum - 1))
        
        # 3. Build Comparator & Registers
        # Comparator flips target if Sum >= int_strike
        comp = IntegerComparator(agg.num_sum_qubits, int_strike)
        
        # Use proper attribute names for the current Qiskit version
        qr_state = QuantumRegister(dist.num_qubits, 's')
        qr_sum = QuantumRegister(agg.num_sum_qubits, 'sum')
        # Unified ancilla register for Adder and Comparator
        num_ancillas = max(agg.num_qubits - (dist.num_qubits + agg.num_sum_qubits), comp.num_qubits - (agg.num_sum_qubits + 1))
        qr_anc = QuantumRegister(num_ancillas, 'a')
        qr_targ = QuantumRegister(1, 't')
        
        qc = QuantumCircuit(qr_state, qr_sum, qr_anc, qr_targ)
        qc.append(dist, qr_state)
        qc.append(agg, qr_state[:] + qr_sum[:] + qr_anc[:agg.num_qubits - (dist.num_qubits + agg.num_sum_qubits)])
        qc.append(comp, qr_sum[:] + qr_targ[:] + qr_anc[:comp.num_qubits - (agg.num_sum_qubits + 1)])

        # 4. Post-Processing (Probability of being In-The-Money)
        def post_proc(prob):
            # prob is the probability that Sum >= int_strike
            # For a simple binary payoff: Payoff = Prob * (Average_Price_If_ITM - Strike)
            # We approximate the average ITM price as the midpoint between Strike and High
            avg_itm_price = (self.norm_strike + high) / 2
            return prob * max(0, avg_itm_price - self.norm_strike)

        # 5. Execute with high-sensitivity Iterative AE
        ae = IterativeAmplitudeEstimation(0.01, 0.01, sampler=self.sampler)
        problem = EstimationProblem(qc, objective_qubits=[qc.num_qubits-1], post_processing=post_proc)
        
        result = ae.estimate(problem)
        return float(result.estimation_processed * self.scale_factor * np.exp(-self.r * self.T))

    def price_american_quantum(self, steps=5):
        """
        Prices an American-style option using a quantum optimization approach.

        This method sets up a quadratic program representing the optimal stopping problem 
        at discrete time nodes. It uses QAOA with a classical optimizer to find the optimal exercise strategy 
        and computes the American option price accordingly.

        Parameters:
        - steps (int): Number of decision nodes (exercise opportunities).

        Returns:
        - float: Estimated American option price in monetary units.
        """
        qp = QuadraticProgram()
        # Create 4 decision nodes (T/4, T/2, 3T/4, T)
        vars = [f't{i}' for i in range(steps)]
        for v in vars:
            qp.binary_var(v)
        
        dt = self.T / steps
        weights = {}
        
        for i in range(1, steps + 1):
            t_curr = i * dt
            # DRIFT + VOLATILITY: This is the 'Forward' expectation
            # We use (r + 0.5*vol^2) to capture the mean of the Log-Normal distribution
            s_t = self.spot * np.exp((self.r + 0.5 * self.vol**2) * t_curr)
            
            # Payoff if we exercise at this specific node
            immediate = max(s_t - self.strike, 0)
            
            # Continuation value: Probability of the stock moving even higher later
            # If we are at the last step, continuation is 0
            if i < steps:
                continuation = black_scholes_value(s_t, self.strike, self.T - t_curr, self.r, self.vol)
            else:
                continuation = 0
                
            # The node value is the max of exercising vs holding, discounted to Now
            node_value = max(immediate, continuation) * np.exp(-self.r * t_curr)
            weights[f't{i-1}'] = node_value

        # The Quantum Optimizer finds which of these 4 time-steps is the "Optimal Stopping" point
        qp.maximize(linear=weights)
        
        # Constraint: You MUST pick exactly one optimal exercise time
        qp.linear_constraint(linear={v: 1 for v in vars}, sense='==', rhs=1)

        # Use a slightly higher maxiter (30) to handle the 4-qubit space
        opt = MinimumEigenOptimizer(QAOA(optimizer=COBYLA(maxiter=30), sampler=self.sampler))
        result = opt.solve(qp)
        
        return float(result.fval)

    def compare_all(self, qmc_price=None):
        """
        Compares various pricing methods for the specified option and outputs the results.

        This method prints a formatted comparison table including classical Black-Scholes, 
        quantum manual, quantum normalized, Asian, American, and optional Monte Carlo prices.

        Parameters:
        - qmc_price (float, optional): Quantum Monte Carlo estimate of the option price for comparison.
        """
        bs = black_scholes_value(self.spot, self.strike, self.T, self.r, self.vol, 'call')
        
        print(f"\n--- {self.ticker} Comparison ---")
        print(f"Spot: ${self.spot:.2f} | Strike: ${self.strike}")
        print(f"{'Method':<25} | {'Price':<10}")
        print("-" * 40)
        print(f"{'Classical (BS)':<25} | ${bs:.4f}")
        print(f"{'Quantum Manual (Euro)':<25} | ${self.price_euro_manual(qubits=5):.4f}")
        print(f"{'Quantum (Euro)':<25} | ${self.price_euro_norm(qubits=5):.4f}")
        print(f"{'Quantum (Asian)':<25} | ${self.price_asian_norm(qubits_per_step=3):.4f}")
        print(f"{'Quantum (Amer)':<25} | ${self.price_american_quantum(steps=5):.4f}")
        if qmc_price is not None:
            print(f"{'Quantum (Monte Carlo)':<25} | ${qmc_price:.4f}")
