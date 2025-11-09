import re

def explain_correlation(corr_df, user_input=""):
    """
    Generate a correlation explanation.
    - Detailed mode: if user asks for 'explain' or 'details'
    - Summary mode: otherwise (highlights only strong correlations)
    """

    # Detect if the user wants a detailed explanation
    detailed = bool(re.search(r"\b(explain|detail|describe)\b", user_input.lower()))

    if detailed:
        # --- Detailed Mode ---
        text = "📘 Here's what the correlations mean:\n"
        for col1 in corr_df.columns:
            for col2 in corr_df.columns:
                if col1 != col2:
                    value = corr_df.loc[col1, col2]
                    if abs(value) > 0.7:
                        level = "strong"
                    elif abs(value) > 0.4:
                        level = "moderate"
                    else:
                        level = "weak"
                    direction = "positive" if value > 0 else "negative"
                    text += f"- {col1} and {col2} have a {level} {direction} relationship ({value:.2f}).\n"
        return text
    else:
        # --- Summary Mode ---
        strong_corrs = []
        for col1 in corr_df.columns:
            for col2 in corr_df.columns:
                value = corr_df.loc[col1, col2]
                if abs(value) > 0.7 and col1 != col2:
                    strong_corrs.append(f"{col1} and {col2} (r = {value:.2f})")

        if strong_corrs:
            return "🔍 Strong correlations detected:\n- " + "\n- ".join(strong_corrs)
        else:
            return "No strong correlations detected (|r| < 0.7)."


def explain_regression(model_info, user_input=""):
    """
    Explain regression results (detailed or brief depending on user input)
    """
    coef = model_info["coefficient"]
    r2 = model_info["r_squared"]

    direction = "increases" if coef > 0 else "decreases"
    strength = "strong" if r2 > 0.7 else "moderate" if r2 > 0.4 else "weak"

    detailed = bool(re.search(r"\b(explain|detail|describe)\b", user_input.lower()))

    if detailed:
        explanation = (
            f"📊 Regression Analysis Details:\n"
            f"- The dependent variable **{direction}** as the independent variable increases.\n"
            f"- The model fit (R² = {r2:.2f}) indicates a **{strength}** relationship.\n"
            f"- Coefficient value: {coef:.3f}\n"
            f"This means that for each unit increase in the independent variable, "
            f"the dependent variable changes by approximately {coef:.3f} units."
        )
    else:
        explanation = (
            f"The dependent variable {direction} as the independent variable increases. "
            f"The relationship is {strength} (R² = {r2:.2f})."
        )
    return explanation