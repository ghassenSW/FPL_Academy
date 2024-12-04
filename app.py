from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
import os 
from pymongo import MongoClient
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = 'f3082ef12d47bf71416425c7eef8d573'

load_dotenv()
MONGODB_URI=os.environ.get('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['accounts']

if 'accounts' not in db.list_collection_names():
    db.create_collection('accounts')
    collection.create_index('username', unique=True)
    collection.create_index('password', unique=True)
    collection.create_index('email', unique=True)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = collection.find_one({'username': username, 'password': password})

        if account:
            session['loggedin'] = True
            session['id'] = str(account['_id'])  # MongoDB uses ObjectId
            session['username'] = account['username']
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = collection.find_one({'username': username})

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            collection.insert_one({'username': username, 'password': password, 'email': email})
            msg = 'You have successfully registered!'
            return render_template('login.html')
    return render_template('register.html', msg=msg)

@app.route("/price_change")
def price_change():
    return render_template("price_change.html")

@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html',session=session)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
