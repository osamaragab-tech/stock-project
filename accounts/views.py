from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import get_language
from django.urls import reverse
# ===============================
# Signup
# ===============================
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "❌ Passwords do not match!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, f"❌ Username '{username}' already exists!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)  # تسجيل الدخول تلقائيًا
            messages.success(request, f"✅ Welcome {username}, your account was created successfully!")
            return redirect('inventory:inventory_home')

        # لو فيه خطأ نرجع form مع الرسائل
        return render(request, 'accounts/signup.html', {
            'username': username,
            'email': email,
        })

    # لو GET
    return render(request, 'accounts/signup.html')


# ===============================
# Login
# ===============================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"✅ Welcome back, {user.username}!")
            return redirect('inventory:inventory_home')
        else:
            messages.error(request, "❌ Invalid username or password.")

    return render(request, 'accounts/login.html')

# ===============================
# Logout
# ===============================
def logout_view(request):
    logout(request)
    messages.success(request, "✅ You have been logged out.")
    return redirect('accounts:login')