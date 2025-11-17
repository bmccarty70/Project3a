import requests, webbrowser, sys
import pygal
from datetime import datetime
from pathlib import Path

API_KEY = "CQTGP3IZCHMSUM53"

def main():
    print("Stock Data Visualizer")
    print("---------------------\n")
    symbol = input("Enter the stock symbol you are looking for: ").strip().upper()

    print("\nChart Types")
    print("------------")
    print("1. Bar")
    print("2. Line")
    chart_pick = input("\nEnter the chart type you want (1, 2): ").strip()

    print("\nSelect the Time Series of the chart you want to Generate")
    print("---------------------------------------------------------")
    print("1. Intraday")
    print("2. Daily")
    print("3. Weekly")
    print("4. Monthly")
    series_pick = input("\nEnter the seires option (1, 2, 3, 4): ").strip()

    begin_str = input("\nEnter the start Date (YYYY-MM-DD): ").strip()
    end_str   = input("Enter the end Date (YYYY-MM-DD): ").strip()

    if not symbol or chart_pick not in ("1","2") or series_pick not in ("1","2","3","4"):
        print("Input error"); sys.exit(1)
    try:
        begin_date = datetime.strptime(begin_str, "%Y-%m-%d").date()
        end_date   = datetime.strptime(end_str,   "%Y-%m-%d").date()
    except:
        print("Dates must be YYYY-MM-DD."); sys.exit(1)
    if end_date < begin_date:
        print("End date cannot be before the begin date."); sys.exit(1)

    return symbol, chart_pick, series_pick, begin_date, end_date

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
    html = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>{symbol} Chart</title></head>
<body style="font-family:Arial; padding:16px;">
  <h2 style="margin:0 0 8px;">{symbol} — {label}</h2>
  <div style="color:#555;margin-bottom:12px;">Range: {start_date} → {end_date}</div>
  <object type="image/svg+xml" data="{data_uri}" style="width:95%; height:75vh;"></object>
</body>
</html>"""
    from pathlib import Path
    out = Path("chart.html").resolve()
    out.write_text(html, encoding="utf-8")
    webbrowser.open(out.as_uri())

while True:
    symbol, chart_pick, series_pick, begin_date, end_date = main()
    fetch_plot(symbol, chart_pick, series_pick, begin_date, end_date)
    again = input("\nDo you want to continue? (y/n): ")
    if again.lower() != "y":
        break