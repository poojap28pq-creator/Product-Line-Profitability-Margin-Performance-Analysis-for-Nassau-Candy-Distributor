# -*- coding: utf-8 -*-
"""
Created on Fri May 22 14:43:43 2026

@author: conne
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===================================================
# PAGE CONFIG
# ===================================================

st.set_page_config(
    page_title="Candy Profitability Dashboard",
    layout="wide"
)

st.title("🍫 Product Line Profitability & Margin Performance Dashboard")

# ===================================================
# LOAD DATA
# ===================================================

df = pd.read_csv("Nassau Candy Distributor.csv")

# ===================================================
# DATA CLEANING
# ===================================================

df['Product Name'] = df['Product Name'].str.strip().str.title()

df['Division'] = df['Division'].str.strip().str.title()

df['Order Date'] = pd.to_datetime(
    df['Order Date'],
    dayfirst=True
)

df['Ship Date'] = pd.to_datetime(
    df['Ship Date'],
    dayfirst=True
)

df = df[df['Sales'] > 0]

df = df[df['Cost'] >= 0]

df = df[df['Gross Profit'].notnull()]

# ===================================================
# SIDEBAR FILTERS
# ===================================================

st.sidebar.header("📌 Filters")

# Division Filter

division_filter = st.sidebar.multiselect(
    "Select Division",
    df['Division'].unique(),
    default=df['Division'].unique()
)

# Product Filter

product_filter = st.sidebar.selectbox(
    "Select Product",
    ['All'] + list(df['Product Name'].unique())
)

# Order Date Filter

order_date = st.sidebar.date_input(
    "Order Date",
    df['Order Date'].min()
)

# Ship Date Filter

ship_date = st.sidebar.date_input(
    "Ship Date",
    df['Ship Date'].max()
)

# Margin Threshold Slider

margin_threshold = st.sidebar.slider(
    "📊 Minimum Gross Margin %",
    min_value=0,
    max_value=100,
    value=0
)
# ===================================================
# FILTER DATA
# ===================================================

filtered_df = df[
    (df['Division'].isin(division_filter)) &
    (df['Order Date'].dt.date >= order_date) &
    (df['Ship Date'].dt.date <= ship_date)
]

# Product Filtering

if product_filter != 'All':

    filtered_df = filtered_df[
        filtered_df['Product Name'] == product_filter
    ]

# ===================================================
# KPI METRICS
# ===================================================

total_sales = filtered_df['Sales'].sum()

total_profit = filtered_df['Gross Profit'].sum()

gross_margin = (
    total_profit / total_sales
) * 100

col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Total Sales",
    f"${total_sales:,.0f}"
)

col2.metric(
    "📈 Total Gross Profit",
    f"${total_profit:,.0f}"
)

col3.metric(
    "📊 Gross Margin %",
    f"{gross_margin:.2f}%"
)

# ===================================================
# PRODUCT SUMMARY
# ===================================================

product_summary = filtered_df.groupby(
    'Product Name'
).agg({
    'Sales': 'sum',
    'Gross Profit': 'sum',
    'Units': 'sum',
    'Cost': 'sum'
}).reset_index()

# KPI Calculations

product_summary['Gross Margin %'] = (
    product_summary['Gross Profit'] /
    product_summary['Sales']
) * 100

product_summary['Profit per Unit'] = (
    product_summary['Gross Profit'] /
    product_summary['Units']
)

product_summary['Revenue Contribution %'] = (
    product_summary['Sales'] /
    product_summary['Sales'].sum()
) * 100

product_summary['Profit Contribution %'] = (
    product_summary['Gross Profit'] /
    product_summary['Gross Profit'].sum()
) * 100

# Margin Threshold Filter

product_summary = product_summary[
    product_summary['Gross Margin %'] >= margin_threshold
]

# ===================================================
# DIVISION SUMMARY
# ===================================================

division_summary = filtered_df.groupby(
    'Division'
).agg({
    'Sales': 'sum',
    'Gross Profit': 'sum'
}).reset_index()

division_summary['Gross Profit %'] = (
    division_summary['Gross Profit'] /
    division_summary['Sales']
) * 100

division_summary['Revenue %'] = (
    division_summary['Sales'] /
    division_summary['Sales'].sum()
) * 100

division_summary['Profit %'] = (
    division_summary['Gross Profit'] /
    division_summary['Gross Profit'].sum()
) * 100

division_summary['Efficiency Gap'] = (
    division_summary['Profit %'] -
    division_summary['Revenue %']
)

# ===================================================
# COST ANALYSIS
# ===================================================

cost_analysis = product_summary.copy()

cost_analysis['Cost Ratio'] = (
    cost_analysis['Cost'] /
    cost_analysis['Sales']
)

# Risk Flags

cost_analysis['Risk Flag'] = 'Healthy'

cost_analysis.loc[
    cost_analysis['Gross Margin %'] < 10,
    'Risk Flag'
] = 'Margin Risk'

cost_analysis.loc[
    cost_analysis['Cost Ratio'] > 0.8,
    'Risk Flag'
] = 'Cost Heavy'

# ===================================================
# REVENUE PARETO ANALYSIS
# ===================================================

revenue_pareto = product_summary.sort_values(
    by='Sales',
    ascending=False
)

revenue_pareto['Revenue %'] = (
    revenue_pareto['Sales'] /
    revenue_pareto['Sales'].sum()
) * 100

revenue_pareto['Cumulative Revenue %'] = (
    revenue_pareto['Revenue %'].cumsum()
)

# ===================================================
# PROFIT PARETO ANALYSIS
# ===================================================

profit_pareto = product_summary.sort_values(
    by='Gross Profit',
    ascending=False
)

profit_pareto['Profit %'] = (
    profit_pareto['Gross Profit'] /
    profit_pareto['Gross Profit'].sum()
) * 100

profit_pareto['Cumulative Profit %'] = (
    profit_pareto['Profit %'].cumsum()
)

# ===================================================
# DEPENDENCY INDICATORS
# ===================================================

top_5_revenue = (
    product_summary
    .sort_values(by='Sales', ascending=False)
    .head(5)['Revenue Contribution %']
    .sum()
)

top_5_profit = (
    product_summary
    .sort_values(by='Gross Profit', ascending=False)
    .head(5)['Profit Contribution %']
    .sum()
)

# ===================================================
# TABS
# ===================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Product Profitability",
    "🏢 Division Analysis",
    "⚠️ Cost Diagnostics",
    "📈 Pareto Analysis",
    "📉 Margin Volatility"
])

# ===================================================
# TAB 1 - PRODUCT PROFITABILITY OVERVIEW
# ===================================================

with tab1:

    st.header("📦 Product Profitability Overview")

    # Margin Leaderboard

    st.subheader("Product-Level Margin Leaderboard")

    st.dataframe(
        product_summary.sort_values(
            by='Gross Margin %',
            ascending=False
        )
    )

    # Profit Contribution Chart

    st.subheader("Profit Contribution Chart")

    fig1, ax1 = plt.subplots(figsize=(12,6))

    ax1.bar(
        product_summary['Product Name'],
        product_summary['Profit Contribution %']
    )

    ax1.set_ylabel("Profit Contribution %")

    plt.xticks(rotation=90)

    plt.tight_layout()

    st.pyplot(fig1)

   
# ===================================================
# TAB 2 - DIVISION PERFORMANCE DASHBOARD
# ===================================================

with tab2:

    st.header("🏢 Division Performance Dashboard")

    # Revenue vs Profit Comparison

    st.subheader("Revenue vs Profit Comparison")

    fig2, ax2 = plt.subplots(figsize=(8,6))

    ax2.scatter(
        division_summary['Revenue %'],
        division_summary['Profit %'],
        s=250
    )

    for i, txt in enumerate(division_summary['Division']):

        ax2.annotate(
            txt,
            (
                division_summary['Revenue %'].iloc[i],
                division_summary['Profit %'].iloc[i]
            )
        )

    ax2.plot([0,100], [0,100], linestyle='--')

    ax2.set_xlabel("Revenue Contribution %")

    ax2.set_ylabel("Profit Contribution %")

    st.pyplot(fig2)

    # Margin Distribution by Division

    st.subheader("Margin Distribution by Division")

    fig3, ax3 = plt.subplots(figsize=(8,5))

    ax3.bar(
        division_summary['Division'],
        division_summary['Gross Profit %']
    )

    ax3.set_ylabel("Gross Profit %")

    st.pyplot(fig3)

# ===================================================
# TAB 3 - COST VS MARGIN DIAGNOSTICS
# ===================================================

with tab3:

    st.header("⚠️ Cost vs Margin Diagnostics")

    # Color Mapping

    colors = []

    for margin in cost_analysis['Gross Margin %']:

        if margin >= cost_analysis['Gross Margin %'].median():
            colors.append('green')

        else:
            colors.append('red')

    # Cost-Sales Scatter Plot

    st.subheader("Cost-Sales Scatter Plot")

    fig4, ax4 = plt.subplots(figsize=(12,6))

    ax4.scatter(
        cost_analysis['Sales'],
        cost_analysis['Cost'],
        s=250,
        c=colors
    )

    for i, txt in enumerate(cost_analysis['Product Name']):

        ax4.annotate(
            txt,
            (
                cost_analysis['Sales'].iloc[i],
                cost_analysis['Cost'].iloc[i]
            ),
            xytext=(5,5),
            textcoords='offset points',
            fontsize=8
        )

    ax4.set_xlabel("Sales")

    ax4.set_ylabel("Cost")

    plt.tight_layout()

    st.pyplot(fig4)

    # Margin Risk Flags

    st.subheader("Margin Risk Flags")

    st.dataframe(
        cost_analysis[
            [
                'Product Name',
                'Gross Margin %',
                'Cost Ratio',
                'Risk Flag'
            ]
        ]
    )

# ===================================================
# TAB 4 - PROFIT CONCENTRATION ANALYSIS
# ===================================================

with tab4:

    st.header("📈 Profit Concentration Analysis")

    # Revenue Pareto Chart

    st.subheader("Pareto Chart by Revenue")

    fig5, ax5 = plt.subplots(figsize=(12,6))

    ax5.bar(
        revenue_pareto['Product Name'],
        revenue_pareto['Revenue %']
    )
    plt.xticks(rotation=90)
    ax6 = ax5.twinx()

    ax6.plot(
        revenue_pareto['Product Name'],
        revenue_pareto['Cumulative Revenue %'],
        marker='o'
    )

    ax6.axhline(
        80,
        color='red',
        linestyle='--'
    )


    plt.tight_layout()

    st.pyplot(fig5)

    # Profit Pareto Chart

    st.subheader("Pareto Chart by Profit")

    fig7, ax7 = plt.subplots(figsize=(12,6))

    ax7.bar(
        profit_pareto['Product Name'],
        profit_pareto['Profit %']
    )
    
    plt.xticks(rotation=90)
    
    ax8 = ax7.twinx()

    ax8.plot(
        profit_pareto['Product Name'],
        profit_pareto['Cumulative Profit %'],
        marker='o'
    )

    ax8.axhline(
        80,
        color='red',
        linestyle='--'
    )

   

    plt.tight_layout()

    st.pyplot(fig7)

    # Dependency Indicators

    st.subheader("Dependency Indicators")

    col4, col5 = st.columns(2)

    col4.metric(
        "Top 5 Products Revenue Dependency",
        f"{top_5_revenue:.2f}%"
    )

    col5.metric(
        "Top 5 Products Profit Dependency",
        f"{top_5_profit:.2f}%"
    )
    
# ===================================================
# MARGIN VOLATILITY ANALYSIS
# ===================================================

# Row-Level Margin %

filtered_df['Margin %'] = (
    filtered_df['Gross Profit'] /
    filtered_df['Sales']
) * 100

# Product-Level Margin Volatility

margin_volatility = filtered_df.groupby(
    'Product Name'
)['Margin %'].std().reset_index()

# Rename Column

margin_volatility.rename(
    columns={
        'Margin %': 'Margin Volatility'
    },
    inplace=True
)

# Fill Missing Values

margin_volatility['Margin Volatility'] = (
    margin_volatility['Margin Volatility']
    .fillna(0)
)

# Merge into Product Summary

product_summary = pd.merge(
    product_summary,
    margin_volatility,
    on='Product Name',
    how='left'
)
    
# ===================================================
# TAB 5 - MARGIN VOLATILITY ANALYSIS
# ===================================================

with tab5:

    st.header("📉 Margin Volatility Analysis")

    st.write(
        """
        Margin volatility measures how unstable or fluctuating
        product margins are over time.
        High volatility may indicate:
        
        - pricing inconsistency
        - unstable costs
        - discounting pressure
        - operational inefficiency
        """
    )

    # Sort by highest volatility

    volatility_table = product_summary.sort_values(
        by='Margin Volatility',
        ascending=False
    )

    # Display Table

    st.subheader("Product Margin Volatility Table")

    st.dataframe(
        volatility_table[
            [
                'Product Name',
                'Gross Margin %',
                'Margin Volatility'
            ]
        ]
    )

    # Volatility Chart

    st.subheader("Margin Volatility by Product")

    fig9, ax9 = plt.subplots(figsize=(12,6))

    ax9.bar(
        volatility_table['Product Name'],
        volatility_table['Margin Volatility']
    )
    
    plt.xticks(rotation=90)

    ax9.set_ylabel("Margin Volatility")


    plt.tight_layout()

    st.pyplot(fig9)

    # High Risk Products

    high_volatility = volatility_table[
        volatility_table['Margin Volatility'] >
        volatility_table['Margin Volatility'].median()
    ]

    st.subheader("⚠️ High Margin Volatility Products")

    st.dataframe(
        high_volatility[
            [
                'Product Name',
                'Margin Volatility'
            ]
        ]
    )