# 💸 Expenses Tracker

Imports spending data from Google Sheets and categorizes your spending.

> ⚠️ Work in Progress — actively being developed

---

## 📌 Overview

AI Spending Analyzer is a Python desktop application designed to simplify personal finance tracking by automatically organizing expenses into categories such as:

- Groceries
- Utilities
- Entertainment
- Transportation
- Shopping
- Subscriptions
- Income
- Miscellaneous

The application pulls transaction data directly from Google Sheets and uses AI-assisted categorization to reduce manual budgeting work.

---

## ✨ Current Features

### ✅ Implemented
- Google Sheets integration
- Link reformatted for CSV
- AI categorization of businesses
- Merchant categories are editable (in case of misclassification by AI)
- Terminal based interactions

### 🚧 In Development
- Budget functionality
- Visualization of spending
- GUI

---

## 🧠 The Idea

User gives link to the app and it turns the sheet into a table with the format

| ID | card_number | date | amount | merchant | category |
|---|---|---|---|---|---|
| INT AUTO_INCREMENT PRIMARY KEY | VARCHAR(255) | DATE | FLOAT | VARCHAR(255) | VARCHAR(255) |

It then sends each uncategorized unique merchant to Open AI API to return a json of the merchant and category. Those are then added to an SQL table with the format

| ID | name Category | category |
|---|---|---|
| INT AUTO_INCREMENT PRIMARY KEY | VARCHAR(255) | VARCHAR(255) |

Using the merchant table, the main spending table is updated. The merchant table can be modified via terminal to resolve incorrect categorizations.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Pandas | Data processing |
| MySQL | Local storage |
| OpenAI API / Open Router | AI categorization of merchants |
| Flask | GUI |
| Javascript | html logic |

---
