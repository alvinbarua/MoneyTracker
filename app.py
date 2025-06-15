from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-later'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)