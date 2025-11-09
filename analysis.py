# analysis.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler

# ===============================
# 🔹 Existing: Dataset Summary
# ===============================
def summarize_data(df):
    return df.describe(include='all')

# ===============================
# 🔹 Existing: Correlation Matrix
# ===============================
def correlation_matrix(df):
    numeric_df = df.select_dtypes(include=np.number)
    return numeric_df.corr()

# ===============================
# 🔹 Existing: Simple Linear Regression
# ===============================
def simple_regression(df, x_col, y_col):
    from sklearn.linear_model import LinearRegression
    X = df[[x_col]].values
    y = df[y_col].values
    model = LinearRegression()
    model.fit(X, y)
    coef = model.coef_[0]
    intercept = model.intercept_
    r2 = model.score(X, y)
    return {"coefficient": coef, "intercept": intercept, "r_squared": r2, "x_col": x_col, "y_col": y_col}

# ===============================
# 🔹 New: Outlier Detection
# ===============================
def detect_outliers(df, method="IQR", threshold=3):
    """
    Detect outliers in numeric columns.
    method: "IQR" or "zscore"
    threshold: z-score threshold for outliers
    Returns: dataframe of outlier rows
    """
    numeric_df = df.select_dtypes(include=np.number)
    
    if numeric_df.empty:
        return pd.DataFrame()  # No numeric columns
    
    if method == "IQR":
        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1
        outlier_mask = (numeric_df < (Q1 - 1.5 * IQR)) | (numeric_df > (Q3 + 1.5 * IQR))
    elif method == "zscore":
        mean = numeric_df.mean()
        std = numeric_df.std()
        outlier_mask = ((numeric_df - mean).abs() > threshold * std)
    else:
        raise ValueError("method must be 'IQR' or 'zscore'")
    
    return df[outlier_mask.any(axis=1)]

# ===============================
# 🔹 New: Feature Engineering
# ===============================
def create_feature(df, new_col_name, formula):
    """
    Create a new column using a formula string.
    Example: "weight / (height ** 2)"
    """
    try:
        df[new_col_name] = df.eval(formula)
        return df
    except Exception as e:
        raise ValueError(f"Error creating feature: {e}")

def encode_categorical(df, method="onehot", columns=None):
    """
    Encode categorical columns.
    method: "onehot" or "label"
    columns: list of columns to encode. If None, encode all object columns.
    """
    if columns is None:
        columns = df.select_dtypes(include='object').columns.tolist()
    
    df_encoded = df.copy()
    
    if method == "onehot":
        df_encoded = pd.get_dummies(df_encoded, columns=columns, drop_first=True)
    elif method == "label":
        le = LabelEncoder()
        for col in columns:
            df_encoded[col] = le.fit_transform(df_encoded[col])
    else:
        raise ValueError("method must be 'onehot' or 'label'")
    
    return df_encoded

def normalize_columns(df, columns=None, method="standard"):
    """
    Normalize or standardize numerical columns.
    method: "standard" (z-score) or "minmax" (0-1 scaling)
    columns: list of numeric columns to normalize. If None, normalize all numeric columns.
    """
    if columns is None:
        columns = df.select_dtypes(include=np.number).columns.tolist()
    
    df_norm = df.copy()
    
    if method == "standard":
        scaler = StandardScaler()
    elif method == "minmax":
        scaler = MinMaxScaler()
    else:
        raise ValueError("method must be 'standard' or 'minmax'")
    
    df_norm[columns] = scaler.fit_transform(df_norm[columns])
    return df_norm
