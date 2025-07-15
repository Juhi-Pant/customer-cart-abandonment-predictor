import streamlit as st
import pandas as pd
import requests
import sqlite3
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🛒 Cart Abandonment Dashboard", layout="wide")

st.title("🧠 Customer Cart Abandonment Prediction & Insights")

tab1, tab2 = st.tabs(["🔮 Predict Abandonment", "📊 Session Analytics"])

# ------------------------- TAB 1: PREDICTION -------------------------
with tab1:
    st.header("📥 User Session Behavior")
    with st.form("predict_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            is_viewed = st.selectbox("Viewed Product Details?", ["Yes", "No"]) == "Yes"
            is_logged_in = st.selectbox("User Logged In?", ["Yes", "No"]) == "Yes"
        with col2:
            items_added = st.slider("No. of Items Added in Cart", 0, 10, 1)
            session_count = st.slider("Session Activity Count", 1, 20, 5)
        with col3:
            clicks = st.slider("Product Clicks", 0, 15, 3)
            time_spent = st.slider("Time Spent on Site (seconds)", 30, 600, 120)

        bounce_rate = st.slider("Bounce Rate (0-1)", 0.0, 1.0, 0.3)
        abandon_history = st.selectbox("User Abandoned Before?", ["Yes", "No"]) == "Yes"

        submitted = st.form_submit_button("🔍 Predict")

    if submitted:
        payload = {
            "Is_Product_Details_viewed": int(is_viewed),
            "No_Items_Added_InCart": items_added,
            "Session_Activity_Count": session_count,
            "No_of_Product_Clicks": clicks,
            "Bounce_Rate": bounce_rate,
            "Time_Spent_on_Site": time_spent,
            "Is_User_Logged_In": int(is_logged_in),
            "User_Prior_Abandonment_History": int(abandon_history),
            "user_id": f"user_{datetime.now().strftime('%H%M%S')}"
        }

        try:
            res = requests.post("http://127.0.0.1:5000/predict", json=payload)
            output = res.json()
            proba = output.get("abandonment_probability", 0.0)

            st.success(f"🧾 Abandonment Probability: **{proba * 100:.2f}%**")

            # Strategic Suggestion
            if proba > 0.7:
                st.error("⚠️ High risk of abandonment! Suggest: 🔔 pop-up coupon or ⚡ fast checkout UI.")
            elif proba > 0.5:
                st.warning("🟡 Moderate risk. Consider showing urgency or reminder notification.")
            else:
                st.success("✅ Low risk. User likely to complete the purchase.")

        except Exception as e:
            st.error(f"Error contacting prediction API: {str(e)}")


# ------------------------- TAB 2: ANALYTICS -------------------------
with tab2:
    st.header("📈 Analyze Logged Sessions")
    try:
        conn = sqlite3.connect("abandonment_logs.db")
        df = pd.read_sql("SELECT * FROM session_logs", conn)
        conn.close()

        if df.empty:
            st.info("No session logs found.")
        else:
            df['timestamp_logged'] = pd.to_datetime(df['timestamp_logged'])
            df['prediction'] = df['prediction'].astype(float)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Sessions", len(df))
            with col2:
                high_risk = df[df['prediction'] > 0.7]
                st.metric("High Risk Sessions", len(high_risk))

            # Line Chart of Abandonment Over Time
            df['date'] = df['timestamp_logged'].dt.date
            line = df.groupby('date')['prediction'].mean().reset_index()
            fig_line = px.line(line, x='date', y='prediction',
                               title="📉 Avg. Abandonment Risk Over Time")
            st.plotly_chart(fig_line, use_container_width=True)

            # Feature correlation bar
            st.subheader("🔍 Top Contributing Factors")
            corr_df = df.drop(columns=['id', 'user_id', 'timestamp_logged', 'date'])
            corrs = corr_df.corr()['prediction'].sort_values(ascending=False)[1:]
            fig_bar = px.bar(corrs, orientation='h', title="📊 Feature Correlation with Abandonment Risk")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("📋 Raw Data Table")
            st.dataframe(df.sort_values("timestamp_logged", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"Error loading logs: {str(e)}")
