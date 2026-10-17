"""Fetch Heart Disease dataset, perform EDA, and save clean snapshot."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ucimlrepo import fetch_ucirepo

def main():
    # Fetch dataset (Heart Disease is ID 45)
    heart_disease = fetch_ucirepo(id=45)
    X = heart_disease.data.features
    y = heart_disease.data.targets

    # Combine for EDA and cleaning
    df = pd.concat([X, y], axis=1)

# Save the original, raw data before any modifications
#    df.to_csv("heart_data_raw.csv", index=False)
    
    # Handle missing values (e.g., dropping rows with NaNs in ca or thal)
    df = df.dropna()
    
    # Binarize target: 0 = no disease, 1-4 = presence of disease
    df['num'] = df['num'].apply(lambda x: 1 if x > 0 else 0)

    # --- Exploratory Data Analysis (EDA) ---
    # 1. Class Balance
    plt.figure(figsize=(6, 4))
    sns.countplot(x='num', data=df)
    plt.title("Class Balance: Heart Disease Presence")
    plt.savefig("eda_class_balance.png")

    # 2. Correlation Heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Feature Correlation Heatmap")
    plt.savefig("eda_correlation.png")

    # Save clean dataset for reproducibility
    df.to_csv("heart_data.csv", index=False)
    print(f"Data cleaned and saved. Total rows: {len(df)}. Positive diagnosis rate: {df['num'].mean():.2%}")

if __name__ == "__main__":
    main()