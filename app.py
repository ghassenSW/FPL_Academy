from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
import os

app = Flask(__name__)
app.secret_key = 'f3082ef12d47bf71416425c7eef8d573'

DATABASE = 'users.db'
if not os.path.exists(DATABASE):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        ''')
        conn.commit()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username = ? AND password = ?', (username, password))
            account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]  # account[0] is the ID
            session['username'] = account[1]  # account[1] is the username
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
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
            account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO accounts (username, password, email) VALUES (?, ?, ?)', (username, password, email))
                conn.commit()
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
