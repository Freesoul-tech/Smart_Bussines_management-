from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

User = get_user_model()


def landing(request):

    if request.user.is_authenticated:
        return redirect("accounts:post_login")

    return render(
        request,
        "accounts/landing.html",
    )


def signup(request):

    if request.user.is_authenticated:
        return redirect("accounts:post_login")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        errors = []

        if not username:
            errors.append("Username is required.")

        if not email:
            errors.append("Email is required.")

        if not password:
            errors.append("Password is required.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")

        if User.objects.filter(email=email).exists():
            errors.append("Email already exists.")

        if not errors:

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            login(request, user)

            return redirect("accounts:post_login")

        return render(
            request,
            "accounts/landing.html",
            {
                "mode": "signup",
                "errors": errors,
                "username": username,
                "email": email,
            },
        )

    return render(
        request,
        "accounts/landing.html",
        {
            "mode": "signup",
        },
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:post_login")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            return redirect("accounts:post_login")

        return render(
            request,
            "accounts/landing.html",
            {
                "mode": "login",
                "error": "Invalid username or password.",
            },
        )

    return render(
        request,
        "accounts/landing.html",
        {
            "mode": "login",
        },
    )


@login_required
def post_login(request):

    from businesses.models import Business

    business = (
        Business.objects
        .filter(owner=request.user)
        .first()
    )

    if business:

        # Existing user ? go directly to dashboard
        return redirect("dashboard:dashboard")

    # New user ? business setup
    return redirect("businesses:business_setup")


@login_required
def logout_view(request):

    logout(request)

    return redirect("accounts:landing")
