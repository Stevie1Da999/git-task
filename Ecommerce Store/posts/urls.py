from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="posts/password_reset_form.html",
            email_template_name="posts/password_reset_email.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="posts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="posts/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="posts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    path("stores/", views.store_list, name="store_list"),
    path("stores/new/", views.store_create, name="store_create"),
    path(
        "stores/<int:pk>/edit/",
        views.store_update,
        name="store_update",
    ),
    path(
        "stores/<int:pk>/delete/",
        views.store_delete,
        name="store_delete",
    ),
    path(
        "stores/<int:store_pk>/products/new/",
        views.product_create,
        name="product_create",
    ),

    path(
        "products/<int:pk>/",
        views.product_detail,
        name="product_detail",
    ),
    path(
        "products/<int:pk>/edit/",
        views.product_update,
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        views.product_delete,
        name="product_delete",
    ),
    path(
        "products/<int:pk>/review/",
        views.add_review,
        name="add_review",
    ),

    path("cart/", views.cart_view, name="cart"),
    path(
        "cart/add/<int:pk>/",
        views.add_to_cart,
        name="add_to_cart",
    ),
    path(
        "cart/remove/<int:pk>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("checkout/", views.checkout, name="checkout"),
]
