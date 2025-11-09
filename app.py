import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime
import re
import os

from nlu import detect_intent
from analysis import summarize_data, correlation_matrix, simple_regression, detect_outliers
from visualize import generate_plot
from memory import initialize_memory, add_message, get_history
from explain import explain_correlation, explain_regression
from reports import export_pdf_report

# =====================================
# 🔐 USER AUTHENTICATION FUNCTIONS
# =====================================
USER_FILE = "users.csv"

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    else:
        return pd.DataFrame(columns=["username", "password", "fullname", "email"])

def save_user(username, password, fullname, email):
    users = load_users()
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame([[username, password, fullname, email]],
                            columns=["username", "password", "fullname", "email"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_FILE, index=False)
    return True

def authenticate_user(username, password):
    users = load_users()
    match = users[(users["username"] == username) & (users["password"] == password)]
    if not match.empty:
        return match.iloc[0]
    else:
        return None

# =====================================
# 🧭 AUTH PAGES (LOGIN / REGISTER)
# =====================================
def login_page():
    st.title("🔐 Welcome to Data Mentor Chatbot")
    st.subheader("Sign In to Continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(username, password)
        if user is not None:
            st.session_state["logged_in"] = True
            st.session_state["username"] = user["username"]
            st.session_state["fullname"] = user["fullname"]
            st.success(f"✅ Welcome back, {user['fullname']}!")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

    st.info("Don't have an account?")
    if st.button("Register Here"):
        st.session_state["show_register"] = True
        st.rerun()

def register_page():
    st.title("📝 Create a New Account")

    fullname = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if not all([fullname, email, username, password, confirm]):
            st.warning("Please fill in all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            success = save_user(username, password, fullname, email)
            if success:
                st.success("🎉 Account created successfully! You can now log in.")
                st.session_state["show_register"] = False
                st.rerun()
            else:
                st.error("⚠️ Username already exists. Try another one.")

    if st.button("Back to Login"):
        st.session_state["show_register"] = False
        st.rerun()

# =====================================
# 💬 MAIN CHATBOT PAGE
# =====================================
def chatbot_page():
    st.set_page_config(page_title="Data Analysis Chatbot", layout="wide")
    st.title(f"🤖 Data Analysis Chatbot — Welcome, {st.session_state['fullname']}!")
    st.write("Upload your dataset and chat with your AI assistant about analysis, visualization, and statistics.")
    initialize_memory()

    st.sidebar.header(f"👋 Hello, {st.session_state['fullname']}")
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.clear()
        st.rerun()

    # === Sidebar Controls ===
    st.sidebar.header("⚙️ Control Panel")
    if st.sidebar.button("🧹 Clear Chat History"):
        st.session_state["history"] = []
        st.success("Chat history cleared!")

    st.sidebar.header("🧠 Memory & Export")
    if "data" in st.session_state:
        df = st.session_state["data"]
        if st.sidebar.button("💾 Save Summary to Memory"):
            from memory import save_summary_to_memory
            save_summary_to_memory(df)
            st.sidebar.success("Summary saved to memory ✅")
        if st.sidebar.button("📂 Recall Summary"):
            from memory import get_saved_summary
            saved = get_saved_summary()
            if saved:
                st.sidebar.write(saved)
            else:
                st.sidebar.warning("No saved summary found.")
    else:
        st.sidebar.warning("Upload a dataset to enable export options.")

    st.sidebar.subheader("📊 Dataset Info")
    if "data" in st.session_state:
        data = st.session_state["data"]
        st.sidebar.write(f"**Rows:** {data.shape[0]}")
        st.sidebar.write(f"**Columns:** {data.shape[1]}")
        st.sidebar.write(f"**Columns:** {', '.join(list(data.columns[:5]))} ...")

    st.sidebar.write("---")
    st.sidebar.caption("💡 Try asking me:")
    st.sidebar.markdown("""
    - "Show summary statistics"
    - "Plot a histogram of Salary"
    - "Find correlation between Age and Income"
    - "Run regression between Experience and Salary"
    - "Select columns Name, Salary"
    - "Filter where Age > 30"
    - "Detect outliers"
    - "Create column BMI = Weight / Height ** 2"
    - "Normalize Age"
    - "One-hot encode Gender"
    """)

    # === Dataset Upload ===
    uploaded_file = st.file_uploader("📂 Upload CSV or Excel", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state["data"] = df
        st.success("✅ Dataset uploaded successfully!")
    else:
        st.info("👋 Please upload a dataset to start chatting.")

    # === Chat Interface ===
    user_input = st.text_input("💬 Ask me anything (e.g., 'Filter where Age > 30')")
    if user_input:
        add_message("user", user_input)
        intent = detect_intent(user_input)

        if "data" not in st.session_state:
            add_message("bot", "Please upload a dataset first 📂.")
        else:
            df = st.session_state["data"]

            try:
                # --- ANALYZE ---
                if intent == "analyze":
                    result = summarize_data(df)
                    add_message("bot", "Here’s your dataset summary 📊:")
                    st.write(result)

                # --- VISUALIZE ---
                elif intent == "visualize":
                    add_message("bot", "Let's make a chart together 📈")
                    generate_plot(df)

                # --- SHOW DATASET ---
                elif intent == "show_data":
                    add_message("bot", "Here’s your dataset preview 🧾:")
                    st.write(df.head())

                # --- CORRELATION ---
                elif intent == "correlation":
                    corr = correlation_matrix(df)
                    add_message("bot", "Here’s your correlation matrix 📘:")
                    st.write(corr)
                    explanation = explain_correlation(corr, user_input)
                    add_message("bot", explanation)
                    st.write(explanation)

                # --- REGRESSION ---
                elif intent == "regression":
                    st.write("Select columns for regression:")
                    cols = df.columns.tolist()
                    x_col = st.selectbox("Independent (X)", cols)
                    y_col = st.selectbox("Dependent (Y)", cols)
                    if st.button("Run Regression"):
                        model_info = simple_regression(df, x_col, y_col)
                        add_message("bot", f"Regression Result:\n{model_info}")
                        explanation = explain_regression(model_info, user_input)
                        add_message("bot", explanation)
                        st.json(model_info)
                        st.write(explanation)

                # --- CLEANING ---
                elif intent == "clean":
                    missing = df.isna().sum()
                    add_message("bot", "Here’s a summary of missing values 🧹:")
                    st.write(missing)

                # --- DATA TYPES ---
                elif intent == "dtypes":
                    add_message("bot", "Here are the data types for each column 📘:")
                    st.write(df.dtypes)

                # --- COLUMN SELECTION ---
                elif intent == "select_columns":
                    add_message("bot", "Sure! Which columns would you like to see? 🧮")
                    cols = re.findall(r'\b[A-Za-z_]+\b', user_input)
                    cols = [c for c in cols if c.lower() not in ["select", "show", "columns", "column", "display"]]
                    if cols:
                        valid = [c for c in cols if c in df.columns]
                        if valid:
                            st.write(df[valid].head())
                            add_message("bot", f"Here are your selected columns: {', '.join(valid)} ✅")
                        else:
                            add_message("bot", "I couldn’t find those columns. Please check their names.")
                    else:
                        add_message("bot", "Please mention the column names you want to select.")

                # --- FILTERING ---
                elif intent == "filter":
                    add_message("bot", "Let's filter your data 🔍")
                    match = re.search(r"(\b\w+\b)\s*(=|>|<|>=|<=)\s*([\w\s]+)", user_input)
                    if match:
                        col, op, val = match.groups()
                        col, val = col.strip(), val.strip()

                        if col not in df.columns:
                            add_message("bot", f"Column '{col}' not found.")
                        else:
                            try:
                                if op == "=":
                                    filtered = df[df[col].astype(str) == val]
                                elif op == ">":
                                    filtered = df[df[col] > float(val)]
                                elif op == "<":
                                    filtered = df[df[col] < float(val)]
                                elif op == ">=":
                                    filtered = df[df[col] >= float(val)]
                                elif op == "<=":
                                    filtered = df[df[col] <= float(val)]
                                else:
                                    filtered = df

                                st.write(filtered.head())
                                add_message("bot", f"Here are rows where `{col} {op} {val}` ✅")

                                # --- Sanitize filename for Windows ---
                                def sanitize_filename(name):
                                    return re.sub(r'[<>:"/\\|?*]', '_', name)

                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                safe_label = sanitize_filename(f"{col}_{op}_{val}")
                                download_filename = f"Filtered_{safe_label}_{timestamp}.csv"

                                # --- Download button ---
                                csv_data = filtered.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download Filtered Data",
                                    data=csv_data,
                                    file_name=download_filename,
                                    mime='text/csv'
                                )
                            except Exception as e:
                                add_message("bot", f"⚠️ Could not filter: {e}")
                    else:
                        add_message("bot", "Use a format like 'Filter where Age > 30'.")

                # --- OUTLIER DETECTION ---
                elif intent == "outlier":
                    add_message("bot", "Detecting outliers in your dataset 🕵️‍♂️")
                    outlier_df = detect_outliers(df)
                    st.write(outlier_df)
                    add_message("bot", "Outliers detected ✅")

                # --- DATA TRANSFORMATION / FEATURE ENGINEERING ---
                elif intent == "transform":
                    add_message("bot", "Let's perform data transformation ⚙️")

                    # 1. Create new column
                    match_create = re.search(r"create column (\w+)\s*=\s*(.+)", user_input, re.IGNORECASE)
                    if match_create:
                        new_col, formula = match_create.groups()
                        try:
                            for col_name in df.columns:
                                formula = re.sub(rf"\b{col_name}\b", f'df["{col_name}"]', formula)
                            df[new_col] = eval(formula)
                            st.write(df.head())
                            add_message("bot", f"✅ Column '{new_col}' created successfully!")
                        except Exception as e:
                            add_message("bot", f"⚠️ Could not create column: {e}")

                    # 2. Encode categorical variables
                    elif "encode" in user_input.lower():
                        match_encode = re.search(r"(one[-\s]?hot|label) encode (\w+)", user_input, re.IGNORECASE)
                        if match_encode:
                            method, col = match_encode.groups()
                            if col not in df.columns:
                                add_message("bot", f"Column '{col}' not found.")
                            else:
                                try:
                                    if "one" in method.lower():
                                        df = pd.get_dummies(df, columns=[col])
                                        st.write(df.head())
                                        add_message("bot", f"✅ Column '{col}' one-hot encoded.")
                                    else:
                                        from sklearn.preprocessing import LabelEncoder
                                        le = LabelEncoder()
                                        df[col] = le.fit_transform(df[col])
                                        st.write(df.head())
                                        add_message("bot", f"✅ Column '{col}' label encoded.")
                                except Exception as e:
                                    add_message("bot", f"⚠️ Could not encode column: {e}")

                    # 3. Normalize / Standardize
                    elif any(word in user_input.lower() for word in ["normalize", "standardize"]):
                        match_norm = re.search(r"(normalize|standardize) (\w+)", user_input, re.IGNORECASE)
                        if match_norm:
                            method, col = match_norm.groups()
                            if col not in df.columns:
                                add_message("bot", f"Column '{col}' not found.")
                            else:
                                try:
                                    from sklearn.preprocessing import MinMaxScaler, StandardScaler
                                    if method.lower() == "normalize":
                                        scaler = MinMaxScaler()
                                    else:
                                        scaler = StandardScaler()
                                    df[[col]] = scaler.fit_transform(df[[col]])
                                    st.write(df.head())
                                    add_message("bot", f"✅ Column '{col}' {method.lower()}d successfully.")
                                except Exception as e:
                                    add_message("bot", f"⚠️ Could not {method} column: {e}")

                    else:
                        add_message("bot", "Please specify a valid transformation, e.g., create, encode, normalize, or standardize.")

                # --- HELP ---
                elif intent == "help":
                    add_message("bot", "I can help you with these tasks 🧠:")
                    st.markdown("""
                        - **Analyze**: summary stats
                        - **Visualize**: plots and charts
                        - **Correlate**: relationships
                        - **Regression**: trends and prediction
                        - **Select Columns**: show specific variables
                        - **Filter**: filter rows by condition
                        - **Outliers**: detect anomalies
                        - **Transform**: create new columns, encode, normalize, standardize
                    """)

                # --- UNKNOWN ---
                else:
                    add_message("bot", "Sorry, I didn’t quite get that 🤔.")

            except Exception as e:
                add_message("bot", f"⚠️ Error: {e}")

    # === Chat History ===
    st.write("---")
    st.markdown("<h3>💭 Conversation History</h3>", unsafe_allow_html=True)
    for msg in get_history():
        if msg["sender"] == "user":
            st.markdown(f"<div style='background:#DCF8C6;padding:8px;border-radius:10px;margin:4px 0;text-align:right;'><b>You:</b> {msg['message']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#E9E9EB;padding:8px;border-radius:10px;margin:4px 0;text-align:left;'><b>Bot:</b> {msg['message']}</div>", unsafe_allow_html=True)

# =====================================
# 🚀 MAIN APP ENTRY
# =====================================
def main():
    if "show_register" not in st.session_state:
        st.session_state["show_register"] = False

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        if st.session_state["show_register"]:
            register_page()
        else:
            login_page()
    else:
        chatbot_page()

if __name__ == "__main__":
    main()
