from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import json
from datetime import datetime, timedelta
import uuid
from werkzeug.utils import secure_filename
from functools import wraps

from config import Config
from database import db, init_db, User, Customer, Item, Estimate, EstimateItem

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Add current datetime to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Initialize database
init_db(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom decorator for checking if user is allowed
def allowed_users_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('username') or session.get('username') not in app.config['ALLOWED_USERS']:
            flash('You are not authorized to access this application.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Create default admin user if it doesn't exist
def create_default_user():
    with app.app_context():
        if User.query.count() == 0:
            admin_user = User(
                username=app.config['USERNAME'],
                name='Gaurish'
            )
            admin_user.set_password(app.config['PASSWORD'])
            db.session.add(admin_user)
            db.session.commit()
            print(f"Created default user: {app.config['USERNAME']}")

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Check if user is in allowed users list
            if username not in app.config['ALLOWED_USERS']:
                flash('You are not authorized to access this application.', 'danger')
                return redirect(url_for('login'))
            
            # Update last login time
            user.last_login = datetime.now()
            db.session.commit()
            
            # Begin user session
            login_user(user)
            session['user_id'] = user.id
            session['username'] = username
            session['name'] = user.name
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@allowed_users_only
def dashboard():
    # Get statistics for dashboard
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    first_day_of_month = today.replace(day=1)
    first_day_of_year = today.replace(month=1, day=1)
    
    # Estimates statistics
    estimates_yesterday = Estimate.query.filter(Estimate.estimate_date == yesterday).count()
    estimates_this_month = Estimate.query.filter(Estimate.estimate_date >= first_day_of_month).count()
    estimates_this_year = Estimate.query.filter(Estimate.estimate_date >= first_day_of_year).count()
    
    # Customer and item counts
    customer_count = Customer.query.count()
    item_count = Item.query.count()
    
    # Last 4 days trend data
    trend_data = []
    for i in range(4, 0, -1):
        day = today - timedelta(days=i)
        count = Estimate.query.filter(Estimate.estimate_date == day).count()
        trend_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return render_template('dashboard.html', 
                          estimates_yesterday=estimates_yesterday,
                          estimates_this_month=estimates_this_month,
                          estimates_this_year=estimates_this_year,
                          customer_count=customer_count,
                          item_count=item_count,
                          trend_data=json.dumps(trend_data))

@app.route('/customers')
@allowed_users_only
def customers():
    return render_template('customers.html')

@app.route('/api/customers', methods=['GET'])
@allowed_users_only
def get_customers():
    search_term = request.args.get('search', '')
    
    if search_term:
        customers = Customer.query.filter(
            (Customer.name.ilike(f'%{search_term}%')) | 
            (Customer.mobile.ilike(f'%{search_term}%'))
        ).all()
    else:
        customers = Customer.query.all()
    
    return jsonify([customer.to_dict() for customer in customers])

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
@allowed_users_only
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@app.route('/api/customers', methods=['POST'])
@allowed_users_only
def create_customer():
    data = request.json
    
    if not data.get('name') or not data.get('mobile'):
        return jsonify({'error': 'Name and mobile are required'}), 400
    
    customer = Customer(
        name=data.get('name'),
        address=data.get('address'),
        mobile=data.get('mobile')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify(customer.to_dict()), 201

@app.route('/search')
@allowed_users_only
def search():
    return render_template('search.html')

@app.route('/api/search', methods=['GET'])
@allowed_users_only
def api_search():
    search_type = request.args.get('type', 'customer')
    search_term = request.args.get('term', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if search_type == 'customer' and search_term:
        # Search by customer name or mobile
        customers = Customer.query.filter(
            (Customer.name.ilike(f'%{search_term}%')) | 
            (Customer.mobile.ilike(f'%{search_term}%'))
        ).all()
        
        customer_ids = [c.id for c in customers]
        estimates = Estimate.query.filter(Estimate.customer_id.in_(customer_ids)).all()
        
    elif search_type == 'date' and start_date:
        # Search by date range
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            if end_date:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end = start
            
            estimates = Estimate.query.filter(
                Estimate.estimate_date >= start,
                Estimate.estimate_date <= end
            ).all()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        return jsonify({'error': 'Invalid search parameters'}), 400
    
    result = []
    for estimate in estimates:
        customer = Customer.query.get(estimate.customer_id)
        result.append({
            'estimate_id': estimate.id,
            'quotation_no': estimate.quotation_no,
            'customer_name': customer.name,
            'customer_mobile': customer.mobile,
            'estimate_date': estimate.estimate_date.strftime('%Y-%m-%d'),
            'total_amount': estimate.total_amount
        })
    
    return jsonify(result)

@app.route('/estimates/new')
@allowed_users_only
def new_estimate():
    return render_template('estimate_form.html')

@app.route('/estimates/edit/<int:estimate_id>')
@allowed_users_only
def edit_estimate(estimate_id):
    # Check if estimate exists
    estimate = Estimate.query.get_or_404(estimate_id)
    return render_template('estimate_form.html', estimate_id=estimate_id, is_edit=True)

@app.route('/estimates/<int:estimate_id>')
@allowed_users_only
def view_estimate(estimate_id):
    estimate = Estimate.query.get_or_404(estimate_id)
    return render_template('estimate_view.html', estimate_id=estimate_id)

@app.route('/api/estimates/<int:estimate_id>', methods=['GET'])
@allowed_users_only
def get_estimate(estimate_id):
    estimate = Estimate.query.get_or_404(estimate_id)
    return jsonify(estimate.to_dict())

@app.route('/api/estimates', methods=['POST'])
@allowed_users_only
def create_estimate():
    data = request.json
    
    # Validate required fields
    if not data.get('customer_id') or not data.get('items') or len(data.get('items', [])) == 0:
        return jsonify({'error': 'Customer and at least one item are required'}), 400
    
    # Generate quotation number if not provided
    quotation_no = data.get('quotation_no')
    if not quotation_no:
        today = datetime.now().date()
        count = Estimate.query.filter(Estimate.estimate_date == today).count() + 1
        quotation_no = f"EST-{count:03d}-{today.strftime('%d%m%Y')}"
    else:
        # Check if quotation number already exists
        existing = Estimate.query.filter_by(quotation_no=quotation_no).first()
        if existing:
            return jsonify({'error': 'Quotation number already exists'}), 400
    
    # Create estimate
    estimate = Estimate(
        quotation_no=quotation_no,
        customer_id=data.get('customer_id'),
        estimate_date=datetime.now().date(),
        estimate_time=datetime.now().time(),
        total_amount=data.get('total_amount', 0)
    )
    
    db.session.add(estimate)
    db.session.flush()  # Get the estimate ID
    
    # Add estimate items
    for idx, item_data in enumerate(data.get('items', []), 1):
        # Check if item exists in database
        item_code = item_data.get('item_code')
        item = Item.query.filter_by(code=item_code).first()
        
        # If item doesn't exist or rate/picture is different, update or create
        if not item:
            item = Item(
                code=item_code,
                picture=item_data.get('picture', ''),
                rate=item_data.get('rate', 0)
            )
            db.session.add(item)
        elif item.rate != item_data.get('rate') or (item_data.get('picture') and item.picture != item_data.get('picture')):
            item.rate = item_data.get('rate', item.rate)
            if item_data.get('picture'):
                item.picture = item_data.get('picture')
        
        # Create estimate item
        estimate_item = EstimateItem(
            estimate_id=estimate.id,
            serial=idx,
            item_code=item_code,
            size=item_data.get('size', ''),
            area=item_data.get('area'),
            quantity=item_data.get('quantity', 0),
            unit=item_data.get('unit', 'Piece'),
            rate=item_data.get('rate', 0),
            amount=item_data.get('amount', 0),
            picture=item_data.get('picture', '')
        )
        
        db.session.add(estimate_item)
    
    db.session.commit()
    
    return jsonify(estimate.to_dict()), 201

@app.route('/api/estimates/<int:estimate_id>', methods=['PUT'])
@allowed_users_only
def update_estimate(estimate_id):
    estimate = Estimate.query.get_or_404(estimate_id)
    data = request.json
    
    # Validate required fields
    if not data.get('customer_id') or not data.get('items') or len(data.get('items', [])) == 0:
        return jsonify({'error': 'Customer and at least one item are required'}), 400
    
    # Check if quotation number changed and if the new one already exists
    if data.get('quotation_no') and data.get('quotation_no') != estimate.quotation_no:
        existing = Estimate.query.filter_by(quotation_no=data.get('quotation_no')).first()
        if existing and existing.id != estimate_id:
            return jsonify({'error': 'Quotation number already exists'}), 400
    
    # Update estimate
    if data.get('quotation_no'):
        estimate.quotation_no = data.get('quotation_no')
    
    estimate.customer_id = data.get('customer_id')
    estimate.total_amount = data.get('total_amount', 0)
    
    # Remove old estimate items
    EstimateItem.query.filter_by(estimate_id=estimate.id).delete()
    
    # Add new estimate items
    for idx, item_data in enumerate(data.get('items', []), 1):
        # Check if item exists in database
        item_code = item_data.get('item_code')
        item = Item.query.filter_by(code=item_code).first()
        
        # If item doesn't exist or rate/picture is different, update or create
        if not item:
            item = Item(
                code=item_code,
                picture=item_data.get('picture', ''),
                rate=item_data.get('rate', 0)
            )
            db.session.add(item)
        elif item.rate != item_data.get('rate') or (item_data.get('picture') and item.picture != item_data.get('picture')):
            item.rate = item_data.get('rate', item.rate)
            if item_data.get('picture'):
                item.picture = item_data.get('picture')
        
        # Create estimate item
        estimate_item = EstimateItem(
            estimate_id=estimate.id,
            serial=idx,
            item_code=item_code,
            size=item_data.get('size', ''),
            area=item_data.get('area'),
            quantity=item_data.get('quantity', 0),
            unit=item_data.get('unit', 'Piece'),
            rate=item_data.get('rate', 0),
            amount=item_data.get('amount', 0),
            picture=item_data.get('picture', '')
        )
        
        db.session.add(estimate_item)
    
    db.session.commit()
    
    return jsonify(estimate.to_dict())

@app.route('/api/items', methods=['GET'])
@allowed_users_only
def get_items():
    search_term = request.args.get('search', '')
    
    if search_term:
        items = Item.query.filter(Item.code.ilike(f'%{search_term}%')).all()
    else:
        items = Item.query.all()
    
    return jsonify([item.to_dict() for item in items])

@app.route('/api/upload_image', methods=['POST'])
@allowed_users_only
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({'filename': f"/static/images/items/{filename}"})
    
    return jsonify({'error': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


if __name__ == '__main__':
    # Create default admin user
    create_default_user()
    app.run(debug=True)
