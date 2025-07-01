from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///money_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(5).all()
    
    # Calculate basic stats
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_income = db.session.query(db.func.sum(Transaction.amount)).join(Category).filter(
        Transaction.user_id == current_user.id,
        Category.type == 'income',
        db.extract('month', Transaction.date) == current_month,
        db.extract('year', Transaction.date) == current_year
    ).scalar() or 0
    
    monthly_expenses = db.session.query(db.func.sum(Transaction.amount)).join(Category).filter(
        Transaction.user_id == current_user.id,
        Category.type == 'expense',
        db.extract('month', Transaction.date) == current_month,
        db.extract('year', Transaction.date) == current_year
    ).scalar() or 0
    
    return render_template('dashboard.html', 
                         transactions=recent_transactions,
                         monthly_income=monthly_income,
                         monthly_expenses=monthly_expenses,
                         balance=monthly_income - monthly_expenses)

@app.route('/transactions')
@login_required
def transactions():
    return render_template('transactions.html')

@app.route('/budgets')
@login_required
def budgets():
    return render_template('budgets.html')

# ===============================
# REST API ENDPOINTS
# ===============================

@app.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def api_transactions():
    if request.method == 'GET':
        # Get all transactions for current user
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        return jsonify([{
            'id': t.id,
            'amount': t.amount,
            'description': t.description,
            'date': t.date.isoformat(),
            'category_id': t.category_id,
            'category_name': t.category.name,
            'category_type': t.category.type,
            'category_color': t.category.color
        } for t in transactions])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            if not all(key in data for key in ['category_id', 'amount', 'date']):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Verify category belongs to valid categories
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Invalid category'}), 400
            
            # Create new transaction
            transaction = Transaction(
                user_id=current_user.id,
                category_id=data['category_id'],
                amount=float(data['amount']),
                description=data.get('description', ''),
                date=datetime.strptime(data['date'], '%Y-%m-%d').date()
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return jsonify({
                'message': 'Transaction created successfully',
                'transaction': {
                    'id': transaction.id,
                    'amount': transaction.amount,
                    'description': transaction.description,
                    'date': transaction.date.isoformat(),
                    'category_name': transaction.category.name
                }
            }), 201
            
        except ValueError as e:
            return jsonify({'error': 'Invalid data format'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create transaction'}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_transaction(transaction_id):
    # Get transaction belonging to current user
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'id': transaction.id,
            'amount': transaction.amount,
            'description': transaction.description,
            'date': transaction.date.isoformat(),
            'category_id': transaction.category_id,
            'category_name': transaction.category.name,
            'category_type': transaction.category.type
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update fields if provided
            if 'category_id' in data:
                category = Category.query.get(data['category_id'])
                if not category:
                    return jsonify({'error': 'Invalid category'}), 400
                transaction.category_id = data['category_id']
            
            if 'amount' in data:
                transaction.amount = float(data['amount'])
            
            if 'description' in data:
                transaction.description = data['description']
            
            if 'date' in data:
                transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            
            db.session.commit()
            
            return jsonify({
                'message': 'Transaction updated successfully',
                'transaction': {
                    'id': transaction.id,
                    'amount': transaction.amount,
                    'description': transaction.description,
                    'date': transaction.date.isoformat(),
                    'category_name': transaction.category.name
                }
            })
            
        except ValueError as e:
            return jsonify({'error': 'Invalid data format'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update transaction'}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(transaction)
            db.session.commit()
            return jsonify({'message': 'Transaction deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete transaction'}), 500

@app.route('/api/categories', methods=['GET'])
@login_required
def api_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'type': c.type,
        'color': c.color
    } for c in categories])

@app.route('/api/budgets', methods=['GET', 'POST'])
@login_required
def api_budgets():
    if request.method == 'GET':
        budgets = Budget.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': b.id,
            'category_id': b.category_id,
            'category_name': b.category.name,
            'amount': b.amount,
            'month': b.month,
            'year': b.year,
            'created_at': b.created_at.isoformat()
        } for b in budgets])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            if not all(key in data for key in ['category_id', 'amount', 'month', 'year']):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Verify category exists
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Invalid category'}), 400
            
            # Check if budget already exists for this category/month/year
            existing_budget = Budget.query.filter_by(
                user_id=current_user.id,
                category_id=data['category_id'],
                month=data['month'],
                year=data['year']
            ).first()
            
            if existing_budget:
                return jsonify({'error': 'Budget already exists for this category and month'}), 400
            
            # Create new budget
            budget = Budget(
                user_id=current_user.id,
                category_id=data['category_id'],
                amount=float(data['amount']),
                month=int(data['month']),
                year=int(data['year'])
            )
            
            db.session.add(budget)
            db.session.commit()
            
            return jsonify({
                'message': 'Budget created successfully',
                'budget': {
                    'id': budget.id,
                    'category_name': budget.category.name,
                    'amount': budget.amount,
                    'month': budget.month,
                    'year': budget.year
                }
            }), 201
            
        except ValueError as e:
            return jsonify({'error': 'Invalid data format'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create budget'}), 500

@app.route('/api/budgets/<int:budget_id>', methods=['PUT', 'DELETE'])
@login_required
def api_budget(budget_id):
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first()
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            if 'amount' in data:
                budget.amount = float(data['amount'])
            
            if 'month' in data:
                budget.month = int(data['month'])
            
            if 'year' in data:
                budget.year = int(data['year'])
            
            db.session.commit()
            
            return jsonify({
                'message': 'Budget updated successfully',
                'budget': {
                    'id': budget.id,
                    'category_name': budget.category.name,
                    'amount': budget.amount,
                    'month': budget.month,
                    'year': budget.year
                }
            })
            
        except ValueError as e:
            return jsonify({'error': 'Invalid data format'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update budget'}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(budget)
            db.session.commit()
            return jsonify({'message': 'Budget deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete budget'}), 500

@app.route('/api/stats/spending-by-category')
@login_required
def api_spending_by_category():
    try:
        # Get month/year from query params or use current
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Query spending by category for the specified month
        results = db.session.query(
            Category.name,
            Category.color,
            db.func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            Transaction.user_id == current_user.id,
            Category.type == 'expense',
            db.extract('month', Transaction.date) == month,
            db.extract('year', Transaction.date) == year
        ).group_by(Category.id).all()
        
        return jsonify([{
            'category': r.name,
            'amount': float(r.total),
            'color': r.color
        } for r in results])
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch spending data'}), 500

@app.route('/api/stats/monthly-summary')
@login_required
def api_monthly_summary():
    try:
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Calculate income and expenses
        income = db.session.query(db.func.sum(Transaction.amount)).join(Category).filter(
            Transaction.user_id == current_user.id,
            Category.type == 'income',
            db.extract('month', Transaction.date) == month,
            db.extract('year', Transaction.date) == year
        ).scalar() or 0
        
        expenses = db.session.query(db.func.sum(Transaction.amount)).join(Category).filter(
            Transaction.user_id == current_user.id,
            Category.type == 'expense',
            db.extract('month', Transaction.date) == month,
            db.extract('year', Transaction.date) == year
        ).scalar() or 0
        
        return jsonify({
            'month': month,
            'year': year,
            'income': float(income),
            'expenses': float(expenses),
            'balance': float(income - expenses),
            'transaction_count': Transaction.query.filter(
                Transaction.user_id == current_user.id,
                db.extract('month', Transaction.date) == month,
                db.extract('year', Transaction.date) == year
            ).count()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch monthly summary'}), 500

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