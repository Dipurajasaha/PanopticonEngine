import os
import streamlit as st 
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Panopticon Dashboard", layout="wide")

token = st.session_state.get("token")
is_authenticated = bool(token)

# -- Sidebar: Authentication & Registration --
if not is_authenticated:
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Log In"):
        normalized_email = email.strip().lower()
        normalized_password = password.strip()

        if not normalized_email or not normalized_password:
            st.sidebar.error("Email and password are required.")
            st.stop()

        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json={"email": normalized_email, "password": normalized_password},
                timeout=10,
            )

            if response.status_code == 200 and response.json().get("access_token"):
                st.session_state.token = response.json().get("access_token")
                st.sidebar.success("Authentication Successful...")
                st.rerun()
            else:
                backend_message = ""
                try:
                    backend_message = response.json().get("detail", "")
                except ValueError:
                    backend_message = ""

                if response.status_code == 401:
                    st.sidebar.error(backend_message or "Invalid email or password.")
                else:
                    st.sidebar.error(
                        f"Login failed (status {response.status_code}). {backend_message}".strip()
                    )
        except requests.RequestException:
            st.sidebar.error("Unable to reach backend API during login.")

    with st.sidebar.expander("Create Account"):
        new_email = st.text_input("New Email", key="register_email")
        new_password = st.text_input("New Password", type="password", key="register_password")
        new_role = st.selectbox("Role", options=["Viewer", "Analyst", "Admin"], key="register_role")

        if st.button("Register"):
            register_email = new_email.strip().lower()
            register_password = new_password.strip()

            if not register_email or not register_password:
                st.error("New email and password are required.")
            else:
                try:
                    register_response = requests.post(
                        f"{API_URL}/users/",
                        json={
                            "email": register_email,
                            "password": register_password,
                            "role": new_role,
                        },
                        timeout=10,
                    )

                    if register_response.status_code in (200, 201):
                        st.success("Account created. You can now log in.")
                    else:
                        register_message = ""
                        try:
                            register_message = register_response.json().get("detail", "")
                        except ValueError:
                            register_message = ""
                        st.error(
                            f"Registration failed (status {register_response.status_code}). {register_message}".strip()
                        )
                except requests.RequestException:
                    st.error("Unable to reach backend API during registration.")

else:
    st.sidebar.success("System Online: You are securely connected")
    if st.sidebar.button("Log Out"):
        st.session_state.pop("token", None)
        st.rerun()


# -- Main Page: Analytics Dashboard -- 
if is_authenticated:
    st.title("Finance Intelligence Dashboard")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{API_URL}/analytics/summary", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # -- 1. top level metrics --
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Total Income", value=f"${data['total_income']:,.2f}")
            col2.metric(label="Total Expense", value=f"${data['total_expense']:,.2f}")

            # color the net balance green if positive else red for negative
            balance_delta = "Positive" if data['net_balance'] >= 0 else "Negative"
            col3.metric(label="Net Balance", value=f"${data['net_balance']:,.2f}", delta=balance_delta) 

            st.divider()

            # -- 2. expense distribution by category --
            st.subheader("Expense Distribution by Category")

            if data["category_breakdown"]:
                df = pd.DataFrame(data["category_breakdown"])
                df.set_index("category", inplace=True)
                st.bar_chart(df)

            else:
                st.info("No expense data available to display the distribution.")

        elif response.status_code == 403:
            st.error("Access Denied: Your current role does not have permission to view this dashboard.")
            
        # -- 3. graceful logout fix (401 expired token) --
        elif response.status_code == 401:
            st.warning("⏱️ Your secure session has expired... Please log in again...")
            st.session_state.pop("token", None) 
            if st.button("Return to Login Screen"):
                st.rerun()

        else:
            st.error(f"Failed to connect to backend API, status code: {response.status_code}")
            
    except requests.Timeout:
        st.error("Backend API timed out while loading analytics data.")
    except requests.RequestException:
        st.error("Failed to connect to backend API.")

else:
    st.title("Panopticon Engine")
    st.info("Awaiting Authentication... Please log in using the secure gateway on the left...")