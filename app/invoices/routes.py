from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, Invoice, InvoiceLine, Sale, Client, Payment
from datetime import datetime, UTC
import uuid

bp = Blueprint('invoices', __name__)

@bp.before_request
def require_login():
    if 'staff_id' not in session:
        return redirect(url_for('auth.login'))

def update_invoice_status(invoice):
    total_amount = sum(line.sale.total_amount for line in invoice.lines)
    paid_amount = sum(payment.amount for payment in invoice.payments)
    
    if paid_amount >= total_amount and total_amount > 0:
        invoice.status = 'paid'
    elif paid_amount > 0:
        invoice.status = 'partially_paid'
    else:
        invoice.status = 'unpaid'
        
    db.session.commit()

@bp.route('/')
def index():
    shop_id = session.get('shop_id')
    invoices = Invoice.query.filter_by(shop_id=shop_id).order_by(Invoice.issue_date.desc()).all()
    
    now = datetime.now(UTC).replace(tzinfo=None)
    for invoice in invoices:
        if invoice.status in ['unpaid', 'partially_paid'] and invoice.due_date and invoice.due_date < now:
            invoice.is_overdue_live = True
        else:
            invoice.is_overdue_live = False
            
    return render_template('invoices/index.html', invoices=invoices)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    if session.get('role') != 'owner':
        flash('Access denied. Owners only.', 'danger')
        return redirect(url_for('invoices.index'))
    shop_id = session.get('shop_id')
    
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        sale_ids = request.form.getlist('sale_ids')
        due_date_str = request.form.get('due_date')
        
        if not client_id or not sale_ids:
            flash('Client and at least one sale are required', 'danger')
            return redirect(url_for('invoices.new'))
            
        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            
        # generate invoice number
        invoice_num = f"INV-{datetime.now().year}-{uuid.uuid4().hex[:4].upper()}"
        
        invoice = Invoice(
            shop_id=shop_id,
            client_id=client_id,
            invoice_number=invoice_num,
            due_date=due_date,
            created_by=session.get('staff_id')
        )
        db.session.add(invoice)
        db.session.flush() # get invoice_id
        
        for sale_id in sale_ids:
            line = InvoiceLine(
                invoice_id=invoice.invoice_id,
                sale_id=sale_id
            )
            db.session.add(line)
            
        db.session.commit()
        flash('Invoice created successfully', 'success')
        return redirect(url_for('invoices.detail', invoice_id=invoice.invoice_id))
        
    clients = Client.query.filter_by(shop_id=shop_id).all()
    # sales that have a client but no invoice line
    un_invoiced_sales = Sale.query.filter(
        Sale.client_id.isnot(None),
        ~Sale.sale_id.in_(db.session.query(InvoiceLine.sale_id))
    ).join(Client).filter(Client.shop_id == shop_id).all()
    
    return render_template('invoices/new.html', clients=clients, un_invoiced_sales=un_invoiced_sales)

@bp.route('/<int:invoice_id>')
def detail(invoice_id):
    shop_id = session.get('shop_id')
    invoice = Invoice.query.filter_by(invoice_id=invoice_id, shop_id=shop_id).first_or_404()
    
    total_amount = sum(line.sale.total_amount for line in invoice.lines)
    paid_amount = sum(payment.amount for payment in invoice.payments)
    balance = total_amount - paid_amount
    
    now = datetime.now(UTC).replace(tzinfo=None)
    is_overdue = invoice.status in ['unpaid', 'partially_paid'] and invoice.due_date and invoice.due_date < now
    
    return render_template('invoices/detail.html', 
                           invoice=invoice, 
                           total_amount=total_amount, 
                           paid_amount=paid_amount, 
                           balance=balance,
                           is_overdue=is_overdue)

@bp.route('/<int:invoice_id>/pay', methods=['POST'])
def add_payment(invoice_id):
    if session.get('role') != 'owner':
        flash('Access denied. Owners only.', 'danger')
        return redirect(url_for('invoices.detail', invoice_id=invoice_id))
    shop_id = session.get('shop_id')
    invoice = Invoice.query.filter_by(invoice_id=invoice_id, shop_id=shop_id).first_or_404()
    
    amount = float(request.form.get('amount', 0))
    payment_method = request.form.get('payment_method')
    note = request.form.get('note')
    
    if amount <= 0:
        flash('Valid amount is required', 'danger')
        return redirect(url_for('invoices.detail', invoice_id=invoice.invoice_id))
        
    payment = Payment(
        invoice_id=invoice.invoice_id,
        amount=amount,
        payment_method=payment_method,
        note=note,
        recorded_by=session.get('staff_id')
    )
    db.session.add(payment)
    db.session.commit()
    
    update_invoice_status(invoice)
    
    flash('Payment recorded successfully', 'success')
    return redirect(url_for('invoices.detail', invoice_id=invoice.invoice_id))
