from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

#Variables
mysql_config = {
    'user': 'Kevin',
    'password': 'kevin11',
    'host': 'localhost',
    'database': 'SubHub'}

signed_in = False

@app.route('/')
def home():
    return render_template('signin.html')

@app.route('/handle_signin',  methods=['POST', 'GET'])
def handle_signin():
    global signed_in
    if request.method == 'POST':
        username = request.form['signin_username']
        password = request.form['signin_password']

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=\"{}\" AND password=\"{}\";".format(username, password))

        if cur.fetchone():
            signed_in = True
            return redirect(url_for('user_data', username=username))
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

        cur.execute('CREATE TABLE {} (sub_name char(100), sub_price decimal(9,2), sub_purhcase_date date, sub_renewal_date int)'.format(username))

        #send user back to signin page
        return render_template('signin.html', account_creation="Account successfully created.")
    else:
        #signup page is served when getting handle_signup
        return render_template('signup.html')

@app.route('/user/<username>', methods=['POST', 'GET'])
def user_data(username):
    if signed_in == False:
        return redirect(url_for('handle_signin'))

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    cur.execute("SELECT * FROM {};".format(username))
    data = cur.fetchall()

    #sends all user data to the user.html page
    return render_template('user.html', data=data)
