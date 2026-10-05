from django.urls import path

from .views import (
    landing,
    signup,
    login_view,
    post_login,
    logout_view,
)

app_name = "accounts"

urlpatterns = [
    path("", landing, name="landing"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("post-login/", post_login, name="post_login"),
    path("logout/", logout_view, name="logout"),
]