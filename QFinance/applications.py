import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class QuantumAnalytics:
    """
    Advanced analytics for Quantum Option Pricing, including Greeks and Stress Testing.
    """
    def __init__(self, ticker, strike, expiry):
        from .pricer import QuantumPricer
        self.pricer = QuantumPricer(ticker, strike, expiry)
        self.strike = strike

    def visualize_payoff_grid(self):
        """
        Generates a 3D surface plot: Option Price vs Spot vs Volatility.
        """
        print(f"Constructing 3D Quantum Surface for {self.pricer.ticker}...")
        
        # Ranges for the surface
        spots = np.linspace(self.pricer.spot * 0.8, self.pricer.spot * 1.2, 10)
        vols = np.linspace(0.1, 0.6, 10)
        S, V = np.meshgrid(spots, vols)
        
        # Calculate Quantum Prices for the mesh
        Z = np.zeros(S.shape)
        for i in range(len(vols)):
            for j in range(len(spots)):
                # Temporarily update pricer state
                self.pricer.spot = spots[j]
                self.pricer.vol = vols[i]
                # Use a fast 3-qubit Euro manual for the surface
                Z[i, j] = self.pricer.price_euro_manual(qubits=3)

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(S, V, Z, cmap='magma', edgecolor='none', alpha=0.9)
        
        ax.set_title(f"Quantum Option Surface: {self.pricer.ticker} (${self.strike} Strike)")
        ax.set_xlabel('Spot Price ($)')
        ax.set_ylabel('Volatility (σ)')
        ax.set_zlabel('Option Price ($)')
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        plt.show()

    def calculate_quantum_greeks(self):
        """
        Calculates Delta (Price Sensitivity) and Vega (Vol Sensitivity).
        """
        print(f"\n--- Calculating Quantum Greeks for {self.pricer.ticker} ---")
        
        # Baseline Price
        base_price = self.pricer.price_euro_manual(qubits=5)
        
        # 1. Delta: Change in Option Price / $1 change in Spot
        ds = 1.0
        self.pricer.spot += ds
        up_price = self.pricer.price_euro_manual(qubits=5)
        delta = (up_price - base_price) / ds
        self.pricer.spot -= ds # Reset
        
        # 2. Vega: Change in Option Price / 1% change in Vol
        dv = 0.01
        self.pricer.vol += dv
        vol_up_price = self.pricer.price_euro_manual(qubits=5)
        vega = (vol_up_price - base_price) / (dv * 100)
        self.pricer.vol -= dv # Reset

        print(f"Quantum Delta: {delta:.4f} (Profit per $1 stock move)")
        print(f"Quantum Vega:  {vega:.4f} (Profit per 1% vol move)")
        return delta, vega

    def run_stress_test(self):
        """
        Black Swan: Market Crash simulation showing potential portfolio impact.
        """
        print(f"\n[STRESS TEST] Simulating 1987 'Black Monday' for {self.pricer.ticker}...")
        orig_vol = self.pricer.vol
        self.pricer.vol = 0.80 # 80% Volatility spike
        crash_price = self.pricer.price_euro_manual()
        print(f"Crash-State Asian Price: ${crash_price:.2f}")
        self.pricer.vol = orig_vol
