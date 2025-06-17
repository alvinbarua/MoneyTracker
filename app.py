from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///money_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    color = db.Column(db.String(7), default='#007bff')  # Hex color for charts
    
    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.amount} - {self.description}>'

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Budget {self.amount} for {self.month}/{self.year}>'

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/test-db')
def test_db():
    """Test route to verify database setup"""
    try:
        # Test database connection
        users_count = User.query.count()
        categories_count = Category.query.count()
        transactions_count = Transaction.query.count()
        
        return f"""
        <h2>Database Test Results</h2>
        <p>Users: {users_count}</p>
        <p>Categories: {categories_count}</p>
        <p>Transactions: {transactions_count}</p>
        <p>✅ Database is working!</p>
        <a href="/">Back to Home</a>
        """
    except Exception as e:
        return f"❌ Database error: {str(e)}"

def init_db():
    """Initialize database and create default categories"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default categories if they don't exist
        if not Category.query.first():
            default_categories = [
                ('Salary', 'income', '#28a745'),
                ('Freelance', 'income', '#20c997'),
                ('Investment', 'income', '#17a2b8'),
                ('Food & Dining', 'expense', '#dc3545'),
                ('Transportation', 'expense', '#fd7e14'),
                ('Entertainment', 'expense', '#6f42c1'),
                ('Utilities', 'expense', '#ffc107'),
                ('Healthcare', 'expense', '#e83e8c'),
                ('Shopping', 'expense', '#6c757d'),
                ('Education', 'expense', '#007bff'),
            ]
            
            for name, category_type, color in default_categories:
                category = Category(name=name, type=category_type, color=color)
                db.session.add(category)
            
            try:
                db.session.commit()
                print("✅ Default categories created successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating categories: {e}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)