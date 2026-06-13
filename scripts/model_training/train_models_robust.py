"""
Robust Model Training Script for Healthcare Prediction System
Handles various data issues and trains models for each module
"""

import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score
)
import warnings
warnings.filterwarnings('ignore')


def load_and_preprocess_data(module_name):
    """Load and preprocess train and test data for a module"""
    base_path = Path(f'datasets/{module_name}/ml_ready')
    
    X_train = pd.read_csv(base_path / 'X_train.csv')
    X_test = pd.read_csv(base_path / 'X_test.csv')
    y_train = pd.read_csv(base_path / 'y_train.csv').values.ravel()
    y_test = pd.read_csv(base_path / 'y_test.csv').values.ravel()
    
    # Remove problematic columns
    cols_to_drop = ['dataset_split', 'Unnamed: 0']
    for col in cols_to_drop:
        if col in X_train.columns:
            X_train = X_train.drop(columns=[col])
            X_test = X_test.drop(columns=[col])
    
    # Handle categorical columns
    categorical_cols = X_train.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            X_train[col] = le.fit_transform(X_train[col].astype(str))
            X_test[col] = le.transform(X_test[col].astype(str))
            label_encoders[col] = le
    
    # Handle missing values
    if X_train.isnull().any().any():
        imputer = SimpleImputer(strategy='median')
        X_train = pd.DataFrame(
            imputer.fit_transform(X_train),
            columns=X_train.columns
        )
        X_test = pd.DataFrame(
            imputer.transform(X_test),
            columns=X_test.columns
        )
    
    return X_train, X_test, y_train, y_test


def check_data_validity(X_train, y_train, module_name):
    """Check if data is valid for classification"""
    # Check if y is continuous (regression problem)
    unique_y = np.unique(y_train)
    if len(unique_y) > 20 and y_train.dtype in [np.float64, np.float32]:
        return False, f"Target appears to be continuous (regression), not classification. Unique values: {len(unique_y)}"
    
    # Check if only one class
    if len(unique_y) < 2:
        return False, f"Only one class found in training data: {unique_y}"
    
    # Check sample size
    if len(X_train) < 10:
        return False, f"Insufficient training samples: {len(X_train)}"
    
    return True, "Data is valid"


def train_and_evaluate_models(X_train, X_test, y_train, y_test, module_name):
    """Train and evaluate all models"""
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Initialize models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'Support Vector Machine': SVC(kernel='rbf', probability=True, random_state=42)  # type: ignore
    }
    
    results = {}
    
    print(f"\n{'='*60}")
    print(f"Training models for {module_name.upper()} module")
    print(f"{'='*60}")
    
    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        
        try:
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)  # type: ignore
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)  # type: ignore
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)  # type: ignore
            
            # ROC-AUC (only for binary classification)
            try:
                if len(np.unique(y_test)) == 2 and y_pred_proba is not None:
                    roc_auc = roc_auc_score(y_test, y_pred_proba)
                else:
                    roc_auc = None
            except:
                roc_auc = None
            
            results[model_name] = {
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'roc_auc': roc_auc
            }
            
            print(f"  Accuracy:  {accuracy:.4f}")
            print(f"  Precision: {precision:.4f}")
            print(f"  Recall:    {recall:.4f}")
            print(f"  F1 Score:  {f1:.4f}")
            if roc_auc:
                print(f"  ROC-AUC:   {roc_auc:.4f}")
        
        except Exception as e:
            print(f"  [ERROR] Failed to train {model_name}: {str(e)}")
            continue
    
    if not results:
        raise Exception("All models failed to train")
    
    return results, scaler


def select_best_model(results):
    """Select best model based on F1 score and Recall"""
    best_model_name = None
    best_score = -1
    
    for model_name, metrics in results.items():
        # Prioritize F1 score with recall as tiebreaker
        combined_score = metrics['f1_score'] * 0.6 + metrics['recall'] * 0.4
        
        if combined_score > best_score:
            best_score = combined_score
            best_model_name = model_name
    
    return best_model_name


def save_model_and_scaler(model, scaler, module_name):
    """Save the best model and scaler"""
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    # Save model
    model_path = models_dir / f'{module_name}_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save scaler
    scaler_path = models_dir / f'{module_name}_scaler.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    return model_path, scaler_path


def create_summary_report(module_name, results, best_model_name, model_path, scaler_path):
    """Create a summary report for the module"""
    report_dir = Path(f'reports/{module_name}')
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / 'MODEL_SUMMARY.txt'
    
    with open(report_path, 'w') as f:
        f.write(f"{'='*70}\n")
        f.write(f"MODEL TRAINING SUMMARY - {module_name.upper()} MODULE\n")
        f.write(f"{'='*70}\n\n")
        
        f.write("MODELS TRAINED:\n")
        f.write("-" * 70 + "\n")
        for i, model_name in enumerate(results.keys(), 1):
            f.write(f"{i}. {model_name}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("EVALUATION METRICS:\n")
        f.write("="*70 + "\n\n")
        
        for model_name, metrics in results.items():
            f.write(f"{model_name}:\n")
            f.write(f"  - Accuracy:  {metrics['accuracy']:.4f}\n")
            f.write(f"  - Precision: {metrics['precision']:.4f}\n")
            f.write(f"  - Recall:    {metrics['recall']:.4f}\n")
            f.write(f"  - F1 Score:  {metrics['f1_score']:.4f}\n")
            if metrics['roc_auc']:
                f.write(f"  - ROC-AUC:   {metrics['roc_auc']:.4f}\n")
            f.write("\n")
        
        f.write("="*70 + "\n")
        f.write("BEST MODEL SELECTION:\n")
        f.write("="*70 + "\n\n")
        f.write(f"Selected Model: {best_model_name}\n\n")
        
        best_metrics = results[best_model_name]
        f.write("Performance Metrics:\n")
        f.write(f"  - Accuracy:  {best_metrics['accuracy']:.4f}\n")
        f.write(f"  - Precision: {best_metrics['precision']:.4f}\n")
        f.write(f"  - Recall:    {best_metrics['recall']:.4f}\n")
        f.write(f"  - F1 Score:  {best_metrics['f1_score']:.4f}\n")
        if best_metrics['roc_auc']:
            f.write(f"  - ROC-AUC:   {best_metrics['roc_auc']:.4f}\n")
        
        f.write("\nSelection Criteria:\n")
        f.write("  - Primary: F1 Score (60% weight)\n")
        f.write("  - Secondary: Recall (40% weight)\n")
        f.write("  - Rationale: In healthcare prediction, minimizing false negatives\n")
        f.write("    (high recall) is critical while maintaining overall balance (F1).\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("SAVED FILES:\n")
        f.write("="*70 + "\n\n")
        f.write(f"Model File:  {model_path}\n")
        f.write(f"Scaler File: {scaler_path}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("NOTES:\n")
        f.write("="*70 + "\n\n")
        f.write("- All features were standardized using StandardScaler\n")
        f.write("- Categorical features were label-encoded\n")
        f.write("- Missing values were imputed using median strategy\n")
        f.write("- The scaler must be applied to new data before prediction\n")
        f.write("- Load model and scaler using pickle for inference\n")
    
    return report_path


def train_module(module_name):
    """Complete training pipeline for a module"""
    try:
        print(f"\n{'#'*70}")
        print(f"# Processing {module_name.upper()} Module")
        print(f"{'#'*70}")
        
        # Load data
        print("\nLoading data...")
        X_train, X_test, y_train, y_test = load_and_preprocess_data(module_name)
        print(f"  Training samples: {len(X_train)}")
        print(f"  Testing samples:  {len(X_test)}")
        print(f"  Features:         {X_train.shape[1]}")
        
        # Check data validity
        is_valid, message = check_data_validity(X_train, y_train, module_name)
        if not is_valid:
            print(f"\n[SKIP] {message}")
            return False
        
        # Train and evaluate models
        results, scaler = train_and_evaluate_models(X_train, X_test, y_train, y_test, module_name)
        
        # Select best model
        best_model_name = select_best_model(results)
        print(f"\n{'='*60}")
        print(f"BEST MODEL: {best_model_name}")
        print(f"{'='*60}")
        
        # Save model and scaler
        print("\nSaving model and scaler...")
        model_path, scaler_path = save_model_and_scaler(
            results[best_model_name]['model'], 
            scaler, 
            module_name
        )
        print(f"  Model saved:  {model_path}")
        print(f"  Scaler saved: {scaler_path}")
        
        # Create summary report
        print("\nCreating summary report...")
        report_path = create_summary_report(
            module_name, 
            results, 
            best_model_name, 
            model_path, 
            scaler_path
        )
        print(f"  Report saved: {report_path}")
        
        print(f"\n[SUCCESS] {module_name.upper()} module training completed successfully!\n")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error training {module_name} module: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main training function"""
    modules = [
        'heart', 'kidney', 'lung', 'diabetes', 
        'thyroid', 'liver', 'gallbladder', 
        'mental_health', 'survey'
    ]
    
    print("\n" + "="*70)
    print("HEALTHCARE PREDICTION SYSTEM - MODEL TRAINING")
    print("="*70)
    print(f"\nModules to train: {len(modules)}")
    print(f"Models per module: 3 (Logistic Regression, Random Forest, SVM)")
    print(f"Total models to train: {len(modules) * 3}")
    
    successful = []
    failed = []
    skipped = []
    
    for module in modules:
        result = train_module(module)
        if result:
            successful.append(module)
        else:
            failed.append(module)
    
    # Final summary
    print("\n" + "="*70)
    print("TRAINING COMPLETE - FINAL SUMMARY")
    print("="*70)
    print(f"\nSuccessful: {len(successful)}/{len(modules)} modules")
    if successful:
        print("  [+] " + ", ".join(successful))
    
    if failed:
        print(f"\nFailed/Skipped: {len(failed)}/{len(modules)} modules")
        print("  [-] " + ", ".join(failed))
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()

# Made with Bob
