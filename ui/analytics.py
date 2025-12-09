import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

API_URL = "http://172.30.31.76:8000"

def analytics_page():

    st.title("Financial Dashboard")

    # -----------------------------
    # LOAD TRANSACTIONS
    # -----------------------------
    try:
        tx_res = requests.get(f"{API_URL}/transactions")
        data = tx_res.json()
    except:
        st.error("Error loading data.")
        return

    if not data:
        st.info("No data to analyze yet.")
        return

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()

    # -----------------------------
    # BALANCE CARDS
    # -----------------------------
    income = df[df["type"] == "income"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()
    balance = income - expenses

    col1, col2, col3 = st.columns(3)

    col1.metric("Balance", f"${balance:,.0f}")
    col2.metric("Income", f"${income:,.0f}")
    col3.metric("Expenses", f"${expenses:,.0f}")

    st.markdown("---")

    # -----------------------------
    # TIME SERIES: Income vs Expense
    # -----------------------------
    st.subheader("Income vs Expense Over Time")

    ts = df.groupby(["date", "type"])["amount"].sum().reset_index()
    fig_ts = px.line(ts, x="date", y="amount", color="type",
                     template="simple_white",
                     markers=True)
    fig_ts.update_traces(line=dict(width=3))
    st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")

    # -----------------------------
    # CATEGORY PIE CHART
    # -----------------------------
    st.subheader("Spending Distribution by Category")

    cat_df = df[df["type"] == "expense"].groupby("category")["amount"].sum().reset_index()
    fig_pie = px.pie(cat_df, values="amount", names="category",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # -----------------------------
    # HEATMAP — SPENDING BY WEEKDAY
    # -----------------------------
    st.subheader("Spending Heatmap by Day of Week")

    heat = df[df["type"] == "expense"].groupby(["weekday"])["amount"].sum().reindex(
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    )

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=heat.values.tolist(),
            x=["Spending"],
            y=heat.index.tolist(),
            colorscale="Blues"
        )
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # -----------------------------
    # TOP CATEGORIES THIS MONTH
    # -----------------------------
    st.subheader("Top Spending Categories (This Month)")

    current_month = datetime.now().strftime("%Y-%m")
    top_df = (
        df[(df["type"] == "expense") & (df["month"] == current_month)]
        .groupby("category")["amount"].sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    fig_top = px.bar(top_df, x="amount", y="category",
                     orientation="h",
                     color="amount",
                     color_continuous_scale="Blues")
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")

    # -----------------------------
    # SIMPLE MONTHLY FORECAST
    # -----------------------------
    st.subheader("Projected Month Expense")

    month_df = (
        df[df["type"] == "expense"]
        .groupby("date")["amount"].sum()
        .reset_index()
    )

    # Regression fit
    try:
        month_df["day"] = month_df["date"].dt.day
        coef = pd.np.polyfit(month_df["day"], month_df["amount"], 1)
        predicted_end = coef[0] * 30 + coef[1]

        st.info(f"Estimated total spending this month: **${predicted_end:,.0f}**")
    except:
        st.info("Not enough data to compute forecast.")
