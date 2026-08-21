from flask import render_template, redirect, url_for, flash, session, request
from . import bp
from ..services import get_profit_for_period, get_best_sellers, get_worst_sellers, get_attendant_performance, get_attendant_sales_details, get_sales_trend_data
from ..ai_service import generate_sales_insights_narrative
from datetime import datetime, timedelta

@bp.before_request
def require_owner():
    if 'staff_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') != 'owner':
        flash('Access denied. Owners only.', 'danger')
        return redirect(url_for('sales.dashboard'))

def get_date_range(period):
    now = datetime.utcnow()
    if period == 'today':
        return now.replace(hour=0, minute=0, second=0, microsecond=0), None
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        return start.replace(hour=0, minute=0, second=0, microsecond=0), None
    return None, None

@bp.route('/')
def index():
    shop_id = session.get('shop_id')
    period = request.args.get('period', 'all')
    start_date, end_date = get_date_range(period)
    
    profit = get_profit_for_period(shop_id, start_date, end_date)
    best_sellers = get_best_sellers(shop_id, start_date=start_date, end_date=end_date)
    worst_sellers = get_worst_sellers(shop_id, start_date=start_date, end_date=end_date)
    
    return render_template('reports/index.html', profit=profit, best_sellers=best_sellers, worst_sellers=worst_sellers, period=period)

@bp.route('/attendants')
def attendants():
    shop_id = session.get('shop_id')
    period = request.args.get('period', 'all')
    start_date, end_date = get_date_range(period)
    
    performance = get_attendant_performance(shop_id, start_date, end_date)
    details = get_attendant_sales_details(shop_id, start_date, end_date)
    
    return render_template('reports/attendants.html', performance=performance, details=details, period=period)

@bp.route('/insights')
def insights():
    shop_id = session.get('shop_id')
    trend_data = get_sales_trend_data(shop_id)
    narrative = generate_sales_insights_narrative(trend_data)
    
    return render_template('reports/insights.html', trend_data=trend_data, narrative=narrative)
