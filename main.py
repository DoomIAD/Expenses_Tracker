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
    success, failure = False, False
    spending_collumn = []
    spending_row = []
    checked=False

    # Pulls the last preview from the temporary store to show on the page if it exists
    preview = IMPORT_STORE.get("last_preview", {})
    if preview:
        spending_collumn = preview.get("spending_collumn", [])
        spending_row = preview.get("spending_row", [])
        success = preview.get("success", False)

    # Pulls the URL from the form to be used in sheet_import()
    if request.method == "POST":
        sheet_url = request.form["url"]
        checked = request.form.get("checked") == "true"
        if checked==False:
            try:
                spending_collumn,spending_row,incoming_merchants=sheet_import(sheet_url)
                
                # Save the last preview data in the temporary store for display on the page
                IMPORT_STORE["last_preview"] = {
                    "spending_collumn": spending_collumn,
                    "spending_row": spending_row,
                    "success": True,
                    "checked" : False,
                }

                # Save the incoming merchants and spending data in a temporary store for merchant review
                import_id = str(uuid.uuid4())
                IMPORT_STORE[import_id] = {
                    "incoming_merchants": incoming_merchants,
                    "spending_collumn": spending_collumn,
                    "spending_row": spending_row,
                    "checked" : False,
                }

                success = True

                # Redirect to the merchant if new merchants are found
                if len(incoming_merchants) > 0:
                    return redirect(url_for("import_merchants", import_id=import_id))
            
            except Exception as e:
                print(f"Error:{e} during sheet import")
                failure = True
        else:
            IMPORT_STORE.clear()
            return redirect(url_for("home"))

    # Start 'er up
    return render_template(
        "add_spreadsheet.html",
        spending_collumn=spending_collumn,
        spending_row=spending_row,
        success=success,
        failure=failure
    )

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

            # Remove the import data from the temporary store after processing
            IMPORT_STORE.pop(import_id, None)

            success = True
            # Go back to the add_spreadsheet page with a success message
            IMPORT_STORE[import_id]["checked"] = True
            return redirect(url_for("add_spreadsheet", imported="1"))
        
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
            update_spending_categories()
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