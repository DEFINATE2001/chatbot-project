import streamlit as st

def login_page():
    st.title("🔐 Welcome to Data Mentor Chatbot")

    # Store login state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("Sign In")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Simple demo authentication
            if username and password:
                st.session_state.username = username
                st.session_state.logged_in = True
                st.success(f"✅ Welcome {username}! Redirecting to chatbot...")
                st.session_state.page = "chat"
                st.rerun()
            else:
                st.error("Please enter both username and password.")
    else:
        st.success(f"Welcome back, {st.session_state.username}!")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()
