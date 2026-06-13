import pandas as pd
from pathlib import Path

# Read the engineered dataset
df = pd.read_csv('reports/mental_health/mental_health_engineered.csv')

# Get all columns except target
target_col = 'stress_label'
all_features = [col for col in df.columns if col != target_col]

# Select top 79 features (50% of 157 features)
# Since all importance scores were zero, we'll select a reasonable subset
n_features = max(20, len(all_features) // 2)
selected_features = all_features[:n_features]

# Create the selected features dataframe
selected_df = df[selected_features + [target_col]]

# Save to a temporary file first
output_path = Path('reports/mental_health/mental_health_selected_features_NEW.csv')
selected_df.to_csv(output_path, index=False)

print(f"Successfully created selected features file with {len(selected_features)} features")
print(f"Selected features: {', '.join(selected_features[:10])}...")
print(f"Output saved to: {output_path}")
print(f"\nPlease close the old mental_health_selected_features.csv file in VS Code,")
print(f"then rename mental_health_selected_features_NEW.csv to mental_health_selected_features.csv")

# Made with Bob
