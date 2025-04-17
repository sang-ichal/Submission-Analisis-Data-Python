# **Membuat Dashboard Dengan Streamlite**
# **E-Commerce Dashboard**

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from fungsi import DataAnalyzer

sns.set_theme(style='dark')

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date", "review_creation_date"]
all_df = pd.read_csv("all_data_e-commerse.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True, drop=True)

# Make sure the column is in datetime format
all_df["order_approved_at"] = pd.to_datetime(all_df["order_approved_at"], errors='coerce')

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Then you can safely compare
main_df = all_df[
    (all_df["order_approved_at"] >= pd.to_datetime(min_date)) &
    (all_df["order_approved_at"] <= pd.to_datetime(max_date))
]

#for col in datetime_cols:
#    all_df[col] = pd.to_datetime(all_df[col])



# Sidebar
with st.sidebar:
    # Title
    st.title("Faizal Riza")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= pd.to_datetime(start_date)) &
                    (all_df["order_approved_at"] <= pd.to_datetime(end_date))]

function = DataAnalyzer(main_df)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Title
st.header("E-Commerce Dashboard")

# Daily Orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig_daily_orders, ax_daily_orders = plt.subplots(figsize=(12, 6))
ax_daily_orders.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax_daily_orders.tick_params(axis="x", rotation=45)
ax_daily_orders.tick_params(axis="y", labelsize=15)
st.pyplot(fig_daily_orders)

# Order Items
st.subheader("Order Items")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["products"].sum()
    st.markdown(f"Total Items: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["products"].mean()
    st.markdown(f"Average Items: **{avg_items:.2f}**")

fig_order_items, ax_order_items = plt.subplots(nrows=1, ncols=2, figsize=(15, 8)) # Reduced figure size

sns.barplot(x="products", y="product_category_name_english", hue=sum_order_items_df["product_category_name_english"], data=sum_order_items_df.head(5), palette="viridis", ax=ax_order_items[0], legend=False)
ax_order_items[0].set_ylabel(None)
ax_order_items[0].set_xlabel("Number of Sales")
ax_order_items[0].set_title("Best Selling products", loc="center")
ax_order_items[0].tick_params(axis ='y', labelsize=10)
ax_order_items[0].tick_params(axis ='x', labelsize=10)

sns.barplot(x="products", y="product_category_name_english", hue=sum_order_items_df.sort_values(by="products", ascending=True)["product_category_name_english"], data=sum_order_items_df.sort_values(by="products", ascending=True).head(5), palette="viridis", ax=ax_order_items[1], legend=False)
ax_order_items[1].set_ylabel(None)
ax_order_items[1].set_xlabel("Number of Sales")
ax_order_items[1].invert_xaxis()
ax_order_items[1].yaxis.set_label_position("right")
ax_order_items[1].yaxis.tick_right()
ax_order_items[1].set_title("Worst selling products", loc="center")
ax_order_items[1].tick_params(axis='y', labelsize=10)
ax_order_items[1].tick_params(axis='x', labelsize=10)

st.pyplot(fig_order_items)

# Review Score
st.subheader("Review Score")

# Convert start_date and end_date to datetime objects
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Convert 'review_creation_date' column to datetime if not already
all_df['review_creation_date'] = pd.to_datetime(all_df['review_creation_date'], format='ISO8601')

# Filter data based on the selected date range
review_data = all_df[
    (all_df['review_creation_date'] >= start_date) &
    (all_df['review_creation_date'] <= end_date)
]

col1, col2 = st.columns(2)

with col1:
    total_reviews = review_data.shape[0]
    st.markdown(f"Total Reviews: **{total_reviews}**")

with col2:
    avg_review = review_data['review_score'].mean()
    st.markdown(f"Average Review Score: **{avg_review:.2f}**")

fig_review, ax_review = plt.subplots(figsize=(10, 5)) # Use subplots
sns.countplot(x=review_data['review_creation_date'].dt.month,
              hue=review_data['review_score'],
              palette="viridis",
              ax=ax_review)

ax_review.set_title("Customer Satisfaction", fontsize=15)
ax_review.set_xlabel("Month")
ax_review.set_ylabel("Count of Reviews")
ax_review.legend(title="Review Score", loc='upper right', bbox_to_anchor=(1.2, 1))

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Des']
ax_review.set_xticks(range(0, 12))
ax_review.set_xticklabels(months)

st.pyplot(fig_review)

# Order Approved
st.subheader("Orders Approved")

orders_approved_df = all_df[(all_df['order_approved_at'] >= start_date) & (all_df['order_approved_at'] <= end_date)]

monthly_order = orders_approved_df.resample(rule='ME', on='order_approved_at').agg({
    "order_id": "size",
})
monthly_order.index = monthly_order.index.strftime('%B')
monthly_order = monthly_order.reset_index()
monthly_order.rename(columns={
    "order_id": "order_count",
    "order_approved_at": "month"
}, inplace=True)

month_mapping = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

monthly_order["month_numeric"] = monthly_order["month"].map(month_mapping)
monthly_order = monthly_order.sort_values("month_numeric")
monthly_order = monthly_order.drop("month_numeric", axis=1)

col1, col2 = st.columns(2)

with col1:
    # Calculate total orders and average orders per month
    total_orders = orders_approved_df.shape[0]
    st.markdown(f"Total Orders Approved: **{total_orders}**")

with col2:
    # Average orders per month
    avg_orders_per_month = orders_approved_df.resample(rule='ME', on='order_approved_at').size().mean()
    st.markdown(f"Average Orders per Month: **{avg_orders_per_month:.2f}**")

fig_monthly_orders, ax_monthly_orders = plt.subplots(figsize=(10, 5)) # Use subplots
ax_monthly_orders.plot(
    monthly_order["month"],
    monthly_order["order_count"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
ax_monthly_orders.set_title("Number of Orders Approved per Month", loc="center")
ax_monthly_orders.tick_params(axis="x", rotation=45)
ax_monthly_orders.tick_params(axis="y", labelsize=10)
st.pyplot(fig_monthly_orders)

st.caption('Copyright (C) Faizal Riza 2025')