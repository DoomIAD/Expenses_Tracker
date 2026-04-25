import pandas as pd
import matplotlib.pyplot as plt

from private_keys import *
from ai_inquiry import *



# import Google Sheet
df = pd.read_csv(sheets_url)

# Fix data types
df['Date'] = pd.to_datetime(df['Date'])
df['Amount'] = df['Amount'].str.replace(',', '').astype(float)

# Seperate data
filter_ = df['Amount'] >= 0
income_df = df[filter_]
filter_ = df['Amount'] < 0
expense_df = df[filter_]

# Categorize expenses
unique_merchants = expense_df["Merchant"].unique()

merchant_map = {
    m: categorize_merchant(m)
    for m in unique_merchants
}

expense_df["category"] = expense_df["Merchant"].map(merchant_map)

print(expense_df)

# Pie Chart of Expenses
category_totals = (
    expense_df.groupby("category")["Amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
)

plt.figure(figsize=(9, 9))
plt.pie(
    category_totals,
    labels=category_totals.index,
    autopct=lambda p: f"{p:.1f}%\n(${p*category_totals.sum()/100:.0f})",
    startangle=140
)

plt.title("Monthly Expense Breakdown")
plt.axis("equal")
plt.show()