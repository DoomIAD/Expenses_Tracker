import pandas as pd

#import Google Sheet
sheets_url = "https://docs.google.com/spreadsheets/d/1xQm23782yNJ4Ak_QZ5WUfxFqqFPM_aGST-B5ic8dRdM/export?format=csv&gid=0"
df = pd.read_csv(sheets_url)

# Fix data types
df['Date'] = pd.to_datetime(df['Date'])
df['Amount'] = df['Amount'].astype(int)

# Seperate data
filter_ = df['Amount'] >= 0
income_df = df[filter_]
filter_ = df['Amount'] < 0
expense_df = df[filter_]

# Catagorize Data

