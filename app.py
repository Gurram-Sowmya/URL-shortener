import os
from flask import Flask, render_template, request, flash, redirect
import pyshorteners
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'secret_key'

# Configure the database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
Migrate(app, db)

# Define the URL model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(100), nullable=False)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(url)
        flash('Shortened URL: {}'.format(short_url))

        # Create a new URL object and save it to the databases
        new_url = URL(original_url=url, short_url=short_url)
        db.session.add(new_url)
        db.session.commit()
        copy_button = '<button onclick="copyToClipboard(\'{}\')">Copy</button>'.format(short_url)
        return short_url + copy_button

    return render_template('index.html')

@app.route('/history')
def history():
    # Retrieve all URLs from the database and pass them to the template
    urls = URL.query.order_by(URL.id.desc()).all()
    return render_template('history.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)
