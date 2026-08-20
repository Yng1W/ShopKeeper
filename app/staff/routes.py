from flask import render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash
from . import bp
from ..models import db, Staff

@bp.before_request
def require_owner():
    if 'staff_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role') != 'owner':
        flash(g.strings.get('access_denied', 'Access denied. Owners only.'), 'danger')
        return redirect(url_for('sales.dashboard'))

@bp.route('/')
def index():
    shop_id = session.get('shop_id')
    staff_members = Staff.query.filter_by(shop_id=shop_id).all()
    return render_template('staff/index.html', staff=staff_members)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'attendant')
        
        if Staff.query.filter_by(username=username).first():
            flash(g.strings.get('username_taken', 'Username is already taken.'), 'danger')
            return redirect(url_for('staff.new'))
            
        staff = Staff(
            shop_id=session['shop_id'],
            name=name,
            username=username,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(staff)
        db.session.commit()
        
        flash(g.strings.get('staff_added', 'Staff member added successfully.'), 'success')
        return redirect(url_for('staff.index'))
        
    return render_template('staff/form.html', staff_member=None)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    staff_member = Staff.query.get_or_404(id)
    if staff_member.shop_id != session.get('shop_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('staff.index'))
        
    if request.method == 'POST':
        staff_member.name = request.form.get('name')
        new_username = request.form.get('username')
        
        if new_username != staff_member.username and Staff.query.filter_by(username=new_username).first():
             flash(g.strings.get('username_taken', 'Username is already taken.'), 'danger')
             return redirect(url_for('staff.edit', id=id))
             
        staff_member.username = new_username
        staff_member.role = request.form.get('role', 'attendant')
        
        password = request.form.get('password')
        if password:
            staff_member.password_hash = generate_password_hash(password)
            
        db.session.commit()
        flash(g.strings.get('staff_updated', 'Staff member updated successfully.'), 'success')
        return redirect(url_for('staff.index'))
        
    return render_template('staff/form.html', staff_member=staff_member)

@bp.route('/<int:id>/toggle-status', methods=['POST'])
def toggle_status(id):
    staff_member = Staff.query.get_or_404(id)
    if staff_member.shop_id != session.get('shop_id'):
        flash('Unauthorized', 'danger')
        return redirect(url_for('staff.index'))
        
    if staff_member.staff_id == session.get('staff_id'):
        flash(g.strings.get('cannot_deactivate_self', 'You cannot deactivate your own account.'), 'danger')
        return redirect(url_for('staff.index'))
        
    staff_member.is_active = not staff_member.is_active
    db.session.commit()
    
    status_msg = g.strings.get('activated', 'activated') if staff_member.is_active else g.strings.get('deactivated', 'deactivated')
    flash(f"{staff_member.name} {status_msg}.", 'success')
    return redirect(url_for('staff.index'))
