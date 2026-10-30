from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm, RegisterForm, ReviewForm, StoreForm
from .models import Order, OrderItem, Product, Profile, Store


def is_vendor(user):
    return (
        user.is_authenticated
        and Profile.objects.filter(
            user=user,
            account_type="vendor",
        ).exists()
    )


def is_buyer(user):
    return (
        user.is_authenticated
        and Profile.objects.filter(
            user=user,
            account_type="buyer",
        ).exists()
    )


def home(request):
    products = (
        Product.objects.select_related("store")
        .all()
        .order_by("name")
    )
    return render(
        request,
        "posts/home.html",
        {"products": products},
    )


def register_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )

        account_type = form.cleaned_data["account_type"]

        Profile.objects.create(
            user=user,
            account_type=account_type,
        )

        group_name = (
            "Vendors"
            if account_type == "vendor"
            else "Buyers"
        )

        group, _ = Group.objects.get_or_create(
            name=group_name
        )

        user.groups.add(group)

        if account_type == "vendor":
            permissions = Permission.objects.filter(
                content_type__app_label="posts",
                codename__in=[
                    "add_store",
                    "change_store",
                    "delete_store",
                    "view_store",
                    "add_product",
                    "change_product",
                    "delete_product",
                    "view_product",
                ],
            )
        else:
            permissions = Permission.objects.filter(
                content_type__app_label="posts",
                codename__in=[
                    "view_product",
                    "add_review",
                    "view_review",
                ],
            )

        group.permissions.add(*permissions)

        login(request, user)

        messages.success(
            request,
            "Your account was created successfully.",
        )

        return redirect("home")

    return render(
        request,
        "posts/register.html",
        {"form": form},
    )


def login_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    error = None

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user:
            login(request, user)
            request.session.set_expiry(3600)
            return redirect("home")

        error = "Invalid username or password."

    return render(
        request,
        "posts/login.html",
        {"error": error},
    )


def logout_user(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def store_list(request):
    if not is_vendor(request.user):
        return HttpResponseForbidden(
            "Only vendors can manage stores."
        )

    stores = Store.objects.filter(
        vendor=request.user
    )

    return render(
        request,
        "posts/store_list.html",
        {"stores": stores},
    )


@login_required(login_url="login")
def store_create(request):
    if not is_vendor(request.user):
        return HttpResponseForbidden(
            "Only vendors can create stores."
        )

    form = StoreForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        store = form.save(commit=False)
        store.vendor = request.user
        store.save()

        return redirect("store_list")

    return render(
        request,
        "posts/form.html",
        {
            "form": form,
            "heading": "Create Store",
        },
    )


@login_required(login_url="login")
def store_update(request, pk):
    store = get_object_or_404(
        Store,
        pk=pk,
        vendor=request.user,
    )

    form = StoreForm(
        request.POST or None,
        instance=store,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("store_list")

    return render(
        request,
        "posts/form.html",
        {
            "form": form,
            "heading": "Edit Store",
        },
    )


@login_required(login_url="login")
def store_delete(request, pk):
    store = get_object_or_404(
        Store,
        pk=pk,
        vendor=request.user,
    )

    if request.method == "POST":
        store.delete()
        return redirect("store_list")

    return render(
        request,
        "posts/confirm_delete.html",
        {
            "object": store,
            "type": "store",
        },
    )


@login_required(login_url="login")
def product_create(request, store_pk):
    store = get_object_or_404(
        Store,
        pk=store_pk,
        vendor=request.user,
    )

    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.store = store
        product.save()

        return redirect("store_list")

    return render(
        request,
        "posts/form.html",
        {
            "form": form,
            "heading": f"Add Product to {store.name}",
        },
    )


@login_required(login_url="login")
def product_update(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        store__vendor=request.user,
    )

    form = ProductForm(
        request.POST or None,
        instance=product,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("store_list")

    return render(
        request,
        "posts/form.html",
        {
            "form": form,
            "heading": "Edit Product",
        },
    )


@login_required(login_url="login")
def product_delete(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        store__vendor=request.user,
    )

    if request.method == "POST":
        product.delete()
        return redirect("store_list")

    return render(
        request,
        "posts/confirm_delete.html",
        {
            "object": product,
            "type": "product",
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("store"),
        pk=pk,
    )

    reviews = (
        product.reviews.select_related("buyer")
        .order_by("-created_at")
    )

    return render(
        request,
        "posts/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
        },
    )


@login_required(login_url="login")
def add_to_cart(request, pk):
    if not is_buyer(request.user):
        return HttpResponseForbidden(
            "Only buyers can add products to a cart."
        )

    product = get_object_or_404(
        Product,
        pk=pk,
    )

    if request.method == "POST":
        try:
            quantity = max(
                1,
                int(request.POST.get("quantity", 1)),
            )
        except ValueError:
            quantity = 1

        quantity = min(
            quantity,
            product.stock,
        )

        if quantity < 1:
            messages.error(
                request,
                "This product is out of stock.",
            )

            return redirect(
                "product_detail",
                pk=pk,
            )

        cart = request.session.get(
            "cart",
            {},
        )

        key = str(product.pk)

        cart[key] = min(
            cart.get(key, 0) + quantity,
            product.stock,
        )

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(
            request,
            "Product added to your cart.",
        )

    return redirect("cart")


def cart_view(request):
    cart = request.session.get(
        "cart",
        {},
    )

    products = (
        Product.objects.filter(
            pk__in=cart.keys()
        )
        .select_related("store")
    )

    items = []
    total = Decimal("0.00")

    for product in products:
        quantity = cart.get(
            str(product.pk),
            0,
        )

        subtotal = product.price * quantity
        total += subtotal

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "posts/cart.html",
        {
            "items": items,
            "total": total,
        },
    )


def remove_from_cart(request, pk):
    cart = request.session.get(
        "cart",
        {},
    )

    cart.pop(
        str(pk),
        None,
    )

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


@login_required(login_url="login")
@transaction.atomic
def checkout(request):
    if not is_buyer(request.user):
        return HttpResponseForbidden(
            "Only buyers can checkout."
        )

    if request.method != "POST":
        return redirect("cart")

    cart = request.session.get(
        "cart",
        {},
    )

    if not cart:
        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart")

    products = {
        str(product.pk): product
        for product in Product.objects.select_for_update().filter(
            pk__in=cart.keys()
        )
    }

    for product_id, quantity in cart.items():
        product = products.get(product_id)

        if not product or product.stock < quantity:
            messages.error(
                request,
                "One of your products no longer has enough stock.",
            )

            return redirect("cart")

    order = Order.objects.create(
        buyer=request.user
    )

    total = Decimal("0.00")

    invoice_lines = [
        f"Invoice for {request.user.username}",
        f"Order #{order.pk}",
        "",
    ]

    for product_id, quantity in cart.items():
        product = products[product_id]

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )

        product.stock -= quantity
        product.save(
            update_fields=["stock"]
        )

        subtotal = product.price * quantity
        total += subtotal

        invoice_lines.append(
            f"{product.name} x {quantity} "
            f"= R{subtotal:.2f}"
        )

    order.total = total
    order.save(
        update_fields=["total"]
    )

    invoice_lines.extend(
        [
            "",
            f"Total: R{total:.2f}",
        ]
    )

    if request.user.email:
        EmailMessage(
            "Your eCommerce invoice",
            "\n".join(invoice_lines),
            "shop@example.com",
            [request.user.email],
        ).send(
            fail_silently=True
        )

    request.session["cart"] = {}
    request.session.modified = True

    return render(
        request,
        "posts/checkout_success.html",
        {"order": order},
    )


@login_required(login_url="login")
def add_review(request, pk):
    if not is_buyer(request.user):
        return HttpResponseForbidden(
            "Only buyers can leave reviews."
        )

    product = get_object_or_404(
        Product,
        pk=pk,
    )

    form = ReviewForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.buyer = request.user

        review.verified = OrderItem.objects.filter(
            order__buyer=request.user,
            product=product,
        ).exists()

        review.save()

        return redirect(
            "product_detail",
            pk=pk,
        )

    return render(
        request,
        "posts/form.html",
        {
            "form": form,
            "heading": f"Review {product.name}",
        },
    )
