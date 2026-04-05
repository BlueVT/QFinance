from qiskit.primitives import StatevectorSampler as Sampler
from QFinance.pricer import QuantumPricer
from QFinance.strategies import QuantumPortfolio
from QFinance.strategies import QuantumVaR

def test_portfolio_optimization_and_var():
    """Test T2: QAOA Optimization and Value-at-Risk."""
    tickers = ["NVDA", "JNJ", "KO", "AAPL", "MSFT"]
    PORTFOLIO_VALUE = 100000
    sampler = Sampler()

    # Portfolio Engine
    portfolio_engine = QuantumPortfolio(tickers, sampler)
    risk_appetite = 0.7 
    best_assets = portfolio_engine.optimize_allocation(risk_appetite=risk_appetite)
    
    assert len(best_assets) > 0
    assert isinstance(best_assets, list)

    # Risk Analysis
    selected_pricers = [QuantumPricer(t, strike=100, expiry_days=30) for t in best_assets]
    risk_engine = QuantumVaR(total_portfolio_value=PORTFOLIO_VALUE, pricer_list=selected_pricers)
    var_95 = risk_engine.estimate_risk()

    assert var_95 >= 0
    print(f"Max Daily Loss: ${var_95:,.2f}")
