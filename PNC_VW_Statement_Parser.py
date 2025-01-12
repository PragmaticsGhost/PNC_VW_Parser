import pdfplumber
import csv
import re

# Path to your PDF file
STATEMENT_FILE_NAME = 'statement_name.pdf'
pdf_path = f'path/to/statements/{STATEMENT_FILE_NAME}'
csv_path = 'path/to/output/csv/'

PNC_STATEMENT_SECTION_TITLES = {'Deposits and Other Additions', 'Banking/Debit Card Withdrawals and Purchases',
                                'Online and Electronic Banking Deductions', 'Daily Balance Detail'}
PNC_STATEMENT_SECTIONS_TO_IGNORE = {'Daily Balance Detail'}

def format_statement_name(filename):
    return filename.rsplit('.')[0]

def format_section_title(section_title):
    return re.sub(r'[/\s]', '_', section_title)

def append_transaction_by_section(current_section, transaction, transactions_by_section):
    section_transactions = transactions_by_section[current_section]
    section_transactions.append(transaction)
    transactions_by_section[current_section] = section_transactions

    # Function to extract transactions
def extract_transactions(text):
    lines = text.split("\n")
    transactions_by_section = {}
    capture = False
    current_section = ''

    for line in lines:
        # Start capturing after the "Activity Detail" section
        if "Activity Detail" in line:
            capture = True
            continue
        if capture:
            for section in PNC_STATEMENT_SECTION_TITLES:
                if section in line:
                    if section not in transactions_by_section:
                        transactions_by_section[section] = []
                    current_section = section
                    break
        if current_section in PNC_STATEMENT_SECTIONS_TO_IGNORE:
            transactions_by_section.pop(current_section, None)
            break
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
                transaction = [date, amount, description]
                append_transaction_by_section(current_section, transaction, transactions_by_section)
            else:
                # Check if the line starts with a date
                if re.match(r'^\d{1,2}/\d{1,2}', line):
                    # Try to extract a line that may have been misformatted
                    parts = line.split(maxsplit=2)
                    if len(parts) >= 3:
                        date = parts[0] + " " + parts[1]  # Combining potential date components
                        amount = parts[2] if len(parts) > 2 else ''
                        description = ' '.join(parts[3:]) if len(parts) > 3 else ''
                        transaction = [date, amount, description]
                        append_transaction_by_section(current_section, transaction, transactions_by_section)
    return transactions_by_section

# Open the PDF and extract text
with pdfplumber.open(pdf_path) as pdf:
    # Extract text from all pages
    all_text = ""
    for page in pdf.pages:
        all_text += page.extract_text()

# Extract transactions
transactions = extract_transactions(all_text)

# Write transactions to CSV
for section, section_transactions in transactions.items():
    formatted_statement_filename = format_statement_name(STATEMENT_FILE_NAME)
    output_file_name = f'{csv_path}{formatted_statement_filename}_{format_section_title(section)}.csv'
    with open(output_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Amount', 'Description'])  # Header
        writer.writerows(section_transactions)

print(f"Transaction files have been saved to {csv_path}")
