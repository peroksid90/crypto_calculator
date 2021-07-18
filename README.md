# crypto_calculator

Register to https://www.quandl.com to obtain API_KEY and use it for enviroment variable QUANDL_API_KEY

    pip install pandas
    pip install bokeh

    QUANDL_API_KEY=YOUR_API_KEY bokeh serve /path/to/crypto_calculator_dir/

then open in a browser
http://localhost:5006/crypto_calculator


![Alt text](demo.png?raw=true "Demo")

**Cummulative** - is a sum of each mining profit for all elapsed days.

**Equipment cost** is used as a long position in BTC.
For example:
You start date 01.01.2020 and Equipment cost is 2500$.
The program take a BTC price for the date: 01.01.2020, say it 30000 $.
It calculate a hold position as:
hold = 2500 / 30000
hold = 0.0833 BTC

And then this position(0.0833) is recalculated on each point of the chart according to the current market BTC price.


**The left axis** is used for hold and cummulative. So you can compare what is better - spend money(Equipment cost) to buy a miner and mine, or just spend in to buy BTC and hold.

**Contribution are welcome!**

## TODO

Add mining pool fee calculation

Add transaction earnings (FPPS)
