from flask import render_template, request, redirect, url_for, flash, session, g
from . import bp
from ..models import db, Item, Sale, Client
from ..services import get_low_stock_items, check_and_send_low_stock_email

@bp.before_request
def require_login():
    if 'staff_id' not in session:
        return redirect(url_for('auth.login'))

@bp.route('/')
@bp.route('/dashboard')
def dashboard():
    shop_id = session.get('shop_id')
    recent_sales = Sale.query.join(Item).filter(Item.shop_id == shop_id).order_by(Sale.timestamp.desc()).limit(10).all()
    return render_template('sales/dashboard.html', recent_sales=recent_sales)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    shop_id = session.get('shop_id')
    items = Item.query.filter_by(shop_id=shop_id, is_discontinued=False).all()
    clients = Client.query.filter_by(shop_id=shop_id).all()
    
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity_sold = int(request.form.get('quantity_sold'))
        client_id = request.form.get('client_id')
        client_id = int(client_id) if client_id else None
        
        item = Item.query.filter_by(item_id=item_id, shop_id=shop_id).first()
        if not item:
            flash('Item not found.', 'danger')
            return redirect(url_for('sales.new'))
            
        if item.quantity_in_stock < quantity_sold:
            flash('Not enough stock.', 'danger')
            return redirect(url_for('sales.new'))
            
        sale = Sale(
            item_id=item.item_id,
            staff_id=session['staff_id'],
            client_id=client_id,
            quantity_sold=quantity_sold,
            price_at_sale=item.selling_price,
            total_amount=item.selling_price * quantity_sold
        )
        
        item.quantity_in_stock -= quantity_sold
        db.session.add(sale)
        db.session.commit()
        
        flash('Sale recorded successfully.', 'success')
        
        # Check low stock
        if item.quantity_in_stock < item.reorder_threshold:
            flash(f'Warning: {item.name} is now low on stock.', 'warning')
            check_and_send_low_stock_email(item)
            
        return redirect(url_for('sales.dashboard'))
        
    return render_template('sales/new.html', items=items, clients=clients)
