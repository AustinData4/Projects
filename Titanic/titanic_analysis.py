#!/usr/bin/env python3
"""
Titanic Survival Prediction Project
Author: Austin Charbonneau
Email: austin.charbonneau@und.edu 

This project analyzes the Titanic dataset to predict passenger survival.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load the Titanic training and test datasets."""
    print("Loading Titanic dataset...")
    
    try:
        # Load training data
        train_data = pd.read_csv('train.csv')
        print(f"Training data shape: {train_data.shape}")
        
        # Load test data
        test_data = pd.read_csv('test.csv')
        print(f"Test data shape: {test_data.shape}")
        
        return train_data, test_data
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        print("Please ensure train.csv and test.csv are in the current directory.")
        return None, None

def explore_data(train_data):
    """Perform exploratory data analysis on the training dataset."""
    print("\n=== EXPLORATORY DATA ANALYSIS ===")
    
    # Basic info
    print("\nDataset Info:")
    print(train_data.info())
    
    # First few rows
    print("\nFirst 5 rows:")
    print(train_data.head())
    
    # Missing values
    print("\nMissing values:")
    print(train_data.isnull().sum())
    
    # Survival statistics
    print(f"\nSurvival rate: {train_data['Survived'].mean():.2%}")
    
    # Survival by gender
    print("\nSurvival by gender:")
    print(train_data.groupby('Sex')['Survived'].agg(['count', 'sum', 'mean']))
    
    # Survival by class
    print("\nSurvival by passenger class:")
    print(train_data.groupby('Pclass')['Survived'].agg(['count', 'sum', 'mean']))

def preprocess_data(train_data, test_data):
    """Clean and preprocess the data for machine learning."""
    print("\n=== DATA PREPROCESSING ===")
    
    # Combine datasets for consistent preprocessing
    all_data = [train_data, test_data]
    
    for dataset in all_data:
        # Fill missing ages with median age
        dataset['Age'].fillna(dataset['Age'].median(), inplace=True)
        
        # Fill missing embarked with mode
        dataset['Embarked'].fillna(dataset['Embarked'].mode()[0], inplace=True)
        
        # Fill missing fare with median fare
        dataset['Fare'].fillna(dataset['Fare'].median(), inplace=True)
        
        # Create family size feature
        dataset['FamilySize'] = dataset['SibSp'] + dataset['Parch'] + 1
        
        # Create is alone feature
        dataset['IsAlone'] = 0
        dataset.loc[dataset['FamilySize'] == 1, 'IsAlone'] = 1
        
        # Create title feature from name
        dataset['Title'] = dataset['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
        dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
        dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')
        
        # Convert categorical variables to numeric
        dataset['Sex'] = dataset['Sex'].map({'female': 1, 'male': 0})
        dataset['Embarked'] = dataset['Embarked'].map({'S': 0, 'C': 1, 'Q': 2})
        dataset['Title'] = dataset['Title'].map({"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5})
        dataset['Title'] = dataset['Title'].fillna(0)
    
    print("Data preprocessing completed!")
    return train_data, test_data

def train_model(train_data):
    """Train a machine learning model on the preprocessed data."""
    print("\n=== MODEL TRAINING ===")
    
    # Select features for training
    feature_columns = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'FamilySize', 'IsAlone', 'Title']
    X = train_data[feature_columns]
    y = train_data['Survived']
    
    # Split data for validation
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions on validation set
    y_pred = model.predict(X_val)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_val, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature importance:")
    print(feature_importance)
    
    return model, feature_columns

def make_predictions(model, test_data, feature_columns):
    """Generate predictions for the test set."""
    print("\n=== MAKING PREDICTIONS ===")
    
    X_test = test_data[feature_columns]
    predictions = model.predict(X_test)
    
    # Create submission file
    submission = pd.DataFrame({
        'PassengerId': test_data['PassengerId'],
        'Survived': predictions
    })
    
    submission.to_csv('submission.csv', index=False)
    print("Predictions saved to submission.csv")
    
    return submission

def main():
    """Main function to run the Titanic analysis."""
    print("=== TITANIC SURVIVAL PREDICTION ===")
    print("Author: Austin Charbonneau")
    print("Email: austin.charbonneau@und.edu\n")
    
    # Load data
    train_data, test_data = load_data()
    if train_data is None:
        return
    
    # Explore data
    explore_data(train_data)
    
    # Preprocess data
    train_data, test_data = preprocess_data(train_data, test_data)
    
    # Train model
    model, feature_columns = train_model(train_data)
    
    # Make predictions
    submission = make_predictions(model, test_data, feature_columns)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total predictions made: {len(submission)}")
    print(f"Predicted survivors: {submission['Survived'].sum()}")
    print(f"Survival rate prediction: {submission['Survived'].mean():.2%}")

if __name__ == "__main__":
    main()
