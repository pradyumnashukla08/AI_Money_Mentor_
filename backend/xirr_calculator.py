import pandas as pd
from datetime import datetime
import pyxirr
import re
from portfolio_parser import extract_text_from_pdf

def create_mock_sip_data():
    # Mock data for a 12-month mutual fund SIP investment
    data = {
        'Date': [
            '2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', 
            '2023-05-01', '2023-06-01', '2023-07-01', '2023-08-01',
            '2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01',
            '2026-03-21'
        ],
        'Amount Invested': [
            -5000, -5000, -5000, -5000, 
            -5000, -5000, -5000, -5000,
            -5000, -5000, -5000, -5000,
            70000
        ]
    }
    
    # Create the pandas DataFrame
    df = pd.DataFrame(data)
    
    # Convert 'Date' column from strings to datetime objects
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df

def calculate_xirr_from_csv(csv_path, current_portfolio_value):
    """
    Reads a real CSV statement, appends the current value, and calculates XIRR.
    Assumes the CSV has 'Date' and 'Amount' columns.
    """
    print(f"\n--- Reading from CSV: {csv_path} ---")
    df = pd.read_csv(csv_path)
    
    # Ensure dates are datetime objects
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Append the current portfolio valuation for today
    today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
    current_value_row = pd.DataFrame([{'Date': today, 'Transaction Type': 'Current Value', 'Amount': current_portfolio_value}])
    
    # Concatenate the new row
    df = pd.concat([df, current_value_row], ignore_index=True)
    
    return calculate_and_print_xirr(df)

def calculate_xirr_from_pdf(pdf_path, current_portfolio_value):
    """
    Reads a real PDF statement, extracts text, uses regex to find transactions, and calculates XIRR.
    """
    print(f"\n--- Reading from PDF: {pdf_path} ---")
    raw_text = extract_text_from_pdf(pdf_path)
    
    # NOTE: You will need to write a custom Regular Expression (regex) here 
    # to find the specific dates and amounts in your broker's PDF text layout!
    # Example regex that looks for dates like DD-MM-YYYY and amounts:
    # pattern = r"(\d{2}-\d{2}-\d{4})\s+.*?\s+(-?\d+,\d+\.\d{2})"
    
    print("Raw text extracted successfully. Needs regex parsing to build DataFrame!")
    print("(Skipping calculation until regex is added based on your specific PDF layout.)\n")
    return None

def calculate_and_print_xirr(df):
    """Calculates and prints the final XIRR from a formatted DataFrame."""
    print(df.to_string(index=False))
    print("----------------------------\n")
    
    # Metrics
    total_invested = abs(df[df['Amount'] < 0]['Amount'].sum())
    current_value = df.iloc[-1]['Amount']
    
    print(f"Total Amount Invested: ${total_invested:,.2f}")
    print(f"Current Portfolio Value: ${current_value:,.2f}")
    
    # XIRR
    xirr_rate = pyxirr.xirr(df['Date'], df['Amount'])
    if xirr_rate is not None:
        print(f"\nCalculated XIRR: {xirr_rate * 100:.2f}%")
        return xirr_rate
    else:
        print("\nCould not calculate XIRR.")
        return None

if __name__ == "__main__":
    # 1. Example: Using the Mock Data
    print("Generating Mock Mutual Fund SIP Data...\n")
    sip_df = create_mock_sip_data()
    # Rename 'Amount Invested' to 'Amount' to generalize our calculation function
    sip_df.rename(columns={'Amount Invested': 'Amount'}, inplace=True)
    print("--- Mock Data Result ---")
    calculate_and_print_xirr(sip_df)
    
    # 2. Example: Using a Real CSV File
    # We will pass in a final portfolio value of 70,000
    calculate_xirr_from_csv('dummy_statement.csv', 70000)
    
    # 3. Example: Using a Real PDF File
    calculate_xirr_from_pdf('dummy.pdf', 70000)
