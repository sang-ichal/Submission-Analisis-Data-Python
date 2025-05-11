import pandas as pd
import numpy as np

def load_data(filepath):
    """
    Loads the data from the CSV file and attempts to parse date columns.
    Uses errors='coerce' for date parsing to handle potential format issues.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        pandas.DataFrame: The loaded data, or None if an error occurs.
    """
    try:
        # Attempt to read with initial date parsing
        df = pd.read_csv(filepath) # Don't rely solely on parse_dates here

        # List of columns expected to be dates
        date_columns = [
            'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
            'order_delivered_customer_date', 'order_estimated_delivery_date',
            'review_creation_date', 'review_answer_timestamp', 'shipping_limit_date'
        ]

        # Explicitly convert date columns using errors='coerce'
        for col in date_columns:
            if col in df.columns: # Check if column exists
                df[col] = pd.to_datetime(df[col], errors='coerce')
            else:
                print(f"Warning: Date column '{col}' not found in the dataset.")

        return df
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def analyze_product_sales(df, top_n=10):
    """
    Analyzes product sales by category and returns the top and bottom N selling categories.

    Args:
        df (pandas.DataFrame): The input DataFrame.
        top_n (int, optional): The number of top and bottom categories to return. Defaults to 10.

    Returns:
        tuple: A tuple containing two pandas.Series: (top_selling, bottom_selling).
               Returns (None, None) if the required columns are not found.
    """
    if 'product_category_name_english' not in df.columns or 'price' not in df.columns:
        print("Error: Required columns 'product_category_name_english' or 'price' not found.")
        return None, None

    # Handle missing values in relevant columns
    df_product_sales = df.dropna(subset=['product_category_name_english', 'price']).copy() # Use copy()

    if df_product_sales.empty:
        print("Info: No valid product sales data found in the provided DataFrame.")
        return pd.Series(dtype=float), pd.Series(dtype=float)


    # Calculate total sales per category
    product_sales = df_product_sales.groupby('product_category_name_english')['price'].sum().sort_values(ascending=False) # Sort descending for top

    top_selling = product_sales.head(top_n)
    bottom_selling = product_sales.tail(top_n)  # Get the last N after sorting descending

    return top_selling, bottom_selling


# --- FUNGSI INI DIGANTI NAMANYA & LOGIKA 2018 DIHAPUS ---
def analyze_customer_satisfaction(df):
    """
    Analyzes customer satisfaction based on review scores for the provided data.

    Args:
        df (pandas.DataFrame): The input DataFrame (assumed to be already date-filtered).

    Returns:
        tuple: A tuple containing the average review score and the review score distribution.
               Returns (0, empty Series) if required columns are not found or no relevant data.
    """
    # Periksa kolom yang dibutuhkan
    if 'review_score' not in df.columns:
        print("Error: Required column 'review_score' not found for satisfaction analysis.")
        return 0, pd.Series(dtype='int64')

    # Filter data untuk review score yang tidak NaN
    df_reviews = df[df['review_score'].notna()].copy() # Use copy()

    # Periksa apakah ada data review setelah filtering NaN
    if df_reviews.empty:
        print("Info: No valid review data available in the provided DataFrame.")
        return 0, pd.Series(dtype='int64') # Kembalikan 0 dan Series kosong jika tidak ada data review

    # Hitung rata-rata review score
    average_score = df_reviews['review_score'].mean()

    # Hitung distribusi review score
    score_distribution = df_reviews['review_score'].value_counts().sort_index()

    return average_score, score_distribution


def analyze_monthly_orders(df):
    """
    Analyzes the number of orders per month for the provided data.

    Args:
        df (pandas.DataFrame): The input DataFrame (assumed to be already date-filtered).

    Returns:
        pandas.Series: A Series containing the number of orders per month, indexed by 'YYYY-MM'.
                    Returns None if the 'order_purchase_timestamp' column is not found or not datetime,
                    or an empty Series if no data after filtering.
    """
    if 'order_purchase_timestamp' not in df.columns:
        print("Error: Column 'order_purchase_timestamp' not found for monthly order analysis.")
        return None

    # Check if order_purchase_timestamp is datetime (should be handled in load_data)
    if not pd.api.types.is_datetime64_any_dtype(df['order_purchase_timestamp']):
         print("Error: 'order_purchase_timestamp' column is not datetime type. Cannot perform monthly analysis.")
         return None

    # Handle missing values in relevant columns
    df_monthly_orders = df.dropna(subset=['order_purchase_timestamp']).copy() # Use copy()

    if df_monthly_orders.empty:
        print("Info: No valid timestamp data found in the provided DataFrame.")
        return pd.Series(dtype=int) # Return empty Series if no valid data

    # Resample by month and count the number of orders
    monthly_orders = df_monthly_orders.set_index('order_purchase_timestamp').resample('M').size()

    # Format the index
    monthly_orders.index = monthly_orders.index.strftime('%Y-%m')
    return monthly_orders