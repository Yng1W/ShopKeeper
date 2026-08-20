from .models import db, Item, Sale, Staff
from sqlalchemy import func

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
