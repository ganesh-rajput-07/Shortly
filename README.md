# 🔗 Shortly - URL Shortener

**Shortly** is a simple and efficient URL shortener that transforms long URLs into short, shareable links. Built with user-focused features like link analytics, custom labels, and a personal dashboard, it offers a fast and clean way to manage your links.

---

## 🚀 Features

- 🔐 (Optional) Google Authentication
- ✂️ Shorten any long URL
- 🧾 Add labels or tags to organize URLs
- 📊 Track click counts and top links
- 🧑‍💻 User dashboard to manage shortened URLs
- 🔗 Unique slug generation

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JS
- **Backend:** Python (FastAPI and Django)
- **Database:** SQLite
---

## 🧪 Getting Started (Local Setup)

```bash
# 1. Clone the repository
git clone https://github.com/ganesh-rajput-07/Shortly.git
cd Shortly

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the project
uvicorn main:app --reload       # If FastAPI
# OR
python app.py                   # If Flask

# 5. Open in browser:
http://127.0.0.1:8000
