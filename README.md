# 💰 MoneyTracker

A comprehensive personal finance management web application that helps you track expenses, manage budgets, and gain insights into your spending habits.

## 🚀 Live Demo

**Try it now**: [https://moneytracker-6s6i.onrender.com/](https://moneytracker-6s6i.onrender.com/)

*You can create an account to start tracking your finances today!*

## 🌟 What It Does

MoneyTracker is a full-featured financial dashboard that allows you to:

- **Track Transactions**: Record income and expenses with detailed categorization
- **Set Budgets**: Create monthly budgets for different spending categories
- **Visualize Spending**: Get insights with spending analytics and category breakdowns
- **Secure Authentication**: User registration and login with password hashing
- **REST API**: Complete API endpoints for programmatic access to your financial data
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🏗️ Tech Stack & Why I Chose It

### Backend
- **Flask** (Python web framework)
  - *Why*: Lightweight, flexible, and perfect for building APIs quickly
  - Easy to learn and deploy
  - Great for prototyping and small-to-medium applications

- **SQLAlchemy** (ORM)
  - *Why*: Simplifies database operations with Python objects
  - Provides data validation and relationship management
  - Makes database queries more readable and maintainable

- **Flask-Login** (Authentication)
  - *Why*: Battle-tested user session management
  - Handles login state, user sessions, and authentication decorators
  - Integrates seamlessly with Flask

- **Werkzeug** (Security)
  - *Why*: Provides secure password hashing
  - Industry-standard security practices for user credentials

### Frontend
- **Bootstrap 5** 
  - *Why*: Rapid UI development with responsive design
  - Professional-looking components out of the box
  - Extensive icon library (Bootstrap Icons)

- **HTML/CSS/JavaScript**
  - *Why*: Simple, fast, and works everywhere
  - No complex build process or framework overhead
  - Direct manipulation of DOM for dynamic content

### Database
- **SQLite** (Development) / **PostgreSQL** (Production)
  - *Why*: SQLite for easy local development without setup
  - PostgreSQL for production scalability and reliability

### Deployment
- **Render** (Cloud Platform)
  - *Why*: Simple deployment with automatic builds
  - Built-in PostgreSQL database hosting
  - Free tier available for personal projects

## 🚀 Features

### Core Functionality
- **User Management**: Registration, login, logout with secure password hashing
- **Transaction Management**: Add, edit, delete income and expense transactions
- **Category System**: Pre-built categories with custom colors for visual organization
- **Budget Tracking**: Set monthly budgets and track spending against limits
- **Dashboard**: Real-time overview of monthly income, expenses, and balance

### API Endpoints
- `GET/POST /api/transactions` - Manage transactions
- `GET/PUT/DELETE /api/transactions/<id>` - Individual transaction operations
- `GET /api/categories` - List all available categories
- `GET/POST /api/budgets` - Budget management
- `GET /api/stats/spending-by-category` - Category spending analytics
- `GET /api/stats/monthly-summary` - Monthly financial summary

### Security Features
- Password hashing with Werkzeug
- User session management
- Protected routes requiring authentication
- User data isolation (users only see their own data)

## 📦 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd money-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the app**
   - Open http://localhost:5000 in your browser
   - Register a new account or login

## 🗂️ Project Structure

```
money-tracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── render.yaml           # Deployment configuration
├── instance/
│   └── money_tracker.db  # SQLite database (auto-generated)
└── templates/            # HTML templates
    ├── base.html         # Base template with Bootstrap
    ├── index.html        # Landing page
    ├── dashboard.html    # Main dashboard
    ├── transactions.html # Transaction management
    ├── budgets.html      # Budget management
    ├── login.html        # User login
    └── register.html     # User registration
```

## 💡 Key Design Decisions

1. **Flask over Django**: Chose Flask for its simplicity and lightweight nature
2. **SQLite for development**: No setup required, perfect for local development
3. **Bootstrap for UI**: Rapid prototyping with professional appearance
4. **RESTful API design**: Makes the app extensible for mobile apps or integrations
5. **Category-based organization**: Provides structure without being overly complex
6. **Monthly budget tracking**: Focuses on practical, actionable financial planning

## 🔒 Security Considerations

- Passwords are hashed using Werkzeug's secure methods
- User sessions are managed securely with Flask-Login
- Environment variables for sensitive configuration
- User data isolation - users can only access their own financial data

## 🌐 Deployment

The app is configured for deployment on Render with:
- Automatic builds from Git
- Environment variable management
- PostgreSQL database provisioning
- HTTPS by default

## 🛠️ Future Enhancements

- Data export (CSV, PDF reports)
- Recurring transaction templates
- Financial goal setting and tracking
- Mobile app integration via REST API
- Advanced charts and analytics
- Multi-currency support

---

