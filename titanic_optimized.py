#!/usr/bin/env python3
"""
Optimized Titanic Survival Prediction Project
Author: Austin Charbonneau
Email: austin.charbonneau@und.edu 

This project uses advanced machine learning techniques to predict passenger survival
with improved accuracy through ensemble methods, advanced feature engineering, and hyperparameter optimization.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif
import xgboost as xgb
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load the Titanic training and test datasets."""
    print("Loading Titanic dataset...")
    
    try:
        train_data = pd.read_csv('train.csv')
        test_data = pd.read_csv('test.csv')
        print(f"Training data shape: {train_data.shape}")
        print(f"Test data shape: {test_data.shape}")
        return train_data, test_data
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return None, None

def advanced_feature_engineering(train_data, test_data):
    """Advanced feature engineering with more sophisticated techniques."""
    print("\n=== ADVANCED FEATURE ENGINEERING ===")
    
    all_data = [train_data, test_data]
    
    for dataset in all_data:
        # Basic features (from original)
        dataset['FamilySize'] = dataset['SibSp'] + dataset['Parch'] + 1
        dataset['IsAlone'] = (dataset['FamilySize'] == 1).astype(int)
        
        # Extract title from name
        dataset['Title'] = dataset['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
        dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
        dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')
        
        # NEW: Extract deck from cabin
        dataset['Deck'] = dataset['Cabin'].str[0]
        dataset['HasCabin'] = dataset['Cabin'].notna().astype(int)
        
        # NEW: Age grouping
        dataset['AgeGroup'] = pd.cut(dataset['Age'], bins=[0, 12, 18, 35, 60, 100], labels=['Child', 'Teen', 'Adult', 'Middle', 'Senior'])
        
        # NEW: Fare grouping
        dataset['FareGroup'] = pd.qcut(dataset['Fare'], q=4, labels=['Low', 'Medium', 'High', 'VeryHigh'])
        
        # NEW: Ticket prefix analysis
        dataset['TicketPrefix'] = dataset['Ticket'].str.extract('([A-Za-z]+)')
        dataset['TicketPrefix'] = dataset['TicketPrefix'].fillna('None')
        
        # NEW: Name length (potential social status indicator)
        dataset['NameLength'] = dataset['Name'].str.len()
        
        # NEW: Family survival rate (for training data only)
        if 'Survived' in dataset.columns:
            family_survival = dataset.groupby(['SibSp', 'Parch'])['Survived'].mean()
            dataset['FamilySurvivalRate'] = dataset.apply(
                lambda x: family_survival.get((x['SibSp'], x['Parch']), 0.5), axis=1
            )
        else:
            # For test data, use average survival rate
            dataset['FamilySurvivalRate'] = 0.5
        
        # Convert categorical variables
        le = LabelEncoder()
        categorical_features = ['Sex', 'Embarked', 'Title', 'Deck', 'AgeGroup', 'FareGroup', 'TicketPrefix']
        
        for feature in categorical_features:
            if feature in dataset.columns:
                dataset[feature] = dataset[feature].fillna('Unknown')
                dataset[feature] = le.fit_transform(dataset[feature])
        
        # Fill missing values with more sophisticated methods
        # Age: fill based on title and class
        for title in dataset['Title'].unique():
            mask = dataset['Title'] == title
            dataset.loc[mask, 'Age'] = dataset.loc[mask, 'Age'].fillna(
                dataset.loc[mask, 'Age'].median()
            )
        
        # Fill remaining missing ages with overall median
        dataset['Age'] = dataset['Age'].fillna(dataset['Age'].median())
        
        # Fill missing fare with median by class
        for pclass in dataset['Pclass'].unique():
            mask = dataset['Pclass'] == pclass
            dataset.loc[mask, 'Fare'] = dataset.loc[mask, 'Fare'].fillna(
                dataset.loc[mask, 'Fare'].median()
            )
        
        # Fill missing embarked with mode
        dataset['Embarked'] = dataset['Embarked'].fillna(dataset['Embarked'].mode()[0])
    
    print("Advanced feature engineering completed!")
    return train_data, test_data

def train_ensemble_models(train_data):
    """Train multiple models and create an ensemble."""
    print("\n=== ENSEMBLE MODEL TRAINING ===")
    
    # Select features
    feature_columns = [
        'Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked',
        'FamilySize', 'IsAlone', 'Title', 'Deck', 'HasCabin', 'AgeGroup',
        'FareGroup', 'TicketPrefix', 'NameLength', 'FamilySurvivalRate'
    ]
    
    X = train_data[feature_columns]
    y = train_data['Survived']
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features for algorithms that need it
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # Individual models
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
        'XGBoost': xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42),
        'LightGBM': lgb.LGBMClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42),
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    # Train individual models
    model_scores = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        
        if name in ['LogisticRegression', 'SVM']:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_val_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
        
        accuracy = accuracy_score(y_val, y_pred)
        model_scores[name] = accuracy
        trained_models[name] = model
        print(f"{name} accuracy: {accuracy:.4f}")
    
    # Create voting ensemble
    voting_models = [
        ('rf', trained_models['RandomForest']),
        ('xgb', trained_models['XGBoost']),
        ('lgb', trained_models['LightGBM']),
        ('gb', trained_models['GradientBoosting'])
    ]
    
    voting_classifier = VotingClassifier(estimators=voting_models, voting='soft')
    voting_classifier.fit(X_train, y_train)
    voting_pred = voting_classifier.predict(X_val)
    voting_accuracy = accuracy_score(y_val, voting_pred)
    
    print(f"\nVoting Ensemble accuracy: {voting_accuracy:.4f}")
    
    # Feature importance from best model
    best_model_name = max(model_scores, key=model_scores.get)
    best_model = trained_models[best_model_name]
    
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\nFeature importance from {best_model_name}:")
        print(feature_importance.head(10))
    
    return voting_classifier, feature_columns, scaler, model_scores

def hyperparameter_optimization(X_train, y_train):
    """Optimize hyperparameters for the best models."""
    print("\n=== HYPERPARAMETER OPTIMIZATION ===")
    
    # Random Forest optimization
    rf_params = {
        'n_estimators': [100, 200, 300],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        rf_params,
        cv=5,
        scoring='accuracy',
        n_jobs=-1
    )
    
    print("Optimizing Random Forest...")
    rf_grid.fit(X_train, y_train)
    print(f"Best RF params: {rf_grid.best_params_}")
    print(f"Best RF score: {rf_grid.best_score_:.4f}")
    
    return rf_grid.best_estimator_

def make_optimized_predictions(ensemble_model, test_data, feature_columns, scaler):
    """Generate optimized predictions."""
    print("\n=== MAKING OPTIMIZED PREDICTIONS ===")
    
    X_test = test_data[feature_columns]
    predictions = ensemble_model.predict(X_test)
    
    # Create submission file
    submission = pd.DataFrame({
        'PassengerId': test_data['PassengerId'],
        'Survived': predictions
    })
    
    submission.to_csv('submission_optimized.csv', index=False)
    print("Optimized predictions saved to submission_optimized.csv")
    
    return submission

def main():
    """Main function to run the optimized Titanic analysis."""
    print("=== OPTIMIZED TITANIC SURVIVAL PREDICTION ===")
    print("Author: Austin Charbonneau")
    print("Email: austin.charbonneau@und.edu\n")
    
    # Load data
    train_data, test_data = load_data()
    if train_data is None:
        return
    
    # Advanced feature engineering
    train_data, test_data = advanced_feature_engineering(train_data, test_data)
    
    # Train ensemble models
    ensemble_model, feature_columns, scaler, model_scores = train_ensemble_models(train_data)
    
    # Hyperparameter optimization
    X = train_data[feature_columns]
    y = train_data['Survived']
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    optimized_rf = hyperparameter_optimization(X_train, y_train)
    
    # Make predictions
    submission = make_optimized_predictions(ensemble_model, test_data, feature_columns, scaler)
    
    print(f"\n=== OPTIMIZATION SUMMARY ===")
    print(f"Individual model accuracies:")
    for model, score in model_scores.items():
        print(f"  {model}: {score:.4f}")
    
    print(f"\nTotal predictions made: {len(submission)}")
    print(f"Predicted survivors: {submission['Survived'].sum()}")
    print(f"Survival rate prediction: {submission['Survived'].mean():.2%}")

if __name__ == "__main__":
    main()
