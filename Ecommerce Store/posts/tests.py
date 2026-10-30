from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Product, Profile, Store


class EcommerceTests(TestCase):
    def setUp(self):
        self.vendor = User.objects.create_user("vendor", password="TestPass123!")
        Profile.objects.create(user=self.vendor, account_type="vendor")
        self.buyer = User.objects.create_user("buyer", password="TestPass123!", email="buyer@example.com")
        Profile.objects.create(user=self.buyer, account_type="buyer")
        self.store = Store.objects.create(vendor=self.vendor, name="Cape Store")
        self.product = Product.objects.create(store=self.store, name="Football", price=250, stock=5)

    def test_product_is_visible(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Football")

    def test_buyer_can_add_to_cart(self):
        self.client.login(username="buyer", password="TestPass123!")
        self.client.post(reverse("add_to_cart", args=[self.product.pk]), {"quantity": 2})
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 2)

    def test_vendor_can_create_store(self):
        self.client.login(username="vendor", password="TestPass123!")
        response = self.client.post(reverse("store_create"), {"name": "Second Store", "description": "Local shop"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Store.objects.filter(name="Second Store").exists())
