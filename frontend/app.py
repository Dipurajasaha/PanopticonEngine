import os
import json
import base64
from datetime import datetime, time

import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Panopticon Engine", page_icon="📊", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {padding-top: 1.5rem;}
            .hero {
                padding: 1.1rem 1.4rem;
                border-radius: 14px;
                background: linear-gradient(135deg, #0f172a 0%, #1f2937 55%, #334155 100%);
                color: #f8fafc;
                border: 1px solid #334155;
                margin-bottom: 1rem;
            }
            .hero h2 {margin: 0;}
            .hero p {margin: 0.35rem 0 0 0; color: #e2e8f0;}
            .card {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 0.85rem 1rem;
                background: #ffffff;
            }
            .muted {color: #64748b; font-size: 0.92rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def decode_token_payload(token: str) -> dict:
    try:
        token_parts = token.split(".")
        if len(token_parts) < 2:
            return {}
        payload_part = token_parts[1]
        payload_part += "=" * (-len(payload_part) % 4)
        decoded = base64.urlsafe_b64decode(payload_part.encode("utf-8"))
        return json.loads(decoded.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return {}


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def init_state() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("user_email", None)


def clear_login_state() -> None:
    st.session_state.pop("token", None)
    st.session_state.pop("user_email", None)


def api_error_message(resp: requests.Response) -> str:
    try:
        return resp.json().get("detail", "")
    except ValueError:
        return ""


@st.cache_data(ttl=30)
def fetch_dashboard_summary(api_url: str, token: str):
    return requests.get(f"{api_url}/analytics/summary", headers=auth_headers(token), timeout=12)


@st.cache_data(ttl=20)
def fetch_records(
    api_url: str,
    token: str,
    record_type: str,
    category: str,
    start_iso: str,
    end_iso: str,
    limit: int,
):
    params = {"skip": 0, "limit": limit}
    if record_type != "All":
        params["record_type"] = record_type
    if category != "All":
        params["category"] = category
    if start_iso:
        params["start_date"] = start_iso
    if end_iso:
        params["end_date"] = end_iso

    return requests.get(
        f"{api_url}/records/",
        headers=auth_headers(token),
        params=params,
        timeout=15,
    )


def create_record(api_url: str, token: str, payload: dict):
    return requests.post(
        f"{api_url}/records/",
        headers=auth_headers(token),
        json=payload,
        timeout=12,
    )


def delete_record(api_url: str, token: str, record_id: int):
    return requests.delete(
        f"{api_url}/records/{record_id}",
        headers=auth_headers(token),
        timeout=12,
    )


def get_users(api_url: str, token: str):
    return requests.get(f"{api_url}/users/", headers=auth_headers(token), timeout=12)


def register_user(api_url: str, email: str, password: str, role: str = "Viewer"):
    return requests.post(
        f"{api_url}/users/",
        json={"email": email, "password": password, "role": role},
        timeout=12,
    )


def admin_create_user(api_url: str, token: str, email: str, password: str, role: str):
    return requests.post(
        f"{api_url}/users/admin",
        headers=auth_headers(token),
        json={"email": email, "password": password, "role": role},
        timeout=12,
    )


def admin_update_user_role(api_url: str, token: str, user_id: int, role: str):
    return requests.patch(
        f"{api_url}/users/{user_id}/role",
        headers=auth_headers(token),
        json={"role": role},
        timeout=12,
    )


def admin_delete_user(api_url: str, token: str, user_id: int):
    return requests.delete(
        f"{api_url}/users/{user_id}",
        headers=auth_headers(token),
        timeout=12,
    )


def normalize_role(role: str) -> str:
    return str(role).strip().lower()


def display_role(role: str) -> str:
    role_map = {
        "viewer": "Viewer",
        "analyst": "Analyst",
        "admin": "Admin",
    }
    return role_map.get(normalize_role(role), "Viewer")


def role_navigation(role: str):
    normalized_role = normalize_role(role)
    options = ["Executive Dashboard"]
    if normalized_role in ["analyst", "admin"]:
        options.append("Finance Explorer")
        options.append("Record Operations")
    if normalized_role == "admin":
        options.append("User Management")
    return options


def records_to_df(items: list[dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=["id", "amount", "record_type", "category", "description", "created_at"])
    df = pd.DataFrame(items)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.sort_values("created_at", ascending=False)
    return df


def render_hero(user_id: str, username: str, email_id: str, role: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h2>Panopticon Engine Intelligence Console</h2>
            <p>User ID: <strong>{user_id}</strong> · Username: <strong>{username}</strong> · Email ID: <strong>{email_id}</strong> · Role: <strong>{role}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_exec_dashboard(token: str) -> None:
    st.subheader("Executive Dashboard")
    st.caption("High-level financial intelligence from the analytics engine.")

    try:
        response = fetch_dashboard_summary(API_URL, token)
    except requests.RequestException:
        st.error("Could not connect to backend while loading dashboard summary.")
        return

    if response.status_code == 401:
        st.warning("Session expired. Please log in again.")
        clear_login_state()
        st.rerun()
        return
    if response.status_code != 200:
        st.error(f"Dashboard request failed ({response.status_code}). {api_error_message(response)}")
        return

    data = response.json()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Income", f"${data.get('total_income', 0):,.2f}")
    c2.metric("Total Expense", f"${data.get('total_expense', 0):,.2f}")

    net = float(data.get("net_balance", 0))
    c3.metric("Net Balance", f"${net:,.2f}", delta="Positive" if net >= 0 else "Negative")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Expense Distribution by Category")
    breakdown = data.get("category_breakdown", [])
    if breakdown:
        cat_df = pd.DataFrame(breakdown).rename(columns={"total_amount": "total"})
        cat_df = cat_df.sort_values("total", ascending=False).set_index("category")
        st.bar_chart(cat_df)
    else:
        st.info("No expense breakdown data available yet.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_finance_explorer(token: str, role: str) -> None:
    st.subheader("Finance Explorer")
    st.caption("Query records with filters, explore trends, and export analysis-ready data.")

    with st.sidebar:
        st.markdown("### Filters")
        record_type = st.selectbox("Record Type", ["All", "Income", "Expense"], index=0)
        category = st.text_input("Category (exact)", value="All")
        if not category.strip():
            category = "All"
        date_range = st.date_input("Date Range", value=())
        max_rows = st.slider("Max Rows", min_value=50, max_value=1000, value=300, step=50)

    start_iso = ""
    end_iso = ""
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_dt = datetime.combine(date_range[0], time.min)
        end_dt = datetime.combine(date_range[1], time.max)
        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()

    try:
        response = fetch_records(API_URL, token, record_type, category, start_iso, end_iso, max_rows)
    except requests.RequestException:
        st.error("Could not connect to backend while loading records.")
        return

    if response.status_code == 401:
        st.warning("Session expired. Please log in again.")
        clear_login_state()
        st.rerun()
        return
    if response.status_code == 403:
        st.error("Your role cannot access finance records.")
        return
    if response.status_code != 200:
        st.error(f"Record query failed ({response.status_code}). {api_error_message(response)}")
        return

    df = records_to_df(response.json())
    if df.empty:
        st.info("No records match the selected filters.")
        return

    income = float(df[df["record_type"].str.lower() == "income"]["amount"].sum())
    expense = float(df[df["record_type"].str.lower() == "expense"]["amount"].sum())
    net = income - expense

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{len(df):,}")
    m2.metric("Income", f"${income:,.2f}")
    m3.metric("Expense", f"${expense:,.2f}")
    m4.metric("Net", f"${net:,.2f}", delta="Positive" if net >= 0 else "Negative")

    tab1, tab2, tab3 = st.tabs(["Trend", "Category", "Data Table"])

    with tab1:
        trend = df.copy()
        trend["day"] = trend["created_at"].dt.date
        trend = trend.groupby(["day", "record_type"], as_index=False)["amount"].sum()
        if trend.empty:
            st.info("Not enough data for trend chart.")
        else:
            pivot = trend.pivot(index="day", columns="record_type", values="amount").fillna(0)
            st.line_chart(pivot)
            if len(pivot.index) >= 2:
                first = float(pivot.sum(axis=1).iloc[0])
                last = float(pivot.sum(axis=1).iloc[-1])
                if first != 0:
                    pct = ((last - first) / abs(first)) * 100
                    st.caption(f"Period movement: {pct:+.1f}% from first to latest point.")

    with tab2:
        expense_df = df[df["record_type"].str.lower() == "expense"]
        if expense_df.empty:
            st.info("No expense rows available for category distribution.")
        else:
            cat = expense_df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
            st.bar_chart(cat.set_index("category"))
            top = cat.iloc[0]
            st.caption(f"Top expense category: {top['category']} (${top['amount']:,.2f}).")

    with tab3:
        display_df = df[["id", "created_at", "record_type", "category", "amount", "description"]].copy()
        display_df["created_at"] = display_df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(display_df, width="stretch", hide_index=True)
        st.download_button(
            "Download CSV",
            data=display_df.to_csv(index=False).encode("utf-8"),
            file_name="panopticon_records.csv",
            mime="text/csv",
        )
        st.caption(
            "Access policy: Analyst/Admin can view and download the global dataset. "
            "Edit and delete remain owner-scoped."
        )


def render_record_operations(token: str, current_user_id: int) -> None:
    st.subheader("Record Operations")
    st.caption("Analyst and Admin: create and soft delete finance records.")

    left, right = st.columns(2)

    with left:
        st.markdown("### Create Record")
        with st.form("create_record_form"):
            amount = st.number_input("Amount", min_value=0.0, step=1.0)
            record_type = st.selectbox("Type", ["Income", "Expense"])
            category = st.text_input("Category")
            description = st.text_area("Description", height=90)
            submit = st.form_submit_button("Create")

            if submit:
                if not category.strip():
                    st.error("Category is required.")
                else:
                    payload = {
                        "amount": float(amount),
                        "record_type": record_type,
                        "category": category.strip(),
                        "description": description.strip() or None,
                    }
                    try:
                        resp = create_record(API_URL, token, payload)
                        if resp.status_code in (200, 201):
                            st.success("Record created.")
                            fetch_records.clear()
                            fetch_dashboard_summary.clear()
                        else:
                            st.error(f"Create failed ({resp.status_code}). {api_error_message(resp)}")
                    except requests.RequestException:
                        st.error("Could not reach backend while creating record.")

    with right:
        st.markdown("### Delete Record")
        try:
            resp = fetch_records(API_URL, token, "All", "All", "", "", 500)
            if resp.status_code == 200:
                rec_df = records_to_df(resp.json())
                user_records = rec_df[rec_df["owner_id"] == current_user_id]
                if user_records.empty:
                    st.info("No active records available.")
                else:
                    rec_options = user_records["id"].astype(int).tolist()
                    selected_id = st.selectbox("Record ID", rec_options)
                    selected = user_records[user_records["id"] == selected_id].iloc[0]
                    st.caption(
                        f"{selected['record_type']} · {selected['category']} · ${selected['amount']:,.2f}"
                    )
                    if st.button("Delete Record", type="primary"):
                        del_resp = delete_record(API_URL, token, int(selected_id))
                        if del_resp.status_code == 200:
                            st.success("Record deleted.")
                            fetch_records.clear()
                            fetch_dashboard_summary.clear()
                            st.rerun()
                        else:
                            st.error(
                                f"Delete failed ({del_resp.status_code}). {api_error_message(del_resp)}"
                            )
            else:
                st.error(f"Could not load records ({resp.status_code}). {api_error_message(resp)}")
        except requests.RequestException:
            st.error("Could not reach backend while loading records.")


def render_user_management(token: str) -> None:
    st.subheader("User Management")
    st.caption("Admin-only: create users, change roles, and delete users.")

    a, b = st.columns([1.25, 1.0])

    users_df = pd.DataFrame()

    with a:
        st.markdown("### Users")
        try:
            response = get_users(API_URL, token)
            if response.status_code == 200:
                users_df = pd.DataFrame(response.json())
                st.dataframe(users_df, width="stretch", hide_index=True)
            else:
                st.error(f"User list failed ({response.status_code}). {api_error_message(response)}")
        except requests.RequestException:
            st.error("Could not reach backend while loading users.")

    with b:
        st.markdown("### Create User")
        with st.form("admin_create_user"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["Viewer", "Analyst", "Admin"])
            submit = st.form_submit_button("Create User")

            if submit:
                if not email.strip() or not password.strip():
                    st.error("Email and password are required.")
                else:
                    try:
                        resp = admin_create_user(API_URL, token, email.strip().lower(), password.strip(), role)
                        if resp.status_code in (200, 201):
                            st.success("User created successfully.")
                            st.rerun()
                        else:
                            st.error(f"Create user failed ({resp.status_code}). {api_error_message(resp)}")
                    except requests.RequestException:
                        st.error("Could not reach backend while creating user.")

        st.markdown("### Change Role")
        if users_df.empty:
            st.info("Load users to manage roles.")
        else:
            role_options = users_df[["id", "email", "role"]].copy()
            selected_label = st.selectbox(
                "Select User",
                options=[f"{int(row.id)} | {row.email} | {row.role}" for row in role_options.itertuples(index=False)],
                key="role_change_target",
            )
            selected_user_id = int(selected_label.split("|")[0].strip())
            new_role = st.selectbox("New Role", ["Viewer", "Analyst", "Admin"], key="new_role_value")
            if st.button("Update Role", use_container_width=True):
                try:
                    resp = admin_update_user_role(API_URL, token, selected_user_id, new_role)
                    if resp.status_code == 200:
                        st.success("User role updated.")
                        st.rerun()
                    else:
                        st.error(f"Role update failed ({resp.status_code}). {api_error_message(resp)}")
                except requests.RequestException:
                    st.error("Could not reach backend while updating role.")

        st.markdown("### Delete User")
        if users_df.empty:
            st.info("Load users to delete accounts.")
        else:
            delete_label = st.selectbox(
                "Delete Target",
                options=[f"{int(row.id)} | {row.email}" for row in users_df[["id", "email"]].itertuples(index=False)],
                key="delete_user_target",
            )
            delete_user_id = int(delete_label.split("|")[0].strip())
            if st.button("Delete User", type="primary", use_container_width=True):
                try:
                    resp = admin_delete_user(API_URL, token, delete_user_id)
                    if resp.status_code == 200:
                        st.success("User deleted.")
                        st.rerun()
                    else:
                        st.error(f"Delete user failed ({resp.status_code}). {api_error_message(resp)}")
                except requests.RequestException:
                    st.error("Could not reach backend while deleting user.")


def render_login_panel() -> None:
    st.title("Panopticon Engine")
    st.info("Authenticate to access the intelligence console.")

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Log In", use_container_width=True):
        email = email.strip().lower()
        password = password.strip()
        if not email or not password:
            st.sidebar.error("Email and password are required.")
            return

        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json={"email": email, "password": password},
                timeout=12,
            )
        except requests.RequestException:
            st.sidebar.error("Unable to reach backend API during login.")
            return

        if response.status_code == 200 and response.json().get("access_token"):
            st.session_state.token = response.json().get("access_token")
            st.session_state.user_email = email
            st.sidebar.success("Authentication successful.")
            st.rerun()
            return

        st.sidebar.error(
            f"Login failed ({response.status_code}). {api_error_message(response) or 'Invalid credentials.'}"
        )

    with st.sidebar.expander("Create Account"):
        new_email = st.text_input("New Email", key="register_email")
        new_password = st.text_input("New Password", type="password", key="register_password")

        if st.button("Register", use_container_width=True):
            if not new_email.strip() or not new_password.strip():
                st.error("New email and password are required.")
            else:
                try:
                    register_response = register_user(
                        API_URL,
                        new_email.strip().lower(),
                        new_password.strip(),
                        
                    )
                    if register_response.status_code in (200, 201):
                        st.success("Account created. You can now log in.")
                    else:
                        st.error(
                            f"Registration failed ({register_response.status_code}). "
                            f"{api_error_message(register_response)}"
                        )
                except requests.RequestException:
                    st.error("Unable to reach backend API during registration.")



def main() -> None:
    inject_styles()
    init_state()

    token = st.session_state.get("token")
    if not token:
        render_login_panel()
        return

    payload = decode_token_payload(token)
    role = normalize_role(payload.get("role", "Viewer"))
    user_id = str(payload.get("sub", "N/A"))
    email_id = st.session_state.get("user_email") or "N/A"
    username = email_id.split("@", 1)[0] if "@" in email_id else email_id

    with st.sidebar:
        st.success("Secure session active")
        st.caption(f"Role: {display_role(role)}")
        if st.button("Log Out", use_container_width=True):
            clear_login_state()
            st.rerun()

    render_hero(user_id, username, email_id, display_role(role))

    pages = role_navigation(role)
    selected_page = st.sidebar.radio("Navigation", pages)

    if selected_page == "Executive Dashboard":
        render_exec_dashboard(token)
    elif selected_page == "Finance Explorer":
        render_finance_explorer(token, role)
    elif selected_page == "Record Operations":
        render_record_operations(token, int(user_id))
    elif selected_page == "User Management":
        render_user_management(token)


if __name__ == "__main__":
    main()