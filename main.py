from scripts.sheet_importer import *

user_action=input("What would you like to do today? (please input the number)\n1. upload Google Sheet link\n2. Modify category DB\n")
if user_action=="1":
    sheet_url=input("Please input the URL for the google sheet:\n")
    sheet_import(sheet_url)
elif user_action=="2":
    print("Current catorgorized vendors:\n")
    print_table("merchants")
    vendor=input("\n=======================\nWho is the vendor?\n")
    category=input("\nCategories: groceries, restaurant, transport, shopping, entertainment, utilities, subscriptions, health, travel, other\n")
    update_merchant(vendor,category)
    
    