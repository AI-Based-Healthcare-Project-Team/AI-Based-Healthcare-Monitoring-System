# EDA Script - Performs exploratory data analysis on diabetes dataset
# This script generates visualizations and statistical summaries
# Usage: python scripts/perform_eda.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load master dataset
df = pd.read_csv('datasets/diabetes/diabetes_master_dataset.csv')
print(f'Loaded {len(df)} patients')
print(df.describe())

# Made with Bob
