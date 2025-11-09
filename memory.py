import streamlit as st
import io
import pandas as pd

# --- Chat Memory ---
def initialize_memory():
    """Initialize chat memory"""
    if "history" not in st.session_state:
        st.session_state["history"] = []

def add_message(sender, message):
    """Add a new message to memory"""
    st.session_state["history"].append({"sender": sender, "message": message})

def get_history():
    """Retrieve chat history"""
    return st.session_state.get("history", [])

# --- Dataset Summary Memory ---
def save_summary_to_memory(df, name="latest_summary"):
    """
    Store a summary (like describe()) in session memory
    """
    st.session_state[name] = df.describe()

def get_saved_summary(name="latest_summary"):
    """
    Retrieve a saved summary from memory
    """
    return st.session_state.get(name, None)

# --- Export Functions ---
def export_dataframe(df, file_type="csv"):
    """
    Export dataframe to CSV or Excel
    """
    buffer = io.BytesIO()
    if file_type == "csv":
        df.to_csv(buffer, index=False)
        st.download_button(
            label="📥 Download CSV",
            data=buffer.getvalue(),
            file_name="exported_data.csv",
            mime="text/csv"
        )
    elif file_type == "excel":
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        st.download_button(
            label="📊 Download Excel",
            data=buffer.getvalue(),
            file_name="exported_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )