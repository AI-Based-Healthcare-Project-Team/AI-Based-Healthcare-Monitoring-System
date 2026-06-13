# AI-Based Healthcare Monitoring System

AI-powered system for real-time healthcare monitoring, enabling early detection of health risks and personalized patient insights.

## Project Structure

```
PROJECT/
│
├── datasets/                    # All datasets organized by health condition
│   ├── heart/
│   ├── kidney/
│   ├── lung/
│   ├── diabetes/
│   ├── thyroid/
│   ├── liver/
│   ├── gallbladder/
│   ├── mental_health/
│   └── survey/
│
├── reports/                     # Analysis reports and visualizations
│   ├── heart/
│   ├── kidney/
│   ├── lung/
│   ├── diabetes/
│   ├── thyroid/
│   ├── liver/
│   ├── gallbladder/
│   ├── mental_health/
│   └── survey/
│
├── scripts/                     # Data processing and analysis scripts
│
└── README.md                    # This file
```

## Datasets

### Available Health Condition Datasets

1. **Heart Disease** - Cardiovascular health monitoring data
2. **Kidney Disease** - Renal function and health indicators
3. **Lung Disease** - Respiratory health metrics
4. **Diabetes** - Blood glucose and metabolic indicators
5. **Thyroid Disorders** - Thyroid function test results
6. **Liver Disease** - Hepatic function markers
7. **Gallbladder Disease** - Gallstone and gallbladder health data
8. **Mental Health** - Psychological health assessments
9. **Survey Data** - General health survey responses

## Reports

Each health condition has its own reports directory containing:
- Exploratory Data Analysis (EDA) results
- Statistical summaries
- Correlation matrices
- Feature engineering reports
- Visualization plots (boxplots, heatmaps, distributions, etc.)

## Scripts

The `scripts/` directory contains Python scripts for:
- Data cleaning and preprocessing
- Exploratory data analysis
- Feature engineering
- Initial assessments
- Data conversion and formatting

## Getting Started

1. Navigate to the specific dataset folder in `datasets/` to access raw and processed data
2. Check the corresponding `reports/` folder for analysis results and visualizations
3. Use scripts from `scripts/` folder for data processing and analysis

## Data Processing Pipeline

1. **Initial Assessment** - Understand data structure and quality
2. **Data Cleaning** - Handle missing values, duplicates, and outliers
3. **Exploratory Analysis** - Generate statistical summaries and visualizations
4. **Feature Engineering** - Create new features and transform existing ones
5. **Report Generation** - Document findings and save processed datasets

## Notes

- Each dataset folder may contain README files with specific information about that health condition
- Processed datasets are typically saved with suffixes like `_cleaned.csv` or `_engineered.csv`
- All visualizations are saved in the respective `reports/[condition]/eda/plots/` directories
