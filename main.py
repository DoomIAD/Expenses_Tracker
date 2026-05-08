from flask import Flask, render_template, request, redirect, url_for

from scripts.sheet_importer import sheet_import

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return render_template("home.html")

# New Google Sheet
@app.route("/add_spreadsheet", methods=["GET", "POST"])
def add_spreadsheet():
    success = False
    failure = False

    # Pulls the URL from the form to be used in sheet_import()
    if request.method == "POST":
        sheet_url = request.form["url"]
        try:
            sheet_import(sheet_url)
            success = True
        except Exception as e:
            print("Error:", e)
            failure = True

    # Tells the site if success or failure
    return render_template(
        "add_spreadsheet.html",
        success=success,
        failure=failure
    )


# Modify Merchants
@app.route('/edit_merchants')
def edit_merchants():
    return render_template("edit_merchants.html")

# Spending visualizations
@app.route('/about')
def about():
    return render_template("about.html")

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)