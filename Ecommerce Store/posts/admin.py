from django.contrib import admin
from .models import Order, OrderItem, Product, Profile, Review, Store

admin.site.register([Profile, Store, Product, Order, OrderItem, Review])
