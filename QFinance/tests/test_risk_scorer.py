import numpy as np
from qiskit.primitives import StatevectorSampler as Sampler
from qiskit_algorithms.state_fidelities import ComputeUncompute
from QFinance.strategies import QuantumRiskScorer

def test_quantum_risk_scoring_flow():
    print("\n--- Starting Quantum Risk Scorer Test ---")
    
    # 1. Setup
    sampler = Sampler()
    fidelity = ComputeUncompute(sampler=sampler)
    scorer = QuantumRiskScorer(sampler, fidelity)

    # 2. Dummy Training Data
    X_train = np.array([[0.1, 0.9, 0.8], [0.8, 0.2, 0.1]])
    y_train = np.array([0, 1]) # 0 = Safe, 1 = Default

    # 3. Train
    print("Training Quantum SVC on client data...")
    scorer.train_model(X_train, y_train)
    
    # 4. Predict
    test_client = np.array([[0.85, 0.15, 0.1]])
    result = scorer.predict_default(test_client)
    
    # THIS PRINT WILL SHOW UP WITH -s
    print(f"Prediction for High-Risk Client: {result}")
    
    assert result in ["Default Risk", "Safe"]
    print("--- Test Completed Successfully ---")
