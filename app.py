import csv
from flask import Flask, render_template, request
import os
import requests
import pygal
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

API_KEY = "CQTGP3IZCHMSUM53"

def series_params(series_pick):
    if series_pick == "1":
        return ("TIME_SERIES_INTRADAY", "Time Series (60min)", {"interval":"60min","outputsize":"full"}, "Intraday (60min)")
    if series_pick == "2":
        return ("TIME_SERIES_DAILY", "Time Series (Daily)", {"outputsize":"full"}, "Daily")
    if series_pick == "3":
        return ("TIME_SERIES_WEEKLY", "Weekly Time Series", {}, "Weekly")
    return ("TIME_SERIES_MONTHLY", "Monthly Time Series", {}, "Monthly")


def fetch_plot(symbol, chart_type, series_type, start_date, end_date):
    func, key, extra, label = series_params(series_type)

    url = "https://www.alphavantage.co/query"
    params = {"function": func, "symbol": symbol, "apikey": API_KEY}
    params.update(extra)

    data = requests.get(url, params=params).json()
    time_series = data[key]

    dates = []
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []

    for date_text, values in time_series.items():
        try:
            date_value = datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S").date()
        except ValueError:
            date_value = datetime.strptime(date_text, "%Y-%m-%d").date()

        if start_date <= date_value <= end_date:
            dates.append(date_text)
            open_prices.append(float(values["1. open"]))
            high_prices.append(float(values["2. high"]))
            low_prices.append(float(values["3. low"]))
            close_prices.append(float(values["4. close"]))

    dates.reverse()
    open_prices.reverse()
    high_prices.reverse()
    low_prices.reverse()
    close_prices.reverse()

    chart = pygal.Bar() if chart_type == "1" else pygal.Line()
    chart.title = f"{symbol} Stock Prices ({label})"
    chart.x_labels = dates
    chart.add("Open", open_prices)
    chart.add("High", high_prices)
    chart.add("Low", low_prices)
    chart.add("Close", close_prices)

    data_uri = chart.render_data_uri()
    return data_uri

def load_symbols():
    symbols = []
    try:
        with open("stocks.csv", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    symbols.append(row[0].strip().upper())
    except Exception as e:
        print("Error loading CSV:", e)
    return symbols


STOCK_LIST = load_symbols()

# ===== FLASK ROUTE ======
@app.route("/", methods=["GET", "POST"])
def home():
    chart_data_uri = None       
    form_data = {}               

    if request.method == "POST":
        form_data["symbol"] = request.form.get("symbol", "")
        form_data["chart_type"] = request.form.get("chart_type", "")
        form_data["series_type"] = request.form.get("series_type", "")
        form_data["start_date"] = request.form.get("start_date", "")
        form_data["end_date"] = request.form.get("end_date", "")

    try:
        start = datetime.strptime(form_data["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(form_data["end_date"], "%Y-%m-%d").date()

        chart_data_uri = fetch_plot(
            form_data["symbol"],
            form_data["chart_type"],
            form_data["series_type"],
            start,
            end
        )

    except Exception as e:
        print("Error generating chart:", e)


    return render_template(
        "index.html",
        symbols=STOCK_LIST,
        form_data=form_data,
        chart_data_uri=chart_data_uri
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

