import pdfplumber
import csv
import re

# Path to your PDF file
pdf_path = '/home/wntrb0y/Desktop/PNC_Statements_2024/Statement_Apr_12_2024.pdf'
csv_path = '/home/wntrb0y/Desktop/PNC Statement Parser/APR_transactions.csv'

# Function to extract transactions
def extract_transactions(text):
    lines = text.split("\n")
    transactions = []
    capture = False

    for line in lines:
        # Start capturing after the "Activity Detail" section
        if "Activity Detail" in line:
            capture = True
            continue
        if capture:
            # Ignore header and empty lines
            if "Date" in line and "Amount" in line and "Description" in line:  # Transaction header
                continue
            elif line.strip() == "":  # Empty lines
                continue
            else:
                # Use regex to match the expected transaction line format
                match = re.match(r'(\d{1,2}/\d{1,2})\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(.*)', line)
                if match:
                    date, amount, description = match.groups()
                    # Clean up the amount to ensure it only contains digits and decimal point
                    amount = amount.replace(',', '').strip()
                    transactions.append([date, amount, description])
                else:
                    # Check if the line starts with a date
                    if re.match(r'^\d{1,2}/\d{1,2}', line):
                        # Try to extract a line that may have been misformatted
                        parts = line.split(maxsplit=2)
                        if len(parts) >= 3:
                            date = parts[0] + " " + parts[1]  # Combining potential date components
                            amount = parts[2] if len(parts) > 2 else ''
                            description = ' '.join(parts[3:]) if len(parts) > 3 else ''
                            transactions.append([date, amount, description])
    
    return transactions

# Open the PDF and extract text
with pdfplumber.open(pdf_path) as pdf:
    # Extract text from all pages
    all_text = ""
    for page in pdf.pages:
        all_text += page.extract_text()

# Extract transactions
transactions = extract_transactions(all_text)

# Write transactions to CSV
with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Date', 'Amount', 'Description'])  # Header
    writer.writerows(transactions)

print(f"Transactions have been saved to {csv_path}")
