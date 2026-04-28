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


def sheet_import(sheets_url):
    # Create my database
    Create_DB()
    Create_Merchant_Table()
    Create_Spending_Table()

    # import Google Sheet
    sheets_url=url_fixer(sheets_url)

    df = pd.read_csv(sheets_url)

    # Fix data types and clean data
    df['Date'] = pd.to_datetime(df['Date'])
    df['Amount'] = df['Amount'].str.replace(',', '').astype(float)
    df['Merchant'] = (
        df['Merchant']
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.strip()
        .str.lower()
    )

    # Seperate data
    filter_ = df['Amount'] < 0
    expense_df = df[filter_]

    # Add to the Spending DB
    insert_spending(expense_df)

    # Categorize expenses
    unique_merchants = expense_df["Merchant"].unique()
    missing_merchants=merchant_checker(unique_merchants)

    for i in missing_merchants:
        try:
            category = categorize_merchant(i)
            insert_merchant(i,category)
        except:
            print("Error for item:",i)

    update_spending_categories()
    print_table("spending")


