QFinance
==============================
[![GitHub Actions Build Status](https://github.com/BlueVT/QFinance/workflows/CI/badge.svg)](https://github.com/BlueVT/QFinance/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/BlueVT/QFinance/branch/main/graph/badge.svg)](https://codecov.io/gh/BlueVT/QFinance/branch/main)


# Quantum Financial Analytics Suite

This project offers a collection of quantum-enhanced tools for financial modeling, including credit risk prediction, portfolio optimization, VaR estimation, and options pricing. Leveraging quantum machine learning and optimization algorithms, these tools aim to improve accuracy and efficiency in complex financial analyses.

## Features

- **Credit Risk Prediction**: Use Quantum Machine Learning (QSVC) for default risk assessment.
- **Portfolio Optimization**: Select optimal asset subsets based on live market data using QAOA.
- **Risk Management (VaR)**: Estimate portfolio Value at Risk with quantum-based volatility measures.
- **Options Pricing**: Price European, Asian, and American options using quantum algorithms and Monte Carlo methods.

## Classes and Functions Overview

- **QuantumAnalytics** - For option surface visualization, Greeks calculation, and stress testing.
- **QuantumMarketGenerator** - For simulating correlated market moves.
- **QuantumMonteCarloPricer** - For quantum-enhanced Monte Carlo option pricing.
- **ManualEuropeanPricing** - For manual quantum European option pricing.
- **QuantumPricer** - For comprehensive options pricing (European, Asian, American).
- **black_scholes_value** - F function for classical Black-Scholes pricing.
- **QuantumRiskScorer** - For credit risk prediction via QSVC.
- **QuantumPortfolio** - For portfolio optimization using QAOA.
- **QuantumVaR** - For Value at Risk estimation.
## Usage Examples

### Credit Risk Prediction

```python
from your_module_name import QuantumRiskScorer
from qiskit import Aer
from qiskit.utils import QuantumInstance

# Initialize the quantum classifier
classifier = QuantumRiskScorer(sampler=QuantumInstance(Aer.get_backend('qasm_simulator'), shots=1024),
                                fidelity=FidelityQuantumKernel)

# Train with historical data
X_train = [...]  # Your feature data
y_train = [...]  # Your labels
classifier.train_model(X_train, y_train)

# Predict risk for new client
client_data = [[0.3, 0.8, 0.5]]  # Example features
risk_status = classifier.predict_default(client_data)
print(risk_status)
```

### Portfolio Optimization
```python
from your_module_name import QuantumPortfolio
from qiskit import Aer
from qiskit.utils import QuantumInstance

tickers = ['AAPL', 'GOOG', 'MSFT']
backend = Aer.get_backend('qasm_simulator')
quantum_instance = QuantumInstance(backend, shots=1024)

portfolio = QuantumPortfolio(tickers, quantum_instance)
selected_assets = portfolio.optimize_allocation(risk_appetite=0.5)
print("Selected Assets:", selected_assets)
```

### VaR Estimation
```python
from your_module_name import QuantumVaR, QuantumPricer

# Initialize pricers for each asset
pricers = [QuantumPricer(ticker, strike, expiry_days) for ticker, strike, expiry_days in [...]]

# Initialize VaR calculator
portfolio_value = 1_000_000  # Example total portfolio value
vaR = QuantumVaR(portfolio_value, pricers)

# Estimate VaR
vaR.estimate_risk()
```

### Dependencies
- Numpy
- Scipy
- Yfinance
- Qiskit
- Qiskit_finance
- Qiskit_algorithms
- Qiskit_optimization
- Qiskit_machine_learning


### Installation
Create a clean environment and install in editable mode:
```bash
pip install -e .
```

### Notes
Ensure your environment supports Qiskit and has access to quantum simulators or hardware.
Adjust parameters such as qubits, iterations, and confidence levels as needed.

### License
This project is licensed under the MIT License. See the LICENSE file for details.

### Copyright

Copyright (c) 2026, Awida Neji


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.11.
