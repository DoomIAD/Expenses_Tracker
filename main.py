from flask import Flask, render_template, request, redirect, url_for
from scripts.sheet_importer import sheet_import
from scripts.database_logic import *
import matplotlib
matplotlib.use("Agg") # Fixes thread error
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return render_template("home.html")

# New Google Sheet
@app.route("/add_spreadsheet", methods=["GET", "POST"])
def add_spreadsheet():
    success,failure = False,False
    spending_collumn = []
    spending_row = []


    # Pulls the URL from the form to be used in sheet_import()
    if request.method == "POST":
        sheet_url = request.form["url"]
        try:
            spending_collumn,spending_row=sheet_import(sheet_url)
            success = True
        except Exception as e:
            print("Error:", e)
            failure = True

    # Tells the site if success or failure
    return render_template(
        "add_spreadsheet.html",
        spending_collumn=spending_collumn,
        spending_row=spending_row,
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
            print("Error:", e)
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