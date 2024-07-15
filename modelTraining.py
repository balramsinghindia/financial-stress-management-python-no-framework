# Model Training
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pandas as pd
import pickle

df = pd.read_csv("processed/processed_bank_statement.csv")

# Define features and labels
features = df[['income', 'expenses', 'savings', 'expense_ratio']]
labels = df['financial_stress']

# Split data
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save the model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)