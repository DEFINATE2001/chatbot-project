import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
import os
import random
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from nlu import detect_intent
from analysis import summarize_data, correlation_matrix, simple_regression, detect_outliers
from visualize import generate_plot
from memory import initialize_memory, add_message, get_history
from explain import explain_correlation, explain_regression

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

    # --- SIDEBAR START ---
    st.sidebar.header(f"👋 Hello, {st.session_state['fullname']}")
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.clear()
        st.rerun()

    st.sidebar.header("⚙️ Control Panel")
    if st.sidebar.button("🧹 Clear Chat History"):
        st.session_state["history"] = []
        st.success("Chat history cleared!")

    # --- Memory & Export ---
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
            if saved is not None and not isinstance(saved, bool):
                st.sidebar.success("Summary recalled successfully ")
                st.sidebar.write(saved)
            else:
                st.sidebar.warning("⚠️ No saved summary found or it's empty.")

    # --- 📄 DOWNLOAD CHAT HISTORY AS PDF ---
    if st.sidebar.button("📄 Download Chat History as PDF"):
        if "history" in st.session_state and st.session_state["history"]:
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            pdf.setFont("Helvetica", 12)
            y = height - 50
            pdf.drawString(50, y, f"Chat History - Data Mentor Chatbot ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
            y -= 30

            for msg in st.session_state["history"]:
                sender = "You" if msg["sender"] == "user" else "Bot"
                text = f"{sender}: {msg['message']}"
                lines = []
                while len(text) > 90:
                    lines.append(text[:90])
                    text = text[90:]
                lines.append(text)

                for line in lines:
                    if y < 50:
                        pdf.showPage()
                        pdf.setFont("Helvetica", 12)
                        y = height - 50
                    pdf.drawString(50, y, line)
                    y -= 20

            pdf.save()
            buffer.seek(0)

            st.sidebar.download_button(
                label="⬇️ Save PDF",
                data=buffer,
                file_name=f"Chat_History_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        else:
            st.sidebar.warning("⚠️ No chat history to export yet.")

    # --- Dataset Info ---
    st.sidebar.subheader("📊 Dataset Info")
    if "data" in st.session_state:
        data = st.session_state["data"]
        st.sidebar.write(f"**Rows:** {data.shape[0]}")
        st.sidebar.write(f"**Columns:** {data.shape[1]}")
        st.sidebar.write(f"**Columns:** {', '.join(list(data.columns[:5]))} ...")
    else:
        st.sidebar.info("Upload a dataset to view its info.")

    st.sidebar.write("---")

    # --- Quick Tips ---
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
    - "Merge with another dataset"
    """)
    # --- SIDEBAR END ---

    # === Dataset Upload ===
    uploaded_file = st.file_uploader("📂 Upload your main dataset", type=["csv", "xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state["data"] = df
        st.success("✅ Dataset uploaded successfully!")
    else:
        st.info("👋 Please upload a dataset to start chatting.")

    # === Chat Input ===
    user_input = st.text_input("💬 Ask me anything (e.g., 'Filter where Age > 30')")
    if user_input:
        add_message("user", user_input)
        intent = detect_intent(user_input)

        if "data" not in st.session_state:
            add_message("bot", "Please upload a dataset first 📂.")
        else:
            df = st.session_state["data"]
            try:
                if intent == "analyze":
                    result = summarize_data(df)
                    add_message("bot", "Here’s your dataset summary 📊:")
                    st.write(result)

                elif intent == "visualize":
                    add_message("bot", "Let's make a chart together 📈")
                    generate_plot(df)

                elif intent == "show_data":
                    add_message("bot", "Here’s your dataset preview 🧾:")
                    st.write(df.head())

                elif intent == "correlation":
                    corr = correlation_matrix(df)
                    st.write(corr)
                    add_message("bot", "Here’s your correlation matrix 📘:")

                elif intent == "greeting":
                    greeting_responses = [
                        "👋 Hey there! I’m Data Mentor — your friendly data assistant.",
                        "😊 Hi! How’s your day going?",
                        "Hello there! Ready to explore your data together? 📊",
                        "Hey! I’m great — just waiting to dive into your dataset!",
                        "Good to see you again, Definate! Let’s get started 🚀"
                    ]
                    add_message("bot", random.choice(greeting_responses))

                elif intent == "regression":
                    cols = df.columns.tolist()
                    x_col = st.selectbox("Independent (X)", cols)
                    y_col = st.selectbox("Dependent (Y)", cols)
                    if st.button("Run Regression"):
                        model_info = simple_regression(df, x_col, y_col)
                        st.json(model_info)

                elif intent == "clean":
                    missing = df.isna().sum()
                    add_message("bot", "Here’s a summary of missing values 🧹:")
                    st.write(missing)

                elif intent == "dtypes":
                    st.write(df.dtypes)
                    add_message("bot", "Here are the data types for each column 📘:")

                elif intent == "select_columns":
                    cols = re.findall(r'\b[A-Za-z_]+\b', user_input)
                    cols = [c for c in cols if c in df.columns]
                    if cols:
                        st.write(df[cols].head())
                        add_message("bot", f"Here are your selected columns: {', '.join(cols)} ✅")

                elif intent == "filter":
                    match = re.search(r"(\b\w+\b)\s*(=|>|<|>=|<=)\s*([\w\s]+)", user_input)
                    if match:
                        col, op, val = match.groups()
                        if col in df.columns:
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
                                csv_data = filtered.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download Filtered Data",
                                    data=csv_data,
                                    file_name=f"Filtered_{col}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime='text/csv'
                                )
                            except Exception as e:
                                add_message("bot", f"⚠️ Could not filter: {e}")
                        else:
                            add_message("bot", f"Column '{col}' not found.")

                elif intent == "outlier":
                    outlier_df = detect_outliers(df)
                    st.write(outlier_df)
                    add_message("bot", "Outliers detected ✅")

                elif intent == "transform":
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

                elif intent == "help":
                    add_message("bot","Here are some things I can do:")
                    st.markdown("""
                    ### 🧭 Quick Commands
                    - `show dataset` — Preview your uploaded data  
                    - `summarize dataset` — Get a statistical overview  
                    - `visualize age vs salary` — Plot any two columns  
                    - `find correlation` — Check relationships  
                    - `run regression` — Build a simple predictive model  
                    - `clean missing values` — Handle nulls easily  
                    - `show data types` — See each column’s type  
                    - `filter where Age > 30` — Filter specific rows  
                    - `create column BMI = Weight / Height ** 2` — Add new features  
                    - `detect outliers` — Identify anomalies  
                    - `merge with another dataset` — Combine two datasets  
                    """)

                elif intent == "merge":
                    add_message("bot", "Let's merge two datasets 🔗")
                    st.subheader("📂 Upload second dataset to merge")
                    file2 = st.file_uploader("Upload second dataset", type=["csv", "xlsx"], key="merge_file")

                    if file2:
                        df2 = pd.read_csv(file2) if file2.name.endswith(".csv") else pd.read_excel(file2)
                        st.write("Preview of second dataset:")
                        st.write(df2.head())

                        join_col1 = st.selectbox("Select join column from first dataset", df.columns)
                        join_col2 = st.selectbox("Select join column from second dataset", df2.columns)
                        join_type = st.selectbox("Join type", ["inner", "left", "right", "outer"])
                        keep_separate = st.checkbox("Keep merged dataset separate", value=True)

                        if st.button("Merge Datasets"):
                            try:
                                merged_df = pd.merge(df, df2, left_on=join_col1, right_on=join_col2, how=join_type)
                                st.success(f"✅ Merged successfully with {join_type} join.")
                                st.write(merged_df.head())

                                if keep_separate:
                                    st.session_state["merged_data"] = merged_df
                                    st.info("📂 Merged dataset stored separately in memory.")
                                else:
                                    st.session_state["data"] = merged_df
                                    st.success("🔁 Merged dataset replaced the main dataset.")

                                csv_data = merged_df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download Merged Dataset",
                                    data=csv_data,
                                    file_name=f"Merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime='text/csv'
                                )
                            except Exception as e:
                                st.error(f"⚠️ Merge failed: {e}")

                else:
                    add_message("bot", "Sorry, I didn’t quite get that 🤔.")

            except Exception as e:
                add_message("bot", f"⚠️ Error: {e}")

    # === Conversation History ===
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
