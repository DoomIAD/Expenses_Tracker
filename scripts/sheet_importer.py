import pandas as pd
import matplotlib.pyplot as plt

from private_keys import *
from ai_inquiry import *
from database_logic import *


# Create my database
Create_DB()
Create_Merchant_Table()
Create_Spending_Table()

# import Google Sheet
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



