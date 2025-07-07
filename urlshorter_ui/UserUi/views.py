import base64
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ShortenForm

FASTAPI_BASE = "http://localhost:8000"


# ✅ Register View
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            payload = form.cleaned_data
            response = requests.post(f"{FASTAPI_BASE}/register", json=payload)
            if response.status_code == 200:
                messages.success(request, "Registered successfully. Please login.")
                return redirect("login")
            else:
                messages.error(request, "Registration failed. Try another email.")
    else:
        form = RegisterForm()
    return render(request, "auth/register.html", {"form": form})


# ✅ Login View
def login_view(request):
    token = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            payload = form.cleaned_data
            response = requests.post(f"{FASTAPI_BASE}/login", json=payload)
            if response.status_code == 200 and "token" in response.json():
                token = response.json()["token"]
                request.session["token"] = token
                messages.success(request, "Logged in successfully.")
                return redirect("shorten")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, "auth/login.html", {"form": form, "token": token})


# ✅ Shorten URL View
def shorten_view(request):
    token = request.session.get("token")
    if not token:
        messages.warning(request, "Please login first.")
        return redirect("login")

    short_url = None

    if request.method == "POST":
        form = ShortenForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data["original_url"]
            shortencode = form.cleaned_data["shortencode"]

            json_data = {
                "originalUrl": original_url,
                "shortenUrl": shortencode
            }

            params = {"token": token}

            try:
                response = requests.post(f"{FASTAPI_BASE}/url-short", json=json_data, params=params)
                if response.status_code == 401:
                    request.session.flush()
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("login")

                data = response.json()
                if response.status_code == 200:
                    short_url = data["shortenUrl"]
                    messages.success(request, f"Short URL created: {short_url}")
                else:
    # Handle both 'message' and 'detail' fields for better error feedback
                    error_msg = data.get("detail") or data.get("message") or "Shortening failed."
                    messages.error(request, error_msg)

            except Exception:
                messages.error(request, "Internal error while contacting API.")
    else:
        form = ShortenForm()

    return render(request, "shorten.html", {"form": form, "short_url": short_url, "token": token})


# ✅ URL List View
def url_list_view(request):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    try:
        response = requests.get(f"{FASTAPI_BASE}/my-urls", params={"token": token})
        if response.status_code == 401:
            request.session.flush()
            messages.error(request, "Session expired. Please login again.")
            return redirect("login")

        if response.status_code == 200:
            data = response.json()
            urls = data.get("urls", [])
        else:
            urls = []

    except Exception:
        urls = []
    return render(request, "url_list.html", {"urls": urls, "token": token})


# ✅ Delete URL
def delete_url_view(request, url_id):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    try:
        response = requests.delete(f"{FASTAPI_BASE}/delete-url/{url_id}", params={"token": token})
        if response.status_code == 401:
            request.session.flush()
            messages.error(request, "Session expired. Please login again.")
            return redirect("login")
    except Exception:
        pass

    return redirect("url_list")


# ✅ Logout View
def logout_view(request):
    try:
        del request.session["token"]
    except KeyError:
        pass
    return redirect("login")


# ✅ QR Generator View
def generate_qr_view(request):
    qr_image = None
    if request.method == "POST":
        url = request.POST.get("qr_url")
        logo = request.FILES.get("logo")
        token = request.session.get("token")

        if not token:
            messages.warning(request, "Login required")
            return redirect("login")

        files = {}
        if logo:
            files["logo"] = logo

        params = {
            "url": url,
            "token": token,
        }

        try:
            response = requests.post(f"{FASTAPI_BASE}/generate-qr/", params=params, files=files)
            if response.status_code == 401:
                request.session.flush()
                messages.error(request, "Session expired. Please login again.")
                return redirect("login")

            if response.status_code == 200:
                qr_image = base64.b64encode(response.content).decode("utf-8")
            else:
                messages.error(request, "Failed to generate QR")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, "qr_generator.html", {"qr_image": qr_image})


# ✅ QR List View (if used)
def qr_list_view(request):
    token = request.session.get("token")
    if not token:
        messages.warning(request, "Please login")
        return redirect("login")

    try:
        response = requests.get(f"{FASTAPI_BASE}/user-qr-list", params={"token": token})
        if response.status_code == 401:
            request.session.flush()
            messages.error(request, "Session expired. Please login again.")
            return redirect("login")

        if response.status_code == 200:
            qr_list = response.json()
        else:
            qr_list = []
    except Exception:
        qr_list = []

    return render(request, "qr_list.html", {"qr_list": qr_list})

# views.py
def dashboard_view(request):
    token = request.session.get("token")
    if not token:
        messages.error(request, "Please login first.")
        return redirect("login")

    try:
        res = requests.get("http://127.0.0.1:8000/dashboard-stats", params={"token": token})
        if res.status_code == 200:
            stats = res.json()
        else:
            stats = {"total_urls": 0, "total_clicks": 0}
            messages.warning(request, "Could not fetch dashboard stats.")
    except Exception:
        stats = {"total_urls": 0, "total_clicks": 0}
        messages.error(request, "Failed to connect to the backend.")

    return render(request, "dashboard.html", {
        "stats": stats,
        "token": token  # This is passed to JavaScript
    })


from django.http import HttpResponse
import requests

def export_csv_view(request):
    token = request.session.get("token")
    if not token:
        messages.warning(request, "Please login first.")
        return redirect("login")

    response = requests.get("http://localhost:8000/export-urls", params={"token": token})
    if response.status_code != 200:
        messages.error(request, "Failed to download CSV.")
        return redirect("url_list")

    # Return as CSV
    return HttpResponse(
        response.content,
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="short_urls.csv"'}
    )
