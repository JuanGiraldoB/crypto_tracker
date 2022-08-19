from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from json import dumps
from django.http import HttpResponse
from django.urls import reverse

# Others
from datetime import date, datetime, timedelta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import pandas as pd


# Models
from tracker.models import Symbol, PriceData

# Create your views here.


class SymbolListView(ListView):
    model = Symbol


class SymbolDetailView(LoginRequiredMixin, DetailView):
    model = Symbol
    #template_name = "tracker/symbol_detail.html"


class Chart(View):

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    # References
    # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable

    def chart_data(self, symbol="BTCUSDT"):
        symbol_id = Symbol.objects.filter(symbol=symbol).values("id")
        price_data = PriceData.objects.select_related('symbol').values_list(
            'open', flat=True).filter(symbol_id=symbol_id[0]["id"])[:100:1]
        price_date = PriceData.objects.select_related('symbol').values_list(
            'date', flat=True).filter(symbol_id=symbol_id[0]["id"])[:100:1]

        return symbol, price_data, price_date

    def get(self, request):
        if request.GET:
            symbol, price_data, price_date = self.chart_data(
                request.GET.get('selector'))

            return JsonResponse({
                'symbol': symbol,
                'price': price_data,
                'date': price_date
            })
        print("da")
        symbol, price_data, price_date = self.chart_data()
        context = {'symbol': symbol,
                   'price': price_data,
                   'date': price_date
                   }
        dataJSON = dumps(context, default=self.json_serial)

        return render(request, 'tracker/chart.html', {'data': dataJSON})


class SmaCross(Strategy):
    n1 = 50
    n2 = 100

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)
        print("***********0*************")

    def next(self):
        # print("***********1*************")
        price = self.data.Close
        # print("***********2*************")

        if crossover(self.sma1, self.sma2):
            sl = price - price * 0.03
            tp = price + price * 0.04
            self.buy(sl=sl, tp=tp)
            # print("***********3*************")


def resampleOHLC(df, interval):
    df = df.resample(interval).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    })
    df = df.dropna()
    return df


def bts(request, interval):
    returns = []

    # Obtains symbols
    symbols = Symbol.objects.values_list('id', flat=True)[::1]
    # print(symbols)

    time_frame = pd.to_datetime('today') - timedelta(days=40)
    print(time_frame)
    for symbol in symbols:
        qry = PriceData.objects.select_related('symbol').filter(
            date__lt=time_frame, symbol_id=symbol).values_list("date", "open", "high", "low", "close")
        df = pd.DataFrame(
            qry, columns=["Date", "Open", "High", "Low", "Close"]).set_index("Date")
        df = resampleOHLC(df, "4H")
        print(len(df.index))
        bt = Backtest(df, SmaCross, cash=30000,
                      commission=0.0015, exclusive_orders=True)
        output = bt.run()
        returns.append(output['Return [%]'])

    frame = pd.DataFrame(returns, index=symbols, columns=['ret'])
    print(frame)
    return HttpResponse("hi")

    # return redirect(reverse("tracker:chart"))
