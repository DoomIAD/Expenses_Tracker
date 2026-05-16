import pandas as pd
import matplotlib.pyplot as plt

from scripts.private_keys import *
from scripts.ai_inquiry import *
from scripts.database_logic import *

def url_fixer(sheets_url_bad):
    found=False
    # Finds the GID
    for j in range(len(sheets_url_bad)):
        if sheets_url_bad[-j]=="=" and found:
            gid=sheets_url_bad[-j+1:end-4]
            break
        elif sheets_url_bad[-j]=="=":
            end=-j
            found=True

    # Removes extra url
    for i in range(len(sheets_url_bad)):
        if sheets_url_bad[-i]=="/":
            sheets_url_bad=sheets_url_bad[:-i]
            break

    # formats new correct URL
    sheets_url_good=f"{sheets_url_bad}/export?format=csv&gid={gid}"

    return sheets_url_good

def new_merchants_review(unique_merchants):
    missing_merchants=merchant_checker(unique_merchants)
    new_merchants = []
    print_table("merchants")
    print(f"\nMissing merchants found in the sheet:\n{missing_merchants}")
    for i in missing_merchants:
        try:
            category = categorize_merchant(i)
            # category = "other" # Skip over API to save time during tests
            new_merchants.append((i, category))
        except Exception as e:
            print("Error for item:", i, "->", e)

    return new_merchants

def sheet_import(sheets_url):
    # Create my database if not already existing
    Create_DB()
    Create_Merchant_Table()
    Create_Spending_Table()

    # import Google Sheet (with fixed URL)
    sheets_url=url_fixer(sheets_url)
    df = pd.read_csv(sheets_url)

    # Fix data types and clean data
    df['Date'] = df['Date'].astype(str).str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='mixed')
    df['Amount'] = df['Amount'].str.replace(',', '').astype(float)
    df['Merchant'] = (
        df['Merchant']
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.strip()
        .str.lower()
    )

    # Seperate data to only read expenses
    filter_ = df['Amount'] < 0
    expense_df = df.loc[filter_].copy()

    # Categorize expenses of new items and add to the Merchant DB if not already existing
    unique_merchants = expense_df["Merchant"].unique()
    incoming_merchants = new_merchants_review(unique_merchants)
    
    # Exports the Dataframe as a list
    columns = expense_df.columns.tolist()
    rows = expense_df.values.tolist()   

    # Prints added table items to console for Debugging
    print("\nIncoming table items:\n")
    print(" | ".join(columns))
    print("-" * 50)
    for row in rows:
        print(" | ".join(str(value) for value in row))

    # Returns the incoming items for approval
    return columns,rows,incoming_merchants, expense_df