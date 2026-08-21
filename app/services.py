from .models import db, Item, Sale, Staff
from sqlalchemy import func
from flask_mail import Message
from app import mail
from flask import current_app, url_for
from datetime import datetime, timedelta, UTC

def get_profit_for_period(shop_id, start_date=None, end_date=None):
    query = db.session.query(
        func.sum((Sale.price_at_sale - Item.cost_price) * Sale.quantity_sold)
    ).join(Item).filter(Item.shop_id == shop_id)
    
    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)
        
    result = query.scalar()
    return result or 0.0

def get_low_stock_items(shop_id):
    return Item.query.filter(
        Item.shop_id == shop_id,
        Item.is_discontinued == False,
        Item.quantity_in_stock < Item.reorder_threshold
    ).all()

def get_best_sellers(shop_id, limit=5, start_date=None, end_date=None):
    query = db.session.query(
        Item, func.sum(Sale.quantity_sold).label('total_sold')
    ).join(Sale).filter(
        Item.shop_id == shop_id
    )
    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)
    return query.group_by(Item.item_id).order_by(
        db.desc('total_sold')
    ).limit(limit).all()

def get_worst_sellers(shop_id, limit=5, start_date=None, end_date=None):
    query = db.session.query(
        Item, func.sum(Sale.quantity_sold).label('total_sold')
    ).join(Sale).filter(
        Item.shop_id == shop_id
    )
    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)
    return query.group_by(Item.item_id).order_by(
        db.asc('total_sold')
    ).limit(limit).all()

def get_attendant_performance(shop_id, start_date=None, end_date=None):
    profit_col = (Sale.price_at_sale - Item.cost_price) * Sale.quantity_sold
    query = db.session.query(
        Staff,
        func.count(Sale.sale_id).label('total_sales_count'),
        func.sum(Sale.total_amount).label('total_revenue'),
        func.sum(profit_col).label('total_profit')
    ).join(Sale, Staff.staff_id == Sale.staff_id).join(Item, Sale.item_id == Item.item_id).filter(
        Staff.shop_id == shop_id
    )
    
    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)
        
    results = query.group_by(Staff.staff_id).all()
    
    # Fill in zero for staff with no sales
    staff_members = Staff.query.filter_by(shop_id=shop_id).all()
    staff_with_sales = {r[0].staff_id: r for r in results}
    
    final_results = []
    for staff in staff_members:
        if staff.staff_id in staff_with_sales:
            r = staff_with_sales[staff.staff_id]
            final_results.append({
                'staff': r[0],
                'sales_count': r.total_sales_count or 0,
                'revenue': r.total_revenue or 0,
                'profit': r.total_profit or 0
            })
        else:
            final_results.append({
                'staff': staff,
                'sales_count': 0,
                'revenue': 0,
                'profit': 0
            })
            
    # Sort descending by profit
    final_results.sort(key=lambda x: x['profit'], reverse=True)
    return final_results

def get_attendant_sales_details(shop_id, start_date=None, end_date=None):
    query = db.session.query(Sale).join(Item).join(Staff).filter(
        Staff.shop_id == shop_id
    )
    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)
        
    sales = query.order_by(Sale.timestamp.desc()).all()
    
    details_by_staff = {}
    for sale in sales:
        if sale.staff_id not in details_by_staff:
            details_by_staff[sale.staff_id] = []
        details_by_staff[sale.staff_id].append(sale)
        
    return details_by_staff

def check_and_send_low_stock_email(item):
    if not item.shop.email:
        return
        
    now = datetime.now(UTC).replace(tzinfo=None)
    # Check if we should send an email (only once per 24 hours)
    if item.last_low_stock_alert_at and (now - item.last_low_stock_alert_at) < timedelta(hours=24):
        return
        
    try:
        msg = Message(f"Low Stock Alert: {item.name}", recipients=[item.shop.email])
        # Simple plain text body
        msg.body = f"Hello,\n\nThe item '{item.name}' is running low on stock.\n" \
                   f"Current quantity: {item.quantity_in_stock}\n" \
                   f"Reorder threshold: {item.reorder_threshold}\n\n" \
                   f"Please check the stock dashboard to restock."
        mail.send(msg)
        item.last_low_stock_alert_at = now
        db.session.commit()
    except Exception as e:
        # Silently fail or log the error
        current_app.logger.error(f"Failed to send low stock email: {e}")
        
def get_sales_trend_data(shop_id):
    now = datetime.now(UTC).replace(tzinfo=None)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate previous month start
    if this_month_start.month == 1:
        last_month_start = this_month_start.replace(year=this_month_start.year - 1, month=12)
    else:
        last_month_start = this_month_start.replace(month=this_month_start.month - 1)
        
    # Get all items
    items = Item.query.filter_by(shop_id=shop_id).all()
    
    trend_data = []
    
    total_profit_this_month = 0
    total_profit_last_month = 0
    
    for item in items:
        # This month's sales
        tm_sales = Sale.query.filter(Sale.item_id == item.item_id, Sale.timestamp >= this_month_start).all()
        tm_qty = sum(s.quantity_sold for s in tm_sales)
        tm_profit = sum((s.price_at_sale - item.cost_price) * s.quantity_sold for s in tm_sales)
        
        # Last month's sales
        lm_sales = Sale.query.filter(Sale.item_id == item.item_id, Sale.timestamp >= last_month_start, Sale.timestamp < this_month_start).all()
        lm_qty = sum(s.quantity_sold for s in lm_sales)
        lm_profit = sum((s.price_at_sale - item.cost_price) * s.quantity_sold for s in lm_sales)
        
        total_profit_this_month += tm_profit
        total_profit_last_month += lm_profit
        
        if lm_qty > 0:
            pct_change = ((tm_qty - lm_qty) / lm_qty) * 100
        elif tm_qty > 0:
            pct_change = 100 # From 0 to something
        else:
            pct_change = 0 # From 0 to 0
            
        trend_data.append({
            'item_name': item.name,
            'this_month_units': tm_qty,
            'last_month_units': lm_qty,
            'pct_change': pct_change
        })
        
    return {
        'trend_data': trend_data,
        'total_profit_this_month': float(total_profit_this_month),
        'total_profit_last_month': float(total_profit_last_month)
    }
