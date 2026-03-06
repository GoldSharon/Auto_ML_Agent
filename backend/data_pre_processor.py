import re

def canonicalize_columns(df):
    """
    Canonicalize column names and clean categorical values.
    Removes special characters that cause issues with XGBoost.
    
    Args:
        df: Input DataFrame
        
    Returns:
        tuple: (cleaned DataFrame, column mapping dict)
    """
    mapping = {}
    new_cols = []

    # Clean column names
    for col in df.columns:
        clean = col.lower().strip()
        clean = re.sub(r"\s+", "_", clean)
        clean = re.sub(r"[^a-z0-9_]", "", clean)

        mapping[col] = clean
        new_cols.append(clean)

    df.columns = new_cols
    
    # Clean categorical values to prevent one-hot encoding issues
    for col in df.select_dtypes(include=['object', 'category']).columns:
        df[col] = df[col].astype(str).apply(
            lambda x: re.sub(r"[^a-z0-9_]", "_", x.lower().strip())
        )
    
    return df, mapping