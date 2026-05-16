from flask import Flask, render_template, request, redirect, session, url_for
from scripts.sheet_importer import sheet_import
from scripts.database_logic import *
from scripts.private_keys import flask_secret_key
import matplotlib
matplotlib.use("Agg") # Fixes thread error
import matplotlib.pyplot as plt
import io
import base64
import uuid
import pandas as pd

# Lets me store and use data between routes
IMPORT_STORE = {}

app = Flask(__name__)
app.secret_key = flask_secret_key
# Home Page
@app.route('/')
def home():
    return render_template("home.html")

# New Google Sheet
@app.route("/add_spreadsheet", methods=["GET", "POST"])
def add_spreadsheet():
    # Initialize variables for template rendering
    success = request.args.get("success") == "1"
    failure = False
    spending_collumn = []
    spending_row = []
    checked = False

    # Pulls the last preview from the temporary store
    preview = IMPORT_STORE.get("last_preview", {})
    if preview:
        spending_collumn = preview.get("spending_collumn", [])
        spending_row = preview.get("spending_row", [])

    if request.method == "POST":
        sheet_url = request.form.get("url", "")

        # Uses action to determine current step of the import process
        action = request.form.get("action", "import")
        if action == "import":
            sheet_url = request.form.get("url", "")
            try:
                spending_collumn, spending_row, incoming_merchants, expense_df = sheet_import(sheet_url)

                # Save preview
                IMPORT_STORE["last_preview"] = {
                    "spending_collumn": spending_collumn,
                    "spending_row": spending_row,
                    "expense_df": expense_df,
                    "success": True,
                    "checked": False,
                }

                # Save the current import session data with a unique ID
                import_id = str(uuid.uuid4())
                IMPORT_STORE[import_id] = {
                    "incoming_merchants": incoming_merchants,
                    "spending_collumn": spending_collumn,
                    "spending_row": spending_row,
                    "expense_df": expense_df,
                    "checked": False,
                }
                success = True

                # Skips merchant review if there are no new merchants to review, otherwise goes to merchant review page
                if len(incoming_merchants) > 0:
                    return redirect(url_for("import_merchants", import_id=import_id))
                else:
                    IMPORT_STORE[import_id]["checked"] = True
                    IMPORT_STORE["last_preview"]["checked"] = True

            except Exception as e:
                print(f"Error:{e} during sheet import")
                failure = True

        # If the user has already imported and reviewed merchants, apply the changes to the database
        else:
            preview = IMPORT_STORE.get("last_preview", {})

            spending_row = preview.get("spending_row", [])
            spending_collumn = preview.get("spending_collumn", [])
            expense_df = pd.DataFrame(spending_row, columns=spending_collumn)
            insert_spending(expense_df)
            update_spending_categories()
            print_table("spending")

            # Wipe for next import 
            IMPORT_STORE.clear()
            return redirect(url_for("add_spreadsheet", success=1))

    # Starts 'er up
    return render_template(
        "add_spreadsheet.html",
        spending_collumn=spending_collumn,
        spending_row=spending_row,
        success=success,
        failure=failure
    )

# Removes rows from the add_spreadsheet table
@app.route("/remove_spending_row/<int:index>", methods=["POST"])
def remove_spending_row(index):
    preview = IMPORT_STORE.get("last_preview")

    if not preview:
        return redirect(url_for("add_spreadsheet"))

    rows = preview.get("spending_row", [])

    if 0 <= index < len(rows):
        rows.pop(index)

        # Update preview
        preview["spending_row"] = rows
        IMPORT_STORE["last_preview"] = preview

        # Updates any active import session with the new rows
        for key, value in IMPORT_STORE.items():
            if isinstance(value, dict):
                if value.get("spending_row") is not None:
                    value["spending_row"] = rows

    return redirect(url_for("add_spreadsheet"))

# Check incoming merchants before updating the Merchant table
@app.route('/import_merchants/<import_id>', methods=["GET", "POST"])
def import_merchants(import_id):
    success = False
    failure = False

    # Pull the import data from the temporary store using the import ID
    import_data = IMPORT_STORE.get(import_id)
    if not import_data:
        return "Import session expired or invalid", 404
    incoming_merchants = import_data["incoming_merchants"]

    # Takes the input of the dropdowns and updates the Merchant table, then updates the Spending table with the new categories
    if request.method == "POST":
        try:
            for merchant, category in request.form.items():
                print(f"Adding merchant: {merchant} to category: {category}")
                insert_merchant(merchant, category)
            update_spending_categories()

            success = True

            # Go back to the spreadsheet preview page
            return redirect(url_for("add_spreadsheet"))
        
        except Exception as e:
            print(f"Error: {e} on merchant: {merchant} with category: {category} ||| import_merchants()")
            failure = True

    
    # Start 'er up
    return render_template(
        #Uses same HTML, just different values
        "edit_merchants.html",
        # Gives incoming merchants from sheet_import() to the html for approval
        merchant_table=incoming_merchants,
        success=success,
        failure=failure
    )

# Modify Merchants
@app.route('/edit_merchants', methods=["GET", "POST"])
def edit_merchants():
    success = False
    failure = False

    # Takes the input of the dropdowns
    if request.method == "POST":
        try:
            for merchant, category in request.form.items():
                update_merchant(merchant, category)
            success = True
        except Exception as e:
            print(f"Error: {e} on merchant: {merchant} with category: {category}")
            failure = True


    # Passes the merchant table as a variable to the html
    # print_table("merchants")
    merchant_table = export_merchant_table()
    print_table("merchants")
    
    # Start 'er up
    return render_template(
        "edit_merchants.html",
        merchant_table=merchant_table,
        success=success,
        failure=failure
    )

# Spending visualizations
@app.route('/expenditures')
def expenditures():
    # Ensures data is clean before taking action
    remove_duplicates()

    # Passes the merchant table as a variable to the html
    # print_table("merchants")
    merchant_table = export_merchant_table()
    
    # Export total sums of individual categories
    categories_total = category_total()

    # Empty lists to store for pie chart
    categories_list=[]
    total_list=[]


    for i in range(len(categories_total)):
        category,total=categories_total[i]
        categories_list.append(category)
        total_list.append(round(abs(total),2))
    categories_total = list(zip(categories_list, total_list))
    categories_total.sort(key=lambda x: x[1], reverse=True)


    # Create pie chart
    fig, ax = plt.subplots()
    ax.pie(
        total_list,
        labels=categories_list,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.axis("equal")
    ax.set_title("Spending")

    # Make it a usable image for html
    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    pie_chart = base64.b64encode(img.getvalue()).decode("utf-8")
    plt.close(fig)

    print_table("spending")


    # Start 'er up
    return render_template(
        "expenditures.html",
        categories_total=categories_total,
        pie_chart=pie_chart,
    )

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)