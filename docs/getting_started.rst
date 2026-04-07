Getting Started
===============

Welcome to QFinance! This guide will help you set up and begin using the library for quantum-enhanced financial analysis.

Installation
------------
First, install QFinance via pip:

.. code-block:: bash

    pip install qfinance

Basic Usage
-----------
Import the library and initialize your objects:

.. code-block:: python

    import qfinance

Now you can create instances of the core classes, such as `QuantumPricer`, `QuantumPortfolio`, etc.

Example: Pricing an Option
--------------------------
.. code-block:: python
    
    from qfinance import QuantumPricer

    # Create a pricer for Apple with a strike price of $150 and 30 days to expiry
    qp = QuantumPricer(ticker='AAPL', strike=150, expiry_days=30)

    # Calculate the option price
    price = qp.price_euro_manual()
    print(f"Estimated option price: ${price:.2f}")

