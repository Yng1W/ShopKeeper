from flask import render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from . import bp
from ..models import db, Staff, Shop

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Staff.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash(g.strings.get('account_deactivated', 'Account is deactivated.'), 'danger')
                return render_template('auth/login.html')
            
            session['staff_id'] = user.staff_id
            session['shop_id'] = user.shop_id
            session['role'] = user.role
            session['name'] = user.name
            session['shop_name'] = user.shop.name
            flash(g.strings.get('login_success', 'Login successful!'), 'success')
            return redirect(url_for('sales.dashboard'))
            
        flash(g.strings.get('login_failed', 'Invalid username or password.'), 'danger')
        
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash(g.strings.get('logout_success', 'Logged out successfully.'), 'success')
    return redirect(url_for('auth.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        shop_name = request.form.get('shop_name')
        owner_name = request.form.get('owner_name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        location = request.form.get('location')

        if not shop_name or not owner_name or not username or not password:
            flash(g.strings.get('fill_required', 'Please fill all required fields.'), 'danger')
            return render_template('auth/signup.html')

        if password != confirm_password:
            flash(g.strings.get('passwords_mismatch', 'Passwords do not match.'), 'danger')
            return render_template('auth/signup.html')

        if Staff.query.filter_by(username=username).first():
            flash(g.strings.get('username_taken', 'Username is already taken.'), 'danger')
            return render_template('auth/signup.html')

        shop = Shop(name=shop_name, owner_name=owner_name, location=location)
        db.session.add(shop)
        db.session.commit()

        owner = Staff(
            shop_id=shop.shop_id,
            name=owner_name,
            username=username,
            password_hash=generate_password_hash(password),
            role='owner'
        )
        db.session.add(owner)
        db.session.commit()

        session['staff_id'] = owner.staff_id
        session['shop_id'] = owner.shop_id
        session['role'] = owner.role
        session['name'] = owner.name
        session['shop_name'] = owner.shop.name
        flash(g.strings.get('signup_success', 'Shop created successfully! Welcome.'), 'success')
        return redirect(url_for('sales.dashboard'))

    return render_template('auth/signup.html')
