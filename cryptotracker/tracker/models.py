from django.db import models

# Create your models here.

class Symbol(models.Model):
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.symbol

class PriceData(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    date = models.DateField()
    open = models.FloatField()
    high= models.FloatField() 
    low= models.FloatField()
    close= models.FloatField()
