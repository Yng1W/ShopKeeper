from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Shop(db.Model):
    __tablename__ = 'shops'
    shop_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(150), nullable=True)

    staff = db.relationship('Staff', backref='shop', lazy=True)
    items = db.relationship('Item', backref='shop', lazy=True)
    clients = db.relationship('Client', backref='shop', lazy=True)
    invoices = db.relationship('Invoice', backref='shop', lazy=True)

class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.shop_id', ondelete='RESTRICT'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'owner' or 'attendant'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sales = db.relationship('Sale', backref='staff', lazy=True)

class Item(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.shop_id', ondelete='RESTRICT'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    unit_type = db.Column(db.String(20), nullable=False) # piece, pack, kg
    cost_price = db.Column(db.Numeric(10, 2), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_in_stock = db.Column(db.Integer, default=0, nullable=False)
    reorder_threshold = db.Column(db.Integer, default=5, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_discontinued = db.Column(db.Boolean, default=False, nullable=False)
    last_low_stock_alert_at = db.Column(db.DateTime, nullable=True)

    sales = db.relationship('Sale', backref='item', lazy=True)

class Sale(db.Model):
    __tablename__ = 'sales'
    sale_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id', ondelete='RESTRICT'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id', ondelete='RESTRICT'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id', ondelete='SET NULL'), nullable=True)
    quantity_sold = db.Column(db.Integer, nullable=False)
    price_at_sale = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    __tablename__ = 'expenses'
    expense_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.shop_id', ondelete='RESTRICT'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Client(db.Model):
    __tablename__ = 'clients'
    client_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.shop_id', ondelete='RESTRICT'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sales = db.relationship('Sale', backref='client', lazy=True)
    invoices = db.relationship('Invoice', backref='client', lazy=True)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    invoice_id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.shop_id', ondelete='RESTRICT'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id', ondelete='RESTRICT'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='unpaid') # unpaid, partially_paid, paid, overdue
    created_by = db.Column(db.Integer, db.ForeignKey('staff.staff_id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('Staff', backref='created_invoices', lazy=True)
    lines = db.relationship('InvoiceLine', backref='invoice', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='invoice', lazy=True, cascade='all, delete-orphan')

class InvoiceLine(db.Model):
    __tablename__ = 'invoice_lines'
    invoice_line_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.invoice_id', ondelete='CASCADE'), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.sale_id', ondelete='RESTRICT'), nullable=False, unique=True)
    
    sale = db.relationship('Sale', backref=db.backref('invoice_line', uselist=False))

class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.invoice_id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # cash, mobile_money, bank_transfer, card
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by = db.Column(db.Integer, db.ForeignKey('staff.staff_id', ondelete='RESTRICT'), nullable=False)
    note = db.Column(db.String(255), nullable=True)

    recorder = db.relationship('Staff', backref='recorded_payments', lazy=True)
