from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, Client

bp = Blueprint('clients', __name__)

@bp.before_request
def require_login():
    if 'staff_id' not in session:
        return redirect(url_for('auth.login'))

@bp.route('/')
def index():
    shop_id = session.get('shop_id')
    clients = Client.query.filter_by(shop_id=shop_id).order_by(Client.name).all()
    return render_template('clients/index.html', clients=clients)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    shop_id = session.get('shop_id')
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        
        if not name or not email:
            flash('Name and Email are required', 'danger')
            return redirect(url_for('clients.new'))
            
        client = Client(
            shop_id=shop_id,
            name=name,
            phone=phone,
            email=email,
            address=address
        )
        db.session.add(client)
        db.session.commit()
        flash('Client added successfully', 'success')
        return redirect(url_for('clients.index'))
        
    return render_template('clients/new.html')

@bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
def edit(client_id):
    shop_id = session.get('shop_id')
    client = Client.query.filter_by(client_id=client_id, shop_id=shop_id).first_or_404()
    
    if request.method == 'POST':
        client.name = request.form.get('name')
        client.phone = request.form.get('phone')
        client.email = request.form.get('email')
        client.address = request.form.get('address')
        
        if not client.name or not client.email:
            flash('Name and Email are required', 'danger')
            return redirect(url_for('clients.edit', client_id=client.client_id))
            
        db.session.commit()
        flash('Client updated successfully', 'success')
        return redirect(url_for('clients.index'))
        
    return render_template('clients/edit.html', client=client)
