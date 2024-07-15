from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load your trained model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Function to parse date strings like "31-Oct" to datetime objects
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d %b")
    except ValueError:
        # Handle exception if format doesn't match, or provide fallback logic
        return None

@app.route('/')
def home():
    return "Welcome to the Financial Stress Prediction API!"

@app.route('/predict', methods=['POST'])
def predict():
    # Get JSON data from request
    data = request.get_json(force=True)
    
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Parse dates
    df['Date'] = df['Date'].apply(parse_date)

    # Process the data similar to your preparation steps
    df['Amount'] = df['Amount'].str.replace('$', '').str.replace(',', '')
    df['Amount'] = pd.to_numeric(df['Amount'])
    df.loc[df['Transaction Type'] == 'Debit', 'Amount'] *= -1

    # Extract month and day as additional features
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day

    # Group by month and year
    monthly_data = df.groupby(df['Date'].dt.to_period('M')).agg(
        income=('Amount', lambda x: x[x > 0].sum()),
        expenses=('Amount', lambda x: x[x < 0].sum()),
        balance=('Balance', 'last')
    ).reset_index()

    # Calculate financial ratios
    monthly_data['savings'] = monthly_data['income'] + monthly_data['expenses']
    monthly_data['expense_ratio'] = monthly_data['expenses'] / monthly_data['income']

    # Prepare the feature set for prediction
    features = monthly_data[['income', 'expenses', 'balance', 'savings', 'expense_ratio']]

    try:
        # Predict financial stress
        monthly_data['financial_stress'] = model.predict(features)

        # Return predictions
        return jsonify(monthly_data.to_dict(orient='records'))
    
    except ValueError as ve:
        return jsonify({'error': str(ve)})

if __name__ == '__main__':
    app.run(debug=True)
