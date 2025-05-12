import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from fungsi import (
    load_data,
    analyze_product_sales,
    analyze_customer_satisfaction,
    analyze_monthly_orders,
)

# --- Page configuration ---
st.set_page_config(
    page_title="E-commerce Data Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load data ---
CSV_FILE_PATH = "all_data_e-commerse.csv"


@st.cache_data
def get_data(path):
    # Aktualisasi data dari file CSV
    return load_data(path)


# Use st.spinner to show loading progress
with st.spinner("Loading and processing data..."):
    data = get_data(CSV_FILE_PATH)

if data is None:
    st.error("Failed to load data. Please ensure data exists.")
    st.stop()  # Stop the app if data loading fails

# memastikan kolom 'order_purchase_timestamp' ada dan dalam format datetime
# Check if 'order_purchase_timestamp' exists and is in datetime format
if (
    "order_purchase_timestamp" not in data.columns
    or not pd.api.types.is_datetime64_any_dtype(data["order_purchase_timestamp"])
):
    st.error(
        (
            "Required 'order_purchase_timestamp' column not found or not in "
            "datetime format after loading. Cannot apply date filter."
        )
    )
    # Lakukan stop jika kolom tidak ada
    st.stop()

# --- Sidebar ---
st.sidebar.header("Filters")

# Temukan minimum dan maksimum tanggal dari kolom 'order_purchase_timestamp'
# pastikan kolom ada dan dalam format datetime
if "order_purchase_timestamp" in data.columns and pd.api.types.is_datetime64_any_dtype(
    data["order_purchase_timestamp"]
):
    min_date_overall = data["order_purchase_timestamp"].min()
    max_date_overall = data["order_purchase_timestamp"].max()

    # Penangan potensi missing values
    if pd.isna(min_date_overall):
        # Default to today or some fallback
        min_date_overall = datetime.date.today()
    else:
        min_date_overall = min_date_overall.date()

    if pd.isna(max_date_overall):
        # Default to today or some fallback
        max_date_overall = datetime.date.today()
    else:
        max_date_overall = max_date_overall.date()

    st.sidebar.subheader("Select Date Range (Order Purchase)")

    # Masukkan input tanggal di sidebar
    # Set data default ke rentang tanggal minimum dan maksimum
    selected_date_range = st.sidebar.date_input(
        "Select period:",
        value=(min_date_overall, max_date_overall),
        min_value=min_date_overall,
        max_value=max_date_overall,
    )

    # Pastikan elemen dalam selected_date_range adalah datetime.date
    if len(selected_date_range) == 2:
        start_date_filter = selected_date_range[0]
        end_date_filter = selected_date_range[1]

        # Display selected range
        st.sidebar.write(
            (
                f"Applying filter from: "
                f"**{start_date_filter.strftime('%Y-%m-%d')}** "
                f"to **{end_date_filter.strftime('%Y-%m-%d')}**"
            )
        )

        # --- Apply the date filter to the data ---
        # Filter data berdasarkan rentang tanggal yang dipilih

        filtered_data = data.dropna(
            subset=["order_purchase_timestamp"]
        ).copy()  # Drop NaT before filtering by date

        # konvertir tanggal ke format datetime
        start_datetime = pd.to_datetime(start_date_filter)
        end_datetime = (
            pd.to_datetime(end_date_filter)
            + pd.Timedelta(days=1)
            - pd.Timedelta(seconds=1)
        )  # Include the whole end day

        filtered_data = filtered_data[
            (filtered_data["order_purchase_timestamp"] >= start_datetime)
            & (filtered_data["order_purchase_timestamp"] <= end_datetime)
        ].copy()  # Use copy() to prevent SettingWithCopyWarning

    else:
        # jika tidak ada rentang tanggal yang valid, tampilkan peringatan
        st.sidebar.warning("Please select a valid date range.")
        filtered_data = data.copy()  # Use full data if filter is invalid
else:
    # jika kolom tidak ada, tampilkan peringatan
    filtered_data = data.copy()


# --- Check if filtered data is empty ---
if filtered_data.empty:
    st.warning("No data available for the selected date range.")
    # Optionally, you could hide the analysis sections or display specific
    # "No data" messages for each
    show_analyses = False
else:
    show_analyses = True
    st.subheader(
        f"Analyzing data from {filtered_data['order_purchase_timestamp'].min().strftime('%Y-%m-%d')} "
        f"to "
        f"{filtered_data['order_purchase_timestamp'].max().strftime('%Y-%m-%d')}"
    )
# --- Sidebar options ---
# Display actual range of filtered data


# --- Main content Dashboard ---
# Pastikan show_analyses True sebelum menampilkan analisis
if show_analyses:

    # 1. Product Sales Analysis
    st.header("1. Product Sales Analysis")
    # Pass the filtered data to the analysis function
    top_selling, bottom_selling = analyze_product_sales(filtered_data)

    if top_selling is not None and bottom_selling is not None:
        if (
            not top_selling.empty or not bottom_selling.empty
        ):  # Check if results are not empty
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Top Selling Product Categories")
                if not top_selling.empty:
                    st.bar_chart(top_selling)
                    st.dataframe(
                        top_selling.reset_index().rename(
                            columns={
                                "index": "Product Category",
                                "price": "Total Sales",
                            }
                        )
                    )
                else:
                    st.info("No top selling products in this range.")
            with col2:
                st.subheader("Bottom Selling Product Categories")
                if not bottom_selling.empty:
                    st.bar_chart(
                        bottom_selling.sort_values(ascending=True)
                    )  # Reverse sort for bottom chart readability
                    st.dataframe(
                        bottom_selling.reset_index().rename(
                            columns={
                                "index": "Product Category",
                                "price": "Total Sales",
                            }
                        )
                    )
                else:
                    st.info("No bottom selling products in this range.")
        else:
            st.info("No product sales data found for the selected range.")
    else:
        st.warning(
            (
                "Could not perform product sales analysis. Check if required "
                "columns exist and have data."
            )
        )

    # 2. Customer Satisfaction Analysis
    st.header("2. Customer Satisfaction Analysis")
    # Pass the filtered data to the analysis function.
    # It now analyzes the selected date range.
    average_score, score_distribution = analyze_customer_satisfaction(
        filtered_data
    )  # Panggil fungsi baru

    # Fungsi analyze_customer_satisfaction mengembalikan 0 jika tidak ada
    # data review
    if average_score > 0:  # Check if average_score is greater than 0
        # (means data was found in the range)
        st.subheader("Average Review Score")
        st.metric("Average Score", f"{average_score:.2f} / 5.0")

        st.subheader("Review Score Distribution")
        fig, ax = plt.subplots()
        ax.bar(score_distribution.index, score_distribution.values)
        ax.set_xlabel("Review Score")
        ax.set_ylabel("Number of Reviews")
        ax.set_title(
            "Distribution of Review Scores (within selected range)"
        )  # Ubah judul plot
        ax.set_xticks(
            score_distribution.index
        )  # Ensure all scores 1-5 are shown if they exist
        st.pyplot(fig)
        plt.close(fig)  # Close the figure to free memory

        st.dataframe(
            score_distribution.reset_index().rename(
                columns={"index": "Score", "review_score": "Count"}
            )
        )

    else:
        # Pesan ini ditampilkan jika
        # analyze_customer_satisfaction
        # mengembalikan 0
        st.info("No review data available for the selected date range.")  # Ubah pesan

    # 3. Monthly Order Analysis
    st.header("3. Monthly Order Analysis")
    # Pass the filtered data to the analysis function
    monthly_orders = analyze_monthly_orders(filtered_data)

    if (
        monthly_orders is not None and not monthly_orders.empty
    ):  # Check if not None and not empty
        st.subheader("Monthly Order Trend (within selected date range)")
        st.line_chart(monthly_orders)
        st.dataframe(
            monthly_orders.reset_index().rename(
                columns={"index": "Month", 0: "Order Count"}
            )
        )
    else:
        st.info("No monthly order data found for the selected date range.")

# --- Footer (Optional) ---
st.markdown("---")
st.write("Dashboard dibuat dengan Streamlit oleh Faizal Riza")
