from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Others
from services.scripts.backtesting_services import run_backtest
from services.scripts.backtesting_services import get_symbol_data

# Create your views here.
class StrategyView(LoginRequiredMixin, View):
    template_name = 'back_testing/strategies_view.html'
    context = {}

    def get_backtesting_data(self, symbol, interval, periods): 
        df = get_symbol_data(symbol, interval)
        df = run_backtest(symbol, periods, df)
        return df

    def get(self, request):
        
        if request.GET:
            symbol = request.GET.get('symbol')
            interval = request.GET.get('interval')
            strategy = request.GET.get('strategy')

            if "100" in strategy:
                periods = [50, 100]
            else:
                periods = [20, 50]

            result = self.get_backtesting_data(symbol, interval, periods)
            self.context = {
                "symbol": symbol,
                "interval": interval,
                "strategy": strategy,
                "result": round(result.iloc[0]['ret'], 2),
            }

        return render(request, self.template_name, self.context)