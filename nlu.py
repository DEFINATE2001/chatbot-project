import re

def detect_intent(user_input):
    text = user_input.lower().strip()

    # --- 1. ANALYSIS ---
    if re.search(r"\b(summary|describe|overview|analy(s|z)e|statistics?|info|give me summary|dataset info)\b", text):
        return "analyze"

    # --- 2. VISUALIZATION ---
    elif re.search(r"\b(plot|chart|graph|visual|scatter|bar|histogram|boxplot|line|trend)\b", text):
        return "visualize"

    # --- 3. CORRELATION ---
    elif re.search(r"\b(correlation|relationship|association|relate|connection)\b", text):
        return "correlation"

    # --- 4. REGRESSION ---
    elif re.search(r"\b(regression|predict|trend|model|linear|forecast)\b", text):
        return "regression"

    # --- 5. CLEANING ---
    elif re.search(r"\b(clean|missing|null|na|empty|remove|impute|fill)\b", text):
        return "clean"

    # --- 6. DATA TYPES ---
    elif re.search(r"\b(data[\s\-]?types?|dtypes?|column\s+types?|variable\s+types?)\b", text):
        return "dtypes"

    # --- 7. COLUMN SELECTION ---
    elif re.search(r"\b(select|show|display|view|see)\b.*\b(columns?|variables?)\b", text):
        return "select_columns"

    # --- 8. FILTERING ---
    elif re.search(r"\b(filter|where|only|rows?|records?|subset)\b", text):
        return "filter"

    # --- 9. SHOW DATASET ---
    elif re.search(r"\b(show|display|view|see|print)\b.*\b(data|dataset|table|records?)\b", text):
        return "show_data"

    # --- 10. EXPLANATION ---
    elif re.search(r"\b(explain|interpret|meaning|why)\b", text):
        return "explain"

    # --- 11. HELP ---
    elif re.search(r"\b(help|what can you do|options|commands)\b", text):
        return "help"

    # --- 12. OUTLIER DETECTION ---
    elif re.search(r"\b(outlier|anomaly|detect outliers?)\b", text):
        return "outlier"

    # --- 13. DATA TRANSFORMATION / FEATURE ENGINEERING ---
    elif re.search(r"\b(create|add|new column|encode|normalize|standardize|transform|feature)\b", text):
        return "transform"

    # --- 14. MERGE / JOIN DATASETS ---
    elif re.search(r"\b(merge|join|combine|append)\b", text):
        return "merge"
    
    # --- 15. GREETING ---
    elif re.search(r"\b(hi|hello|hey|good\s?(morning|afternoon|evening)|how are you|whats up|sup)\b", text):
        return "greeting"


    # --- 16. Fallback ---
    else:
        return "unknown"