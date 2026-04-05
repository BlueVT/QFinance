"""
Unit and regression test for the QFinance package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import QFinance


def test_QFinance_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "QFinance" in sys.modules
