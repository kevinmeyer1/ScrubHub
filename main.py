from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'some secret key?' #what do i do for this?

#Variables
mysql_config = {
    'user': 'Kevin',
    'password': 'kevin11',
    'host': 'localhost',
    'database': 'SubHub'}

@app.route('/')
def home():
    session['logged_in'] = False
    return render_template('signin.html')

@app.route('/handle_signin',  methods=['POST', 'GET'])
def handle_signin():
    if request.method == 'POST':
        username = request.form['signin_username']
        password = request.form['signin_password']

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=\"{}\" AND password=\"{}\";".format(username, password))

        if cur.fetchone():
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('user_data'))
        else:
            return render_template('signin.html', error_message="Incorrect login credentials.")
    else:
        return render_template('signin.html')

@app.route('/handle_signup', methods=['POST', 'GET'])
def handle_signup():
    if request.method == 'POST':
        #method is post, data is recieved
        username = request.form['signup_username']
        password = request.form['signup_password']

        #Add new user to users table
        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (\"{}\", \"{}\");".format(username, password))
        conn.commit()

        cur.execute('CREATE TABLE {} (sub_name char(100), sub_price decimal(9,2), sub_purchase_date date, sub_renewal_date int)'.format(username))

        #send user back to signin page
        return render_template('signin.html', account_creation="Account successfully created.")
    else:
        #signup page is served when getting handle_signup
        return render_template('signup.html')

@app.route('/user', methods=['POST', 'GET'])
def user_data():
    if session['logged_in'] == False:
        return redirect(url_for('handle_signin'))

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    cur.execute("SELECT * FROM {};".format(session['username']))
    data = cur.fetchall()

    #sends all user data to the user.html page
    return render_template('user.html', data=data, username=session['username'])

@app.route('/add_subscription', methods=['POST', 'GET'])
def add_subscription():
    if session['logged_in'] == False:
        return redirect(url_for('handle_signin'))

    if request.method == 'POST':
        sub_name = request.form['sub_name']
        sub_price = request.form['sub_price']
        sub_purchase_date = request.form['sub_purchase_date']
        sub_renewal_date = request.form['sub_renewal_date']

        ######
        # Need to do a bunch of error handling here at some point - dont use Date for sql or just fuck with the formatting
        ######

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute("INSERT INTO {} (sub_name, sub_price, sub_purchase_date, sub_renewal_date) VALUES (\"{}\", {}, \"{}\", {});"
            .format(session['username'], sub_name, sub_price, sub_purchase_date, sub_renewal_date))
        conn.commit()

        return redirect(url_for('user_data', username=session['username']))
    else:
        return render_template('add_subscription.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username')
    session['logged_in'] = False
    return redirect(url_for('handle_signin'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
