"""Pytest configuration and fixtures"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing playbooks"""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        'age': np.random.randint(20, 80, n),
        'glucose': np.random.normal(100, 20, n),
        'bmi': np.random.normal(25, 5, n),
        'outcome': np.random.choice([0, 1], n, p=[0.6, 0.4]),
        'pregnancies': np.random.randint(0, 10, n),
    })


@pytest.fixture
def empty_dataframe():
    """Create an empty DataFrame"""
    return pd.DataFrame()


@pytest.fixture
def minimal_dataframe():
    """Create a minimal DataFrame with few rows"""
    return pd.DataFrame({
        'value': [1, 2, 3],
        'label': ['a', 'b', 'c']
    })


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

