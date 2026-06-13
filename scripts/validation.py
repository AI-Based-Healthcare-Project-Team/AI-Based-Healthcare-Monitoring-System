# Data Validation Script
# Validates diabetes dataset quality and completeness
# Usage: python scripts/validation.py

import pandas as pd

def validate_dataset(filepath):
    """Validate dataset structure and quality"""
    df = pd.read_csv(filepath)
    print(f'Dataset shape: {df.shape}')
    print(f'Missing values: {df.isnull().sum().sum()}')
    return df

if __name__ == '__main__':
    validate_dataset('datasets/diabetes/diabetes_master_dataset.csv')

# Made with Bob
