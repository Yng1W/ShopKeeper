from flask import Blueprint, redirect, session, request, url_for

bp = Blueprint('main', __name__)

@bp.route('/toggle-lang', methods=['POST'])
def toggle_lang():
    lang = request.form.get('lang', 'en')
    session['lang'] = lang
    return redirect(request.referrer or url_for('sales.dashboard'))

@bp.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    theme = request.form.get('theme', 'light')
    session['theme'] = theme
    return redirect(request.referrer or url_for('sales.dashboard'))

@bp.route('/')
def index():
    if 'staff_id' in session:
        return redirect(url_for('sales.dashboard'))
    return redirect(url_for('auth.login'))
