from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import re
import os 
from pymongo import MongoClient
from datetime import datetime
from price_change import get_price_change_text
from injury_updates import get_injury_updates_text

app = Flask(__name__)
app.secret_key = 'f3082ef12d47bf71416425c7eef8d573'

from dotenv import load_dotenv
load_dotenv()
MONGODB_URI=os.getenv('MONGODB_URI')

# MONGODB_URI=os.environ.get('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['accounts']
price_change_db=db['price_change']
injury_updates_db=db['injuries']

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
    price_changed=price_change_db.find_one()
    risers={'players':[price_changed['web_name'][i] for i in range(len(price_changed['web_name'])) if price_changed['cost_change_event'][i]==1],
            'cost':[price_changed['now_cost'][i] for i in range(len(price_changed['now_cost'])) if price_changed['cost_change_event'][i]==1],
            'team':[price_changed['team'][i] for i in range(len(price_changed['team'])) if price_changed['cost_change_event'][i]==1]}
    fallers={'players':[price_changed['web_name'][i] for i in range(len(price_changed['web_name'])) if price_changed['cost_change_event'][i]==-1],
            'cost':[price_changed['now_cost'][i] for i in range(len(price_changed['now_cost'])) if price_changed['cost_change_event'][i]==-1],
            'team':[price_changed['team'][i] for i in range(len(price_changed['team'])) if price_changed['cost_change_event'][i]==-1]}
    current_date=datetime.now()
    day=f'{str(current_date.day)}/{str(current_date.month)}/{str(current_date.year)}'
    return render_template("price_change.html",risers=risers,fallers=fallers,day=day)

@app.route("/injury_updates")
def injury_updates():
    injuries=list(injury_updates_db.find())
    current_date=datetime.now()
    day=f'{str(current_date.day)}/{str(current_date.month)}/{str(current_date.year)}'
    return render_template("injury_updates.html",injuries=injuries,day=day)

@app.route('/get-copy-price-change', methods=['GET'])
def get_copy_price_change():
    text_to_copy = get_price_change_text(price_change_db)
    return jsonify({'text': text_to_copy})  

@app.route('/get-copy-injury-updates', methods=['GET'])
def get_copy_injury_updates():
    id = request.args.get('id', type=int)
    text_to_copy = get_injury_updates_text(injury_updates_db,id)
    return jsonify({'text': text_to_copy})

@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html',session=session)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
