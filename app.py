from flask import Flask, render_template
from cs_stats import get_cleansheet_data
import pandas as pd

app=Flask(__name__)

@app.route('/')
def home():
    cleansheet_data = get_cleansheet_data()
    cleansheet_data = cleansheet_data.to_html(classes='dataframe', index=False)

    return render_template('index.html', cleansheet_data=cleansheet_data)

@app.route("/price_change")
def price_change():
    return render_template("price_change.html")

if __name__ == '__main__':
    app.run(debug=True)