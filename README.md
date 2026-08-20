# ShopKeeper

ShopKeeper is a Flask + MySQL web application that helps neighbourhood shop owners (boutiques) track inventory, sales, and daily profit in real time. The goal is to solve one real problem well: **know what's in stock, know what's selling, know what's actually being made in profit — all live.**

## Features

- **Live Stock Management**: Add, edit, and view inventory. Live low-stock/out-of-stock badges.
- **Sales Tracking**: Record sales, validate against available stock, and see a dashboard of recent transactions.
- **Profit Tracking**: Live reporting dashboard for profit computation (owner role only).
- **Best/Worst Sellers**: View what items are selling well and which are not.
- **Role-Based Access**: Owner and Attendant roles with different permissions.
- **Modern UI**: Clean, modern design with custom dark/light modes.
- **Bilingual**: Interface translates between English and French.

## Setup Instructions

### Prerequisites
- Python 3.8+
- XAMPP (for MySQL)
- Git (optional)

### 1. Database Setup
1. Start XAMPP and start the MySQL module.
2. Open phpMyAdmin (`http://localhost/phpmyadmin`) or use the MySQL CLI.
3. Create a new database named `shopkeeper`.
   ```sql
   CREATE DATABASE shopkeeper;
   ```

### 2. Environment Setup
1. Clone or navigate to the project directory.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Application Configuration
Ensure your database credentials match the configuration in `app/config.py`.
By default, it uses `mysql+pymysql://root:@localhost/shopkeeper`.
If your MySQL root user has a password or you created a different user, you can set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="mysql+pymysql://username:password@localhost/shopkeeper"
```

### 4. Seed Data
Run the seed script to populate the database with initial dummy data and create the tables.
```bash
python seed.py
```
This will create two default accounts:
- **Owner**: username=`owner`, password=`password`
- **Attendant**: username=`attendant`, password=`password`

### 5. Run the Application
Start the Flask development server:
```bash
python run.py
```
Visit `http://localhost:5000` in your web browser.

## Future Improvements (Out of Scope for V1)
- **Expense Tracking UI**: The database schema includes an `Expense` model, but the UI for it is a future improvement.
- **Multi-Shop Support**: The schema allows for multiple shops, but the current UI implies a single shop context.
- **Content Translation**: Only the UI chrome is translated currently. Translating user-generated item names/categories is a future addition.
