from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=True)
    mobile = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with estimates
    estimates = db.relationship('Estimate', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'mobile': self.mobile,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    picture = db.Column(db.String(255), nullable=True)
    rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Item {self.code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'picture': self.picture,
            'rate': self.rate,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Estimate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quotation_no = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    estimate_date = db.Column(db.Date, default=datetime.utcnow().date)
    estimate_time = db.Column(db.Time, default=datetime.utcnow().time)
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with estimate items
    items = db.relationship('EstimateItem', backref='estimate', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Estimate {self.quotation_no}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'quotation_no': self.quotation_no,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'customer_mobile': self.customer.mobile if self.customer else None,
            'estimate_date': self.estimate_date.strftime('%Y-%m-%d'),
            'estimate_time': self.estimate_time.strftime('%H:%M:%S'),
            'total_amount': self.total_amount,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [item.to_dict() for item in self.items]
        }

class EstimateItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estimate_id = db.Column(db.Integer, db.ForeignKey('estimate.id'), nullable=False)
    serial = db.Column(db.Integer, nullable=False)
    item_code = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(100), nullable=True)
    area = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='Piece')  # Box or Piece
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<EstimateItem {self.serial} - {self.item_code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'estimate_id': self.estimate_id,
            'serial': self.serial,
            'item_code': self.item_code,
            'size': self.size,
            'area': self.area,
            'quantity': self.quantity,
            'unit': self.unit,
            'rate': self.rate,
            'amount': self.amount,
            'picture': self.picture
        }

def init_db(app):
    db.init_app(app)
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
