# Django Stuffs
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponse
from django.urls import reverse

# Others
from json import dumps
from datetime import date, datetime
from services.scripts.backtesting_services import get_symbol_data
import matplotlib.pyplot as plt
import io
import urllib
import base64
import time

# Models
from tracker.models import Symbol, PriceData

# Create your views here.


class SymbolListView(ListView):
    model = Symbol


class SymbolDetailView(LoginRequiredMixin, DetailView):
    model = Symbol
    #template_name = "tracker/symbol_detail.html"


class Chart(View):
    template_name = 'tracker/chart.html'

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    # References
    # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable

    def chart_data(self, symbol="BTCUSDT", interval="4H"):
        df = get_symbol_data(symbol, interval)
        return df

    def convert_df_to_list(self, df):
        price_data = df['Open'].tolist()
        price_date = df.index.tolist()

        return price_data, price_date

    def get(self, request):
        if request.GET:
            symbol = request.GET.get('symbol')
            interval = request.GET.get('interval')

            df = self.chart_data(symbol, interval)
            price_data, price_date = self.convert_df_to_list(df)

            return JsonResponse({
                'symbol': symbol,
                'price': price_data,
                'date': price_date
            })

        df = self.chart_data()
        price_data, price_date = self.convert_df_to_list(df)

        context = {'symbol': "BTCUSDT",
                   'price': price_data,
                   'date': price_date
                   }

        dataJSON = dumps(context, default=self.json_serial)

        return render(request, self.template_name, {'data': dataJSON})

'''
def plot_test(request):
    start = time.time()
    plt.plot(range(10))
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    end = time.time()
    print("took", end - start)
    return render(request, 'tracker/plot_test.html', {'data': uri})'''
