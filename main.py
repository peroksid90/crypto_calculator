from bokeh.layouts import column
from bokeh.models import Button, DateRangeSlider, Range1d, LinearAxis
from bokeh.plotting import figure, curdoc
from datetime import datetime, timedelta
from bokeh.models import TextInput, HoverTool
import pandas as pd
import os

QUANDL_API_KEY = os.environ['QUANDL_API_KEY']

difficulty_df = pd.read_csv(
    "https://www.quandl.com/api/v3/datasets/BCHAIN/DIFF.csv?api_key={API_KEY}".format(API_KEY=QUANDL_API_KEY),
    parse_dates=[0], index_col="Date")
btc_price_df = pd.read_csv(
    "https://www.quandl.com/api/v3/datasets/BCHAIN/MKPRU.csv?api_key={API_KEY}".format(API_KEY=QUANDL_API_KEY),
    parse_dates=[0], index_col="Date")


start_day = datetime(year=2018, month=1, day=1)
end_day = datetime.today() - timedelta(days=1)

date_range_slider = DateRangeSlider(value=(datetime(year=2020, month=2, day=15), end_day), start=start_day, end=end_day)
miner_hashrate = TextInput(value="110", title="Miner hashrate, TH/s")
electricity_per_kwh = TextInput(value="0.05", title="Electricity Cost, $/kWh")
power_consumption = TextInput(value="3250", title="Power, W")
equipment_cost = TextInput(value="2500", title="Equipment Cost, $")
pool_fee = TextInput(value="0", title="Pool fee, %. Example: 2.5% or 4%, etc.")

blank_fig = figure(width=1600, x_axis_type='datetime')

def block_reward_for(date_val):
    if date_val >= datetime(year=2020, month=5, day=11):
        return 6.25
    if date_val >= datetime(year=2016, month=7, day=9):
        return 12.5
    if date_val >= datetime(year=2012, month=11, day=28):
        return 25
    raise Exception("Too old date for block_reward_for: {}".format(date_val))


def calc_callback():
    start_day_val, end_day_val = date_range_slider.value

    start_day_val = datetime.fromtimestamp(start_day_val / 1000.0)
    end_day_val = datetime.fromtimestamp(end_day_val / 1000.0)

    target_date_range = pd.date_range(start=start_day_val, end=end_day_val)

    miner_hashrate_val = float(miner_hashrate.value) * pow(10, 12) #Convert TH/s to H/s

    power_consumption_kwh = float(power_consumption.value) / 1000.0 #Convert W to kW

    chart_data = {
        "date": [],
        "btc_price": [],
        "cumulative": [],
        "profit_per_day": [],
        "hold" : [],
    }

    cumulative_earn = 0

    start_day_str = start_day_val.strftime("%Y-%m-%d")
    buy_btc_price = btc_price_df["Value"][start_day_str]
    hold_btc = float(equipment_cost.value) / float(buy_btc_price)

    for day_val in target_date_range:
        current_reward = block_reward_for(day_val)

        day_str = day_val.strftime("%Y-%m-%d")
        current_difficulty = float(difficulty_df["Value"][day_str])
        current_btc_price = float(btc_price_df["Value"][day_str])

        bitcoin_per_day = (miner_hashrate_val * current_reward * (24 * 60 * 60)) / (current_difficulty * pow(2, 32))
        bitcoin_per_day_dollars = (bitcoin_per_day * current_btc_price) - (power_consumption_kwh * float(electricity_per_kwh.value) * 24)

        cumulative_earn += bitcoin_per_day_dollars

        chart_data["date"].append(day_val)
        chart_data["btc_price"].append(current_btc_price)
        chart_data["cumulative"].append(cumulative_earn)
        chart_data["profit_per_day"].append(bitcoin_per_day_dollars)
        chart_data["hold"].append(hold_btc * current_btc_price)

    cumulative_min, cumulative_max = min(chart_data["cumulative"]), max(chart_data["cumulative"])
    hold_min, hold_max = min(chart_data["hold"]), max(chart_data["hold"])
    range_min = min([cumulative_min, hold_min])
    range_max = max([cumulative_max, hold_max])
    p = figure(width=1600, x_axis_type='datetime', y_range=Range1d(start=range_min, end=range_max))
    p.add_tools(HoverTool(tooltips=[
        ("", '$name:$y{0.00} date:$x{%F}'),
    ], formatters={'$x': 'datetime'}))

    p.extra_y_ranges = {
        "btc_price": Range1d(start=min(chart_data["btc_price"]), end=max(chart_data["btc_price"]) + 1),
        "profit_per_day": Range1d(start=min(chart_data["profit_per_day"]), end=max(chart_data["profit_per_day"]) + 1),
    }
    p.add_layout(LinearAxis(y_range_name="btc_price"), 'right')
    p.add_layout(LinearAxis(y_range_name="profit_per_day"), 'right')

    p.line(x=chart_data["date"], y=chart_data["btc_price"], name="btc_price", legend_label="BTC price, $", y_range_name="btc_price", color="green")
    p.line(x=chart_data["date"], y=chart_data["profit_per_day"], name="profit_per_day", legend_label="Profit per day, $", y_range_name="profit_per_day", color="blue")

    p.line(x=chart_data["date"], y=chart_data["cumulative"], name="cumulative", legend_label="Cumulative profit, $", color="red")
    p.line(x=chart_data["date"], y=chart_data["hold"], name="hold", legend_label="Hold BTC, $", color="olive")

    p.left[0].formatter.use_scientific = False
    p.left[0].axis_label = "Hold BTC and Cumulative profit, $"

    p.right[0].formatter.use_scientific = False
    p.right[0].axis_label = "BTC price, $"

    p.right[1].formatter.use_scientific = False
    p.right[1].axis_label = "Profit per day, $"

    curdoc().roots[0].children[-1] = p
    print("END")

button = Button(label="Calc")
button.on_click(calc_callback)
curdoc().add_root(column(date_range_slider, miner_hashrate, electricity_per_kwh, power_consumption, equipment_cost, pool_fee, button, blank_fig))
