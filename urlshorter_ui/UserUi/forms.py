from django import forms

# Tailwind Input for text/email/url fields
class TailwindInput(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, attrs={
            "class": "w-full px-4 py-3 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400 text-gray-900",
            "placeholder": "Enter value"
        })

# Tailwind Input for password fields
class TailwindPassword(forms.PasswordInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, attrs={
            "class": "w-full px-4 py-3 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-400 focus:border-orange-400 text-gray-900",
            "placeholder": "Enter password"
        })

# Register Form
class RegisterForm(forms.Form):
    email = forms.EmailField(widget=TailwindInput(attrs={
        "placeholder": "Enter your email"
    }))
    password = forms.CharField(widget=TailwindPassword(attrs={
        "placeholder": "Create a strong password"
    }))

# Login Form
class LoginForm(forms.Form):
    email = forms.EmailField(widget=TailwindInput(attrs={
        "placeholder": "Enter your email"
    }))
    password = forms.CharField(widget=TailwindPassword(attrs={
        "placeholder": "Enter your password"
    }))

# Shorten URL Form
class ShortenForm(forms.Form):
    original_url = forms.URLField(widget=TailwindInput(attrs={
        "placeholder": "Enter the original URL"
    }))
    shortencode = forms.CharField(widget=TailwindInput(attrs={
        "placeholder": "Custom short name (optional)"
    }))
