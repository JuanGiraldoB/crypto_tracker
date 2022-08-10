from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

#Models
from tracker.models import Symbol

# Create your views here.
class SymbolListView(ListView):
    model = Symbol

class SymbolDetailView(LoginRequiredMixin, DetailView):
    model = Symbol
    #template_name = "tracker/symbol_detail.html"