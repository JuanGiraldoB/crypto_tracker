from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from json import dumps

# Others
from datetime import date, datetime

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
            'open', flat=True).filter(symbol_id=symbol_id[0]["id"])[::1]
        price_date = PriceData.objects.select_related('symbol').values_list(
            'date', flat=True).filter(symbol_id=symbol_id[0]["id"])[::1]

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

        symbol, price_data, price_date = self.chart_data()
        context = {'symbol': symbol,
                   'price': price_data,
                   'date': price_date
                   }
        dataJSON = dumps(context, default=self.json_serial)

        return render(request, 'tracker/chart.html', {'data': dataJSON})
