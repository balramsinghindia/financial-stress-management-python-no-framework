# Data Preparation and Feature Engineering
import pandas as pd
from datetime import datetime

from sklearn.tree import export_text

# Function to parse date strings like "31-Oct" to datetime objects
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d %b")
    except ValueError:
        # Handle exception if format doesn't match, or provide fallback logic
        return None

# Function for feature engineering or data preparation
def prepare_data(csv_file):
    # Read CSV into pandas DataFrame
    df = pd.read_csv(csv_file)

    # Parse dates using the parse_date function
    df['Date'] = df['Date'].apply(parse_date)

    # Remove dollar signs and commas, then convert Amount to numeric
    df['Amount'] = df['Amount'].str.replace('$', '').str.replace(',', '')
    df['Amount'] = pd.to_numeric(df['Amount'])

    # Convert amounts to negative for debits
    df.loc[df['Transaction Type'] == 'Debit', 'Amount'] *= -1

    # Example feature engineering: Extract month and day as additional features
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day

    return df

csv_file = 'csv_statements_output/bank_statement.csv'
data = prepare_data(csv_file)

# Group by month and year
monthly_data = data.groupby(data['Date'].dt.to_period('M')).agg(
    income=('Amount', lambda x: x[x > 0].sum()),
    expenses=('Amount', lambda x: x[x < 0].sum()),
    balance=('Balance', 'last')
).reset_index()

# Calculate financial ratios
monthly_data['savings'] = monthly_data['income'] + monthly_data['expenses']
monthly_data['expense_ratio'] = monthly_data['expenses'] / monthly_data['income']

# Label data for financial stress
def label_stress(row):
    balance = float(row['balance'].replace('$', '').replace(',', ''))
    if balance < 0 or row['expense_ratio'] > 0.8:
        return 1
    return 0

monthly_data['financial_stress'] = monthly_data.apply(label_stress, axis=1)

print(monthly_data)

# Export the processed data to a new CSV file
output_csv_file = 'processed/processed_bank_statement.csv'
monthly_data.to_csv(output_csv_file, index=False)

print(f"Processed data has been exported to {output_csv_file}")
