# 🏪 Django Stock Management System

A professional **inventory and stock management system** built with Django and Bootstrap.  
It can be used for **any type of business** — retail stores, warehouses, clothing shops, electronics, etc.

---

## 🚀 Features

- 🔐 User authentication (login, signup)
- 🏢 Company & branch management
- 📦 Product and category management
- 🔄 Track stock in/out movements
- 🧾 Sales and return invoices
- 📊 Dashboard with real-time statistics
- 🌍 Multi-language support (Arabic & English)
- 🖨️ Barcode generation and printing

---

## 🧠 Tech Stack

- **Backend:** Django 5.x, Python 3.x  
- **Frontend:** HTML, CSS, Bootstrap 5  
- **Database:** SQLite / PostgreSQL  
- **Languages:** English, Arabic

---

## ⚙️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/osamaragab-tech/stock-project.git
cd stock-project

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
