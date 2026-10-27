import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Retail Sales Analysis", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center; color: #4682B4;'>
        Retail Sales Analysis
    </h1>
    <p style='text-align: center; font-size: 16px;'>
        An overview of sales, profit and customer trends from 2022–2025
    </p>
    """,
    unsafe_allow_html=True
)
col_left, col_center, col_right = st.columns([1, 6, 1])
with col_center:
    st.image(r'C:\Users\Maison\OneDrive\Desktop\Retail Img.jpg', use_container_width=True)

# cleaned dataset
df = pd.read_csv("cleaned_retail_dataset.csv")

# Prepare dates for the monthly sales chart
df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

page = st.sidebar.radio(
    "Pages",
    ["Page 1: Sales Overview", "Page 2: Product and Customer Analysis"],
    key="page_navigation",
)

st.sidebar.divider()
st.sidebar.subheader("Filters")
st.sidebar.caption("Choose one or more values")

year_options = sorted(df["Order_Year"].dropna().astype(int).unique().tolist())
region_options = sorted(df["Region"].dropna().astype(str).unique().tolist())
category_options = sorted(df["Product_Category"].dropna().astype(str).unique().tolist())
channel_options = sorted(df["Sales_Channel"].dropna().astype(str).unique().tolist())
payment_options = sorted(df["Payment_Method"].dropna().astype(str).unique().tolist())

selected_years = st.sidebar.multiselect(
    "Order Year", options=year_options, default=[], key="filter_year"
)
selected_regions = st.sidebar.multiselect(
    "Region", options=region_options, default=[], key="filter_region"
)
selected_categories = st.sidebar.multiselect(
    "Product Category", options=category_options, default=[], key="filter_category"
)
selected_channels = st.sidebar.multiselect(
    "Sales Channel", options=channel_options, default=[], key="filter_channel"
)
selected_payment_methods = st.sidebar.multiselect(
    "Payment Method", options=payment_options, default=[], key="filter_payment_method"
)
# Apply selected filters to the dataset
filtered_df = df.copy()

if selected_years:
    filtered_df = filtered_df[
        filtered_df["Order_Year"].isin(selected_years)
    ]

if selected_regions:
    filtered_df = filtered_df[
        filtered_df["Region"].astype(str).isin(selected_regions)
    ]

if selected_categories:
    filtered_df = filtered_df[
        filtered_df["Product_Category"].astype(str).isin(selected_categories)
    ]

if selected_channels:
    filtered_df = filtered_df[
        filtered_df["Sales_Channel"].astype(str).isin(selected_channels)
    ]

if selected_payment_methods:
    filtered_df = filtered_df[
        filtered_df["Payment_Method"].astype(str).isin(selected_payment_methods)
    ]

st.sidebar.caption(
    f"Rows matching filters: {len(filtered_df):,} of {len(df):,}"
)
full_df = df          # keep the original if you ever need it
df = filtered_df      # everything below now uses filtered data

# Colours used
category_colors = {
    "Appliances": "#90EE90",
    "Electronics": "#4682B4",
    "Furniture": "#FFA500",
    "Office Supplies": "#FF69B4"
}

status_colors = {
    "Completed": "#2E8B57",
    "Shipped": "#4682B4",
    "Returned": "#FFA500",
    "Processing": "#9370DB",
    "Cancelled": "#DC143C"
}

return_colors = {
    "Late Delivery": "#990000",
    "Wrong Item": "#D92D2D",
    "Damaged": "#F25353",
    "Other": "#FF8080",
    "Defective": "#FFAAAA",
    "Changed Mind": "#FFCACA"
}

shipping_colors = {
    "Standard": "#2E8B57",
    "Next Day": "#4682B4",
    "Express": "#FFA500",
    "Pickup": "#9370DB"
}

rating_colors = {
    1: "#D73027",
    2: "#F46D43",
    3: "#FDAE61",
    4: "#A6D96A",
    5: "#1A9850"
}


# -------------------------
# PAGE 1: SALES OVERVIEW
# -------------------------
if page == "Page 1: Sales Overview":
    st.header("Sales Overview")

    total_sales = df["Sales_Amount"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order_ID"].nunique()
    average_order_value = total_sales / total_orders if total_orders else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${total_sales:,.0f}")
    col2.metric("Total Profit", f"${total_profit:,.0f}")
    col3.metric("Unique Orders", f"{total_orders:,}")
    col4.metric("Average Order Value", f"${average_order_value:,.2f}")
    st.dataframe(df)

    # Orders by Year
    st.subheader("Orders by Year")
    orders_by_year = df["Order_Year"].value_counts().reset_index()
    fig_year = px.bar(
        orders_by_year,
        x="Order_Year",
        y="count",
        title="Orders by Year",
        color_discrete_sequence=["lightblue"]
    )
    fig_year.update_xaxes(dtick=1, tickmode="linear")
    st.plotly_chart(fig_year, use_container_width=True)

   # Monthly Sales Trend
    st.subheader("Monthly Sales Trend")

    # Create a copy so the original dataset remains unchanged
    monthly_df = df.copy()

    # Convert Order_Date to datetime format
    monthly_df["Order_Date"] = pd.to_datetime(
        monthly_df["Order_Date"],
        errors="coerce"
    )

    # Remove rows with invalid dates for this chart
    monthly_df = monthly_df.dropna(subset=["Order_Date"])

    # Group sales by month
    monthly_df["Month"] = monthly_df["Order_Date"].dt.to_period("M")

    monthly_sales = (
        monthly_df.groupby("Month", as_index=False)["Sales_Amount"]
        .sum()
    )

    # Convert monthly periods back to dates
    monthly_sales["Order_Date"] = (
        monthly_sales["Month"].dt.to_timestamp()
    )

    # Chart
    fig_monthly = px.line(
        monthly_sales,
        x="Order_Date",
        y="Sales_Amount",
        title="Monthly Sales Trend",
        markers=True
    ).update_traces(
        line_color="green"
    ).update_xaxes(
        range=["2022-01-01", "2025-12-31"]
    )

    # Display
    st.plotly_chart(fig_monthly, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sales by Product Category")
        category_sales = df.groupby(
            "Product_Category", as_index=False
        )["Sales_Amount"].sum()

        fig_category_sales = px.bar(
            category_sales,
            x="Sales_Amount",
            y="Product_Category",
            orientation="h",
            title="Total Sales by Product Category",
            color="Product_Category",
            color_discrete_map=category_colors
        ).update_layout(
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig_category_sales, use_container_width=True)

    with col2:
        st.subheader("Profit by Product Category")
        category_profit = df.groupby(
            "Product_Category", as_index=False
        )["Profit"].sum()

        fig_category_profit = px.bar(
            category_profit,
            x="Profit",
            y="Product_Category",
            orientation="h",
            title="Total Profit by Product Category",
            color="Product_Category",
            color_discrete_map=category_colors,
            text_auto=".2s"
        ).update_layout(
            yaxis={"categoryorder": "total ascending"},
            xaxis_title="Total Profit",
            yaxis_title="Product Category"
        )
        st.plotly_chart(fig_category_profit, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sales by Sales Channel")
        sales_channel = df.groupby(
            "Sales_Channel", as_index=False
        )["Sales_Amount"].sum()

        channel_colors = {
            "Online": "#4682B4",
            "B2B Portal": "#90EE90",
            "Phone Order": "#ADFF2F",
            "Retail Store": "#FF8C00"
        }

        fig_channel = px.bar(
            sales_channel,
            x="Sales_Channel",
            y="Sales_Amount",
            title="Total Sales by Sales Channel",
            color="Sales_Channel",
            color_discrete_map=channel_colors,
            text=sales_channel["Sales_Amount"].map(lambda x: f"{x:,.0f}")
        ).update_layout(
            xaxis_title="Sales Channel",
            yaxis_title="Total Sales",
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            showlegend=False
        ).update_traces(
            textposition="outside"
        )
        st.plotly_chart(fig_channel, use_container_width=True)

    with col2:
        st.subheader("Sales by Region")
        sales_region = (
            df.groupby("Region", as_index=False)["Sales_Amount"]
            .sum()
            .sort_values("Sales_Amount", ascending=True)
        )

        fig_region = px.bar(
            sales_region,
            x="Sales_Amount",
            y="Region",
            orientation="h",
            title="Total Sales by Region",
            color_discrete_sequence=["#4682B4"],
            text=sales_region["Sales_Amount"].map(lambda x: f"{x:,.0f}")
        ).update_layout(
            xaxis_title="Total Sales",
            yaxis_title="Region",
            xaxis_tickprefix="$",
            xaxis_tickformat=",.0f",
            showlegend=False
        ).update_traces(
            textposition="outside",
            cliponaxis=False
        )
        st.plotly_chart(fig_region, use_container_width=True)

    # Order Status Distribution
    st.subheader("Order Status Distribution")
    status_counts = df["Order_Status"].value_counts().reset_index()
    fig_status = px.bar(
        status_counts,
        x="Order_Status",
        y="count",
        title="Order Status Distribution",
        color="Order_Status",
        color_discrete_map=status_colors,
        text_auto=True
    ).update_layout(
        xaxis_title="Order Status",
        yaxis_title="Number of Orders"
    )
    st.plotly_chart(fig_status, use_container_width=True)

# -------------------------
# PAGE 2: PRODUCT AND CUSTOMER ANALYSIS
# -------------------------
elif page == "Page 2: Product and Customer Analysis":
    st.header("Product and Customer Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Return Reasons Distribution")
        return_counts = (
            df[df["Return_Flag"] == "Yes"]["Return_Reason"]
            .value_counts()
            .reindex(
                ["Late Delivery", "Wrong Item", "Damaged", "Other", "Defective", "Changed Mind"],
                fill_value=0
            )
            .rename_axis("Return_Reason")
            .reset_index(name="count")
        )

        fig_returns = px.bar(
            return_counts,
            x="Return_Reason",
            y="count",
            title="Return Reasons Distribution",
            color="Return_Reason",
            color_discrete_map=return_colors,
            text_auto=True
        ).update_layout(
            xaxis_title="Return Reason",
            yaxis_title="Number of Returns"
        )
        st.plotly_chart(fig_returns, use_container_width=True)

    with col2:
        st.subheader("Return Rate by Product Category")
        return_rate = (
            df.groupby("Product_Category")
            .agg(
                Total_Orders=("Order_ID", "nunique"),
                Returned_Orders=("Return_Flag", lambda x: (x == "Yes").sum())
            )
            .reset_index()
        )
        return_rate["Return_Rate"] = (
            return_rate["Returned_Orders"] / return_rate["Total_Orders"] * 100
        )

        fig_return_rate = px.bar(
            return_rate,
            x="Product_Category",
            y="Return_Rate",
            title="Return Rate by Product Category",
            color="Product_Category",
            color_discrete_map=category_colors,
            text=return_rate["Return_Rate"].map(lambda x: f"{x:.1f}%")
        ).update_layout(
            xaxis_title="Product Category",
            yaxis_title="Return Rate (%)",
            yaxis_ticksuffix="%",
            showlegend=False
        ).update_traces(
            textposition="outside"
        )
        st.plotly_chart(fig_return_rate, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Delivery Time by Shipping Method")
        fig_delivery = px.box(
            df.dropna(subset=["Delivery_Days"]),
            x="Shipping_Method",
            y="Delivery_Days",
            color="Shipping_Method",
            color_discrete_map=shipping_colors,
            title="Delivery Time by Shipping Method"
        ).update_layout(
            xaxis_title="Shipping Method",
            yaxis_title="Delivery Days"
        )
        st.plotly_chart(fig_delivery, use_container_width=True)

    with col2:
        st.subheader("Customer Rating Breakdown")
        rating_counts = (
            df.dropna(subset=["Customer_Rating"])["Customer_Rating"]
            .value_counts()
            .sort_index()
            .reset_index()
        )

        fig_ratings = px.pie(
            rating_counts,
            names="Customer_Rating",
            values="count",
            title="Customer Rating Breakdown",
            hole=0.5,
            color="Customer_Rating",
            color_discrete_map=rating_colors
        )
        st.plotly_chart(fig_ratings, use_container_width=True)

    st.subheader("Profit Margin by Product Category")
    profit_margin = (
        df.groupby("Product_Category", as_index=False)
        .agg(
            Total_Sales=("Sales_Amount", "sum"),
            Total_Profit=("Profit", "sum")
        )
    )
    profit_margin["Profit_Margin"] = (
        profit_margin["Total_Profit"] / profit_margin["Total_Sales"] * 100
    )
    profit_margin = profit_margin.sort_values("Profit_Margin", ascending=False)

    fig_margin = px.bar(
        profit_margin,
        x="Product_Category",
        y="Profit_Margin",
        title="Profit Margin by Product Category",
        color_discrete_sequence=["#4682B4"],
        text=profit_margin["Profit_Margin"].map(lambda x: f"{x:.1f}%")
    ).update_layout(
        xaxis_title="Product Category",
        yaxis_title="Profit Margin (%)",
        yaxis_ticksuffix="%",
        showlegend=False
    ).update_traces(
        textposition="outside",
        cliponaxis=False
    )
    st.plotly_chart(fig_margin, use_container_width=True)
