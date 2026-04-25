import mysql.connector
from private_keys import db_user,db_password
import pandas as pd



# Startup creation of the DB
def Create_DB():
  mydb = mysql.connector.connect(
      host="localhost",
      port=8013,
      user=db_user,
      password=db_password
  )
  mycursor = mydb.cursor()
  mycursor.execute("CREATE DATABASE IF NOT EXISTS expenses_db")
  mydb.commit()
  mydb.close()

# connects to DB
def connect_db(db=None):
  return mysql.connector.connect(
        host="localhost",
        port=8013,
        user=db_user,
        password=db_password,
        database=db
  )

# Startup creation of the merchant table
def Create_Merchant_Table():
  Expenses_Tracker_DB=connect_db("expenses_db")
  mycursor = Expenses_Tracker_DB.cursor()

  mycursor.execute("""
  CREATE TABLE IF NOT EXISTS merchants(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(255)
  )
  """)
  Expenses_Tracker_DB.commit()
  Expenses_Tracker_DB.close()

# Startup Creation of spending table
def Create_Spending_Table():
  Expenses_Tracker_DB=connect_db("expenses_db")
  mycursor = Expenses_Tracker_DB.cursor()

  mycursor.execute("""
  CREATE TABLE IF NOT EXISTS spending (
      id INT AUTO_INCREMENT PRIMARY KEY,
      card_number VARCHAR(255),
      date DATE,
      amount FLOAT,
      merchant VARCHAR(255),
      category VARCHAR(255)
  )
  """)
  Expenses_Tracker_DB.commit()
  Expenses_Tracker_DB.close()

# Adds a merchant to the merchants table
def insert_merchant(name,category):
  Expenses_Tracker_DB=connect_db("expenses_db")
  mycursor = Expenses_Tracker_DB.cursor()
  sql = "INSERT INTO merchants (name, category) VALUES (%s, %s)"
  val = (name, category)
  mycursor.execute(sql, val)
  Expenses_Tracker_DB.commit()
  Expenses_Tracker_DB.close()

# Checks if a merchant is already listed in the merchants table
def merchant_checker(merchant_list):
  Expenses_Tracker_DB=connect_db("expenses_db")
  mycursor = Expenses_Tracker_DB.cursor()
  mycursor.execute("SELECT name FROM merchants")
  myresult = mycursor.fetchall()

  existing_merchants = {
        row[0].strip().lower() for row in myresult if row[0] is not None
    }

  missing_merchants = [
        m for m in merchant_list
        if m.strip().lower() not in existing_merchants
  ]

  Expenses_Tracker_DB.close()
  return missing_merchants

# Prints out any existing table
def print_table(table_name):
    Expenses_Tracker_DB = connect_db("expenses_db")
    cursor = Expenses_Tracker_DB.cursor()

    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()

    column_names = [desc[0] for desc in cursor.description]
    print(" | ".join(column_names))
    print("-" * 50)

    for row in rows:
        print(" | ".join(str(value) for value in row))

    Expenses_Tracker_DB.close()

# Takes the spending table and merchants table and updates their categories to fit the merchant based on the merchant table
def update_spending_categories():
  Expenses_Tracker_DB = connect_db("expenses_db")
  mycursor = Expenses_Tracker_DB.cursor()

  mycursor.execute("""
  UPDATE spending s
  JOIN merchants m
      ON s.merchant = m.name
  SET s.category = m.category
  """)

  Expenses_Tracker_DB.commit()
  Expenses_Tracker_DB.close()

import pandas as pd

# Takes a Dataframe and adds it to the spending table. (made for the expenses_df)
def insert_spending(expense_df):
    Expenses_Tracker_DB = connect_db("expenses_db")
    cursor = Expenses_Tracker_DB.cursor()

    # Ensure date is in correct format for MySQL
    df = expense_df.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Insert query
    insert_query = """
        INSERT INTO spending (card_number, date, amount, merchant, category)
        VALUES (%s, %s, %s, %s, %s)
    """

    # Prepare data
    data = [
        (
            row["Card"],
            row["Date"],
            row["Amount"],
            row["Merchant"],
            row.get("category", None)
        )
        for _, row in df.iterrows()
    ]

    # Execute batch insert
    cursor.executemany(insert_query, data)

    # Commit + cleanup
    Expenses_Tracker_DB.commit()
    cursor.close()
    Expenses_Tracker_DB.close()