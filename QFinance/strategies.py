import numpy as np
import yfinance as yf
import pandas as pd
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.circuit.library import ZZFeatureMap
from qiskit_machine_learning.algorithms import QSVC
from qiskit_machine_learning.kernels import FidelityQuantumKernel

class QuantumRiskScorer:
    """
    Uses Quantum ML (QSVC) to predict credit defaults.
    """
    def __init__(self, sampler, fidelity_algorithm):
        # 1. Define the Feature Map (Entangles data into 3 qubits)
        self.feature_map = ZZFeatureMap(feature_dimension=3, reps=2)
        
        # 2. Create the Quantum Kernel using the Sampler and Fidelity
        self.kernel = FidelityQuantumKernel(
            feature_map=self.feature_map, 
            fidelity=fidelity_algorithm
        )
        
        # 3. Initialize the QSVC with the Quantum Kernel
        self.qsvc = QSVC(quantum_kernel=self.kernel)

    def train_model(self, X_train, y_train):
        """
        Trains the QSVC on historical credit data.
        """
        self.qsvc.fit(X_train, y_train)

    def predict_default(self, client_data):
        """
        Predicts risk for new data.
        client_data: 2D array-like [[debt_ratio, stability, history]]
        """
        prediction = self.qsvc.predict(client_data)
        return "Default Risk" if prediction[0] == 1 else "Safe"

class QuantumPortfolio:
    """
    Quantum-Enhanced Portfolio Optimization using Quantum Approximate Optimization Algorithm (QAOA).

    This class fetches real-time market data for specified tickers, constructs a quadratic 
    program to optimize asset selection based on risk and return, and solves it using QAOA 
    with a specified sampler.

    Attributes:
    - tickers (list): List of stock ticker symbols.
    - sampler (QuantumSampler): Quantum sampler for executing quantum circuits.
    - num_assets (int): Number of assets in the portfolio.

    Methods:
    - _fetch_market_data(): Internal method to retrieve and compute annualized returns and covariance.
    - optimize_allocation(risk_appetite=0.5): Uses QAOA to select the optimal subset of stocks.
    """
    def __init__(self, tickers, sampler):
        self.tickers = tickers
        self.sampler = sampler
        self.num_assets = len(tickers)

    def _fetch_market_data(self):
        """Internal helper to get annualized returns and covariance."""
        print(f"Fetching 1-year historical data for {self.tickers}...")
        # Get last 1 year of Close prices
        data = yf.download(self.tickers, period="1y", progress=False)['Close']
        
        # Calculate daily returns
        returns = data.pct_change().dropna()
        returns = returns.dropna(axis=1)
        
        # Annualize (252 trading days)
        mu = returns.mean() * 252
        sigma = returns.cov() * 252
        
        return mu, sigma

    def optimize_allocation(self, risk_appetite=0.5):
        """
        Performs quantum optimization to select the best subset of stocks based on live data.

        Constructs a quadratic programming problem where the objective is to maximize 
        expected return minus risk-adjusted volatility, with a constraint to pick exactly two assets.

        Parameters:
        - risk_appetite (float): Balances the trade-off between return and risk (default is 0.5).

        Returns:
        - list: Selected asset tickers based on the optimization outcome.
        """
        mu, sigma = self._fetch_market_data()
        
        qp = QuadraticProgram("LiveStockSelection")
        for t in self.tickers:
            qp.binary_var(name=t)

        # Objective: Maximize (Return) - (Risk_Appetite * Volatility)
        # linear: mu[i], quadratic: -risk_appetite * sigma[i][j]
        linear_dict = {self.tickers[i]: mu[self.tickers[i]] for i in range(self.num_assets)}
        
        quadratic_dict = {}
        for i in range(self.num_assets):
            for j in range(self.num_assets):
                quadratic_dict[(self.tickers[i], self.tickers[j])] = \
                    -risk_appetite * sigma.loc[self.tickers[i], self.tickers[j]]
        
        qp.maximize(linear=linear_dict, quadratic=quadratic_dict)

        # Constraint: Pick exactly 2 assets for the portfolio
        qp.linear_constraint(linear={t: 1 for t in self.tickers}, sense="==", rhs=2)

        # Quantum Solve
        qaoa = QAOA(optimizer=COBYLA(maxiter=50), sampler=self.sampler)
        optimizer = MinimumEigenOptimizer(qaoa)
        result = optimizer.solve(qp)

        # Map back to ticker names
        selected = [self.tickers[i] for i, val in enumerate(result.x) if val > 0.5]
        return selected

class QuantumVaR:
    """
    Quantum-Enhanced Portfolio Value at Risk (VaR) Estimation.

    This class calculates the 95% confidence VaR for a portfolio based on live volatility 
    estimates from constituent pricers.

    Attributes:
    - total_portfolio_value (float): Total monetary value of the portfolio.
    - pricer_list (list): List of QuantumPricer instances, each representing an asset.

    Methods:
    - estimate_risk(): Computes and reports the portfolio's VaR at 95% confidence.
    """
    def __init__(self, total_portfolio_value, pricer_list):
        self.value = total_portfolio_value
        self.pricers = pricer_list

    def estimate_risk(self):
        """
        Calculates the 95% confidence level VaR using live volatility estimates.

        Computes a weighted sum of individual asset volatilities, then applies the Z-score 
        for 95% confidence to estimate potential loss.

        Returns:
        - float: Estimated VaR value in monetary units.
        """
        """Uses live volatility from each pricer to calculate VaR."""
        # Pull the 'vol' attribute directly from your QuantumPricer instances
        weights = [1/len(self.pricers)] * len(self.pricers)
        total_vol = sum(p.vol * w for p, w in zip(self.pricers, weights))
        
        # 95% Confidence Interval (Z-score 1.645)
        var_95 = self.value * total_vol * 1.645
        
        print(f"Portfolio Value-at-Risk (95%): ${var_95:,.2f}")
        return var_95
