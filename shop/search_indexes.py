import datetime
from haystack import indexes
from .models import *

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    product_name = indexes.CharField(model_attr='product_name')
    price = indexes.DecimalField(model_attr='price')
    currency = indexes.CharField(model_attr='price_currency')
    

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(approved=True)
