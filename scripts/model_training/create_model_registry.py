"""
Create Model Registry JSON
Generates a comprehensive registry of all trained models
"""

import pandas as pd
import pickle
import json
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')


def get_model_info(module_name):
    """Get comprehensive information about a trained model"""
    
    model_path = Path(f'models/{module_name}_model.pkl')
    scaler_path = Path(f'models/{module_name}_scaler.pkl')
    
    if not model_path.exists():
        return None
    
    try:
        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Load test data to get feature names
        X_test = pd.read_csv(f'datasets/{module_name}/ml_ready/X_test.csv')
        y_test = pd.read_csv(f'datasets/{module_name}/ml_ready/y_test.csv')
        
        # Remove problematic columns
        cols_to_drop = ['dataset_split', 'Unnamed: 0']
        for col in cols_to_drop:
            if col in X_test.columns:
                X_test = X_test.drop(columns=[col])
        
        # Handle categorical columns
        categorical_cols = X_test.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                le = LabelEncoder()
                X_test[col] = le.fit_transform(X_test[col].astype(str))
        
        # Handle missing values
        if X_test.isnull().any().any():
            imputer = SimpleImputer(strategy='median')
            X_test = pd.DataFrame(
                imputer.fit_transform(X_test),
                columns=X_test.columns
            )
        
        feature_names = X_test.columns.tolist()
        target_column = y_test.columns[0]
        
        # Get model type
        model_type = type(model).__name__
        
        # Read metrics from MODEL_SUMMARY.txt
        summary_path = Path(f'reports/{module_name}/MODEL_SUMMARY.txt')
        metrics = {}
        
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                content = f.read()
                
                # Extract best model metrics
                if 'Selected Model:' in content:
                    lines = content.split('\n')
                    in_metrics = False
                    for line in lines:
                        if 'Performance Metrics:' in line:
                            in_metrics = True
                            continue
                        if in_metrics and '- Accuracy:' in line:
                            metrics['accuracy'] = float(line.split(':')[1].strip())
                        elif in_metrics and '- Precision:' in line:
                            metrics['precision'] = float(line.split(':')[1].strip())
                        elif in_metrics and '- Recall:' in line:
                            metrics['recall'] = float(line.split(':')[1].strip())
                        elif in_metrics and '- F1 Score:' in line:
                            metrics['f1_score'] = float(line.split(':')[1].strip())
                        elif in_metrics and '- ROC-AUC:' in line:
                            metrics['roc_auc'] = float(line.split(':')[1].strip())
                        elif in_metrics and line.strip() == '':
                            break
        
        # Determine target meaning
        target_meanings = {
            'heart': 'Heart disease presence (0: No, 1: Yes)',
            'kidney': 'Kidney disease presence (0: No, 1: Yes)',
            'lung': 'Lung cancer type (0: Benign, 1: Malignant, 2: Normal)',
            'diabetes': 'Diabetes classification (0: Normal, 1: Prediabetes, 2: Diabetes)',
            'thyroid': 'Thyroid condition (normal, subnormal, hyperthyroid)',
            'liver': 'Liver disease indicator (1: No disease, 2: Disease)',
            'gallbladder': 'Gallstone presence (0: No, 1: Yes)',
            'mental_health': 'Stress level classification',
            'survey': 'Glucose risk level (normal, prediabetes, diabetes)'
        }
        
        return {
            'module_name': module_name,
            'model_path': str(model_path),
            'scaler_path': str(scaler_path) if scaler_path.exists() else None,
            'model_type': model_type,
            'feature_names': feature_names,
            'num_features': len(feature_names),
            'target_column': target_column,
            'target_meaning': target_meanings.get(module_name, 'Disease classification'),
            'metrics': metrics,
            'status': 'ready'
        }
        
    except Exception as e:
        print(f"Error processing {module_name}: {str(e)}")
        return None


def create_registry():
    """Create complete model registry"""
    
    modules = [
        'heart', 'kidney', 'lung', 'diabetes', 
        'thyroid', 'liver', 'gallbladder', 
        'mental_health', 'survey'
    ]
    
    registry = {
        'project': 'Healthcare Monitoring and Early Disease Prediction System',
        'version': '1.0',
        'models': {}
    }
    
    print("\n" + "="*70)
    print("CREATING MODEL REGISTRY")
    print("="*70)
    
    for module in modules:
        print(f"\nProcessing {module}...")
        
        info = get_model_info(module)
        
        if info:
            registry['models'][module] = info
            print(f"  [OK] {module}: {info['model_type']} - {info['status']}")
        else:
            # Add pending modules
            if module == 'mental_health':
                registry['models'][module] = {
                    'module_name': module,
                    'status': 'pending',
                    'reason': 'Empty ml_ready files - feature engineering required'
                }
            elif module == 'gallbladder':
                registry['models'][module] = {
                    'module_name': module,
                    'status': 'pending',
                    'reason': 'Insufficient data - only one class present'
                }
            else:
                registry['models'][module] = {
                    'module_name': module,
                    'status': 'pending',
                    'reason': 'Model not trained'
                }
            print(f"  [PENDING] {module}: {registry['models'][module]['reason']}")
    
    # Save registry
    registry_path = Path('models/model_registry.json')
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Registry saved: {registry_path}")
    print(f"{'='*70}")
    
    # Summary
    ready_count = sum(1 for m in registry['models'].values() if m['status'] == 'ready')
    pending_count = sum(1 for m in registry['models'].values() if m['status'] == 'pending')
    
    print(f"\nSummary:")
    print(f"  Ready models: {ready_count}")
    print(f"  Pending models: {pending_count}")
    print(f"  Total modules: {len(modules)}")
    
    return registry


if __name__ == "__main__":
    registry = create_registry()

# Made with Bob
