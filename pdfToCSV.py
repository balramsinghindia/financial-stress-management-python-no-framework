import PyPDF2
import pandas as pd
import re

def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def determine_transaction_type(line):
    # Count occurrences of '$' in the line
    dollar_count = line.count('$')

    # Determine transaction type based on '$' count
    if dollar_count > 1:
        return "Credit"
    else:
        return "Debit"

# def parse_text(text):
#     # Regular expressions to match dates, descriptions, and amounts
#     date_pattern = r"\d{2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"  # Adjust this pattern according to the date format in your PDF
#     amount_pattern = r"\$\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?(?:\sCR)?"  # Pattern for amounts like 123.45

#     # Split the text into lines
#     lines = text.splitlines()

#     transactions = []

#     # Parse each line
#     for i in range(len(lines)):
#         line = lines[i].strip()  # Remove leading and trailing whitespace

#         # Find all dates and amounts in the line
#         dates = re.findall(date_pattern, line)
#         amounts = re.findall(amount_pattern, line)
#         transaction_type = determine_transaction_type(line)

#         # Initialize amount as None
#         amount = None

#         # Determine transaction value (amount) based on transaction type
#         if transaction_type == "Credit":
#             # Credit transaction: amount is the amount immediately before the last '$'
#             amount_match = re.search(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?=\s*\$\d[\d,\.]+$)', line)
#             if amount_match:
#                 amount = amount_match.group(0)
#         elif transaction_type == "Debit":
#             # Debit transaction: amount is the value from the previous line
#             if i > 0:
#                 prev_line = lines[i - 1].strip()
#                 amount_match = re.search(r'\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?', prev_line)
#                 if amount_match:
#                     amount = amount_match.group(0)

#         # Example logic to extract description assuming it's the text between the date and amount
#         if dates and amounts:
#             date = dates[0]
#             amount = amounts[-1]
#             description = line.replace(date, "").replace(amount, "").strip()

#             # Initialize debit_value
#             debit_value = transaction_type if transaction_type else ""

#             transactions.append({
#                 "Date": date,
#                 "Description": description,
#                 "Balance": amount,
#                 "Transaction Type": debit_value,
#                 "amount": amount  # Add the extracted amount value to the transaction dictionary
#             })

#     return transactions 
def parse_text(text):
    # Regular expressions to match dates, descriptions, and amounts
    date_pattern = r"\d{2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"  # Adjust this pattern according to the date format in your PDF
    balance_pattern = r"\$\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?(?:\sCR)?"  # Pattern for amounts like 123.45

    # Split the text into lines
    lines = text.split("CR")

    transactions = []

    # Parse each line
    for line in lines:
        # Find all dates and amounts in the line
        dates = re.findall(date_pattern, line)
        balances = re.findall(balance_pattern, line)
        transaction_type = determine_transaction_type(line)

         # Initialize amount as None
        amount = None

         # Determine transaction value (amount) based on transaction type
        if transaction_type == "Credit":
            # Credit transaction: amount is the value before the last '$'
            amount_match = re.search(r'(\$\d[\d,\.]+)', line)
            if amount_match:
                amount = amount_match.group(1)
        elif transaction_type == "Debit":
            # Debit transaction: amount is the value between '(' and the last '$'
            amount_match = re.search(r'\((.*?)\$', line)
            if amount_match:
                amount = amount_match.group(1)

        # print("debit", line)
        # Example logic to extract description assuming it's the text between the date and amount
        if dates and balances:
            # print("yes")
            # print("line", line)
            date = dates[0]
            balance = balances[-1]
            # print("line", line)

            if transaction_type:
                debit_value = transaction_type
                print("debit", transaction_type)
                print("line", line)
            else:
                debit_value = ""
            description = line.replace(date, "").replace(balance, "").strip()            
            transactions.append({"Date": date, "Description": description, "Balance": balance, "Transaction Type": debit_value, "Amount": amount })        

    return transactions

def save_to_csv(transactions, csv_path):
    df = pd.DataFrame(transactions)
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    pdf_path = "./bank_statements/1May2022To31October2022.pdf"
    csv_path = "csv_statements_output/bank_statement.csv"

    text = extract_text_from_pdf(pdf_path)
    transactions = parse_text(text)

    save_to_csv(transactions, csv_path)

    print(f"CSV file saved to {csv_path}")
