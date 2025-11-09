import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

def generate_plot(df):
    st.subheader("📈 Create a Visualization")

    # Column selection
    cols = df.columns.tolist()
    x_col = st.selectbox("Select X-axis", cols)
    y_col = st.selectbox("Select Y-axis (optional)", ["None"] + cols)
    plot_type = st.selectbox("Select plot type", ["Histogram", "Scatter", "Boxplot", "Line", "Bar"])

    if st.button("Generate Plot"):
        plt.figure(figsize=(8, 5))

        if plot_type == "Histogram":
            sns.histplot(df[x_col], kde=True)
        elif plot_type == "Scatter" and y_col != "None":
            sns.scatterplot(x=df[x_col], y=df[y_col])
        elif plot_type == "Boxplot" and y_col != "None":
            sns.boxplot(x=df[x_col], y=df[y_col])
        elif plot_type == "Line" and y_col != "None":
            sns.lineplot(x=df[x_col], y=df[y_col])
        elif plot_type == "Bar" and y_col != "None":
            sns.barplot(x=df[x_col], y=df[y_col])

        plt.title(f"{plot_type} of {x_col}" + (f" vs {y_col}" if y_col != "None" else ""))
        st.pyplot(plt)
        st.success("✅ Visualization generated successfully!")