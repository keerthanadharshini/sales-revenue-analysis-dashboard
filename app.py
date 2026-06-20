import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Sales & Revenue Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df = load_data("sales_data.csv")
st.title("📊 Sales & Revenue Analysis Dashboard")
st.markdown("Explore revenue trends, top-performing products, and category breakdowns.")

st.sidebar.header("🔎 Filters")

all_categories = sorted(df["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "Category",
    options=all_categories,
    default=all_categories,
)

products_in_selected_categories = sorted(
    df[df["Category"].isin(selected_categories)]["Product"].unique()
)
selected_products = st.sidebar.multiselect(
    "Product",
    options=products_in_selected_categories,
    default=products_in_selected_categories,
)

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
selected_date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)


if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
else:
    start_date, end_date = min_date, max_date


mask = (
    df["Category"].isin(selected_categories)
    & df["Product"].isin(selected_products)
    & (df["Order Date"].dt.date >= start_date)
    & (df["Order Date"].dt.date <= end_date)
)
filtered_df = df[mask]


if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()


total_revenue = filtered_df["Revenue"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_orders = len(filtered_df)


kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(label="💰 Total Revenue", value=f"${total_revenue:,.2f}")
kpi2.metric(label="📦 Total Quantity Sold", value=f"{total_quantity:,}")
kpi3.metric(label="🧾 Total Orders", value=f"{total_orders:,}")

st.markdown("---") 
st.subheader("📈 Revenue Trend Over Time")
revenue_trend = (
    filtered_df.groupby("Order Date")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("Order Date")
)
fig_trend = px.line(
    revenue_trend,
    x="Order Date",
    y="Revenue",
    title="Daily Revenue Trend",
    markers=True,
)
fig_trend.update_layout(xaxis_title="Order Date", yaxis_title="Revenue ($)")
st.plotly_chart(fig_trend, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top Products by Revenue")
    top_products = (
        filtered_df.groupby("Product")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("Revenue", ascending=False)
        .head(10)  
    )
    fig_top_products = px.bar(
        top_products,
        x="Revenue",
        y="Product",
        orientation="h",
        title="Top 10 Products",
        color="Revenue",
        color_continuous_scale="Blues",
    )
    
    fig_top_products.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_top_products, use_container_width=True)


with col2:
    st.subheader("🥧 Revenue by Category")
    revenue_by_category = (
        filtered_df.groupby("Category")["Revenue"].sum().reset_index()
    )
    fig_category_pie = px.pie(
        revenue_by_category,
        names="Category",
        values="Revenue",
        title="Revenue Share by Category",
        hole=0.4,  # Donut-style pie chart for a more modern look
    )
    st.plotly_chart(fig_category_pie, use_container_width=True)


with st.expander("🔍 View Filtered Raw Data"):
    st.dataframe(filtered_df.sort_values("Order Date"), use_container_width=True)
