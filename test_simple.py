from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Flask is working! 🎉</h1><p>Your MoneyTracker app should work too.</p>'

if __name__ == '__main__':
    app.run(debug=True, port=8001)