# Titanic Survival Prediction

This project analyzes the famous Titanic dataset to predict passenger survival using machine learning techniques.

## Author
- **Name:** Austin Charbonneau
- **Email:** austin.charbonneau@und.edu

## Project Overview

The goal is to predict which passengers survived the Titanic disaster based on various features like:
- Passenger class
- Gender
- Age
- Number of siblings/spouses aboard
- Number of parents/children aboard
- Fare paid
- Port of embarkation

## Files

- `titanic_analysis.py` - Main analysis script
- `requirements.txt` - Python dependencies
- `train.csv` - Training dataset (you need to download this)
- `test.csv` - Test dataset (you need to download this)
- `submission.csv` - Generated predictions (created after running)

## Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Download the Titanic dataset from Kaggle:
   - Go to https://www.kaggle.com/c/titanic/data
   - Download `train.csv` and `test.csv`
   - Place them in this directory

3. Run the analysis:
   ```bash
   python titanic_analysis.py
   ```

## Features

- **Data Exploration:** Comprehensive EDA with visualizations
- **Data Preprocessing:** Handles missing values and creates new features
- **Feature Engineering:** Creates family size, title, and other derived features
- **Machine Learning:** Uses Random Forest classifier
- **Model Evaluation:** Cross-validation and accuracy metrics
- **Prediction Generation:** Creates submission file for Kaggle

## Key Features Created

- **FamilySize:** Total family members (SibSp + Parch + 1)
- **IsAlone:** Binary indicator for passengers traveling alone
- **Title:** Extracted from passenger names (Mr, Miss, Mrs, Master, Rare)

## Model Performance

The Random Forest model typically achieves 80-85% accuracy on the validation set.
