from flask import render_template, request, redirect, url_for, flash, session, g
from . import bp
from ..models import db, Item
from ..services import get_low_stock_items

@bp.before_request
def require_login():
    if 'staff_id' not in session:
        return redirect(url_for('auth.login'))

@bp.route('/')
def index():
    shop_id = session.get('shop_id')
    items = Item.query.filter_by(shop_id=shop_id, is_discontinued=False).all()
    low_stock = get_low_stock_items(shop_id)
    low_stock_ids = [item.item_id for item in low_stock]
    return render_template('stock/index.html', items=items, low_stock_ids=low_stock_ids)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        item = Item(
            shop_id=session['shop_id'],
            name=request.form.get('name'),
            category=request.form.get('category'),
            unit_type=request.form.get('unit_type'),
            cost_price=request.form.get('cost_price'),
            selling_price=request.form.get('selling_price'),
            quantity_in_stock=request.form.get('quantity_in_stock'),
            reorder_threshold=request.form.get('reorder_threshold')
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully.', 'success')
        return redirect(url_for('stock.index'))
    return render_template('stock/form.html', item=None)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    item = Item.query.get_or_404(id)
    if item.shop_id != session.get('shop_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('stock.index'))

    if request.method == 'POST':
        item.name = request.form.get('name')
        item.category = request.form.get('category')
        item.unit_type = request.form.get('unit_type')
        item.cost_price = request.form.get('cost_price')
        item.selling_price = request.form.get('selling_price')
        item.quantity_in_stock = request.form.get('quantity_in_stock')
        item.reorder_threshold = request.form.get('reorder_threshold')
        db.session.commit()
        flash('Item updated successfully.', 'success')
        return redirect(url_for('stock.index'))
    return render_template('stock/form.html', item=item)
