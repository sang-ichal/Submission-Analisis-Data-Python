import pandas as pd


def load_data(filepath):
    """
    Loads data CSV file and converts specified date columns to datetime format.
    """
    try:
        # membaca data dari file CSV
        # Menggunakan encoding 'ISO-8859-1' untuk menghindari error
        # pada karakter tertentu
        df = pd.read_csv(filepath)

        # Kolom tanggal yang perlu diubah menjadi  datetime format
        date_columns = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "review_creation_date",
            "review_answer_timestamp",
            "shipping_limit_date",
        ]

        # Convert specified columns to datetime
        for col in date_columns:
            if col in df.columns:  # Check if column exists
                df[col] = pd.to_datetime(df[col], errors="coerce")
            else:
                print(
                    f"Warning: Date column '{col}' not found in the dataset."
                )

        return df
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def analyze_product_sales(df, top_n=10):
    """
    Analisis penjualan produk berdasarkan kategori untuk data yang diberikan.
    """
    if (
        "product_category_name_english" not in df.columns
        or "price" not in df.columns
    ):
        print(
            (
                "Error: Required columns 'product_category_name_english' "
                "or 'price' not found."
            )
        )
        return None, None

    # Menangani missing values dalam kolom yang relevan
    df_product_sales = df.dropna(
        subset=["product_category_name_english", "price"]
    ).copy()  # Use copy()

    if df_product_sales.empty:
        print(
            "Info: No valid product sales data found in the provided "
            "DataFrame."
        )
        return pd.Series(dtype=float), pd.Series(dtype=float)

    # Kalkulasi total penjualan per kategori produk
    # Menggunakan groupby untuk mengelompokkan berdasarkan kategori produk
    product_sales = (
        df_product_sales.groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
    )  # Sort descending for top

    top_selling = product_sales.head(top_n)
    bottom_selling = product_sales.tail(
        top_n
    )  # Get the last N after sorting descending

    return top_selling, bottom_selling


def analyze_customer_satisfaction(df):
    """
    Analisis kepuasan pelanggan berdasarkan review score
    untuk data yang diberikan.
    """
    # Periksa kolom yang dibutuhkan
    if "review_score" not in df.columns:
        print(
            "Error: Required column 'review_score' not found for "
            "satisfaction analysis."
        )
        return 0, pd.Series(dtype="int64")

    # Filter data untuk review score yang tidak missing value
    df_reviews = df[df["review_score"].notna()].copy()  # Use copy()

    # Periksa apakah ada data review setelah filtering missing values
    if df_reviews.empty:
        print(
            "Info: No valid review data available in the provided DataFrame."
        )
        return 0, pd.Series(
            dtype="int64"
        )  # Kembalikan 0 dan Series kosong jika tidak ada data review

    # Hitung rata-rata review score
    average_score = df_reviews["review_score"].mean()

    # Hitung distribusi review score
    score_distribution = df_reviews["review_score"].value_counts().sort_index()

    return average_score, score_distribution


def analyze_monthly_orders(df):
    """
    Analisis jumlah pesanan bulanan berdasarkan timestamp
    untuk data yang diberikan.
    """
    if "order_purchase_timestamp" not in df.columns:
        print(
            (
                "Error: Column 'order_purchase_timestamp' not found for "
                "monthly order analysis."
            )
        )
        return None

    # Cek kembali jika kolom 'order_purchase_timestamp' adalah tipe datetime
    if not pd.api.types.is_datetime64_any_dtype(
        df["order_purchase_timestamp"]
    ):
        print(
            "Error: 'order_purchase_timestamp' column is not datetime type. "
            "Cannot perform monthly analysis."
        )
        return None

    # Menangani missing values dalam kolom yang relevan
    df_monthly_orders = df.dropna(
        subset=["order_purchase_timestamp"]
    ).copy()  # Use copy()

    if df_monthly_orders.empty:
        print("Info: No valid timestamp data found in the provided DataFrame.")
        return pd.Series(dtype=int)  # Return empty Series if no valid data

    # Resample data untuk menghitung jumlah pesanan per bulan
    monthly_orders = (
        df_monthly_orders.set_index("order_purchase_timestamp")
        .resample("M")
        .size()
    )

    # Format the index
    monthly_orders.index = monthly_orders.index.strftime("%Y-%m")
    return monthly_orders
