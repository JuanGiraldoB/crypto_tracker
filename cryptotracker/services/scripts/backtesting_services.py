from datetime import timedelta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import pandas as pd

# Models
from tracker.models import Symbol, PriceData


class SmaCross(Strategy):
    n1 = 50
    n2 = 100

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        price = self.data.Close

        if crossover(self.sma1, self.sma2):
            sl = price - price * 0.03
            tp = price + price * 0.04
            self.buy(sl=sl, tp=tp)


def resampleOHLC(df, interval):
    df = df.resample(interval).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    })

    return df


def get_symbol_data(symbol, interval):
    symbol_id = Symbol.objects.filter(
        symbol=symbol).values_list('id', flat=True)[::1]

    qry = PriceData.objects.select_related('symbol').filter(
        symbol_id=symbol_id[0]).values_list("date", "open", "high", "low", "close")
    df = pd.DataFrame(
        qry, columns=["Date", "Open", "High", "Low", "Close"]).set_index("Date")

    df = resampleOHLC(df, interval)

    return df


def run_backtest(symbol, periods, df):
    returns = []

    strategy = SmaCross
    strategy.n1 = periods[0]
    strategy.n2 = periods[1]

    bt = Backtest(df, strategy, cash=30_000,
                  commission=0.0015, exclusive_orders=True)
    output = bt.run()
    x = bt.plot(
        filename="back_testing/templates/back_testing/plots/result_plot.html")
    returns.append(output['Return [%]'])

    result = pd.DataFrame(returns, index=[symbol], columns=['ret'])
    return result
