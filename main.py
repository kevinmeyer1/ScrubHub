from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

#Variables
mysql_config = {
    'user': 'Kevin',
    'password': 'kevin11',
    'host': 'localhost',
    'database': 'SubHub'}

@app.route('/')
def home():
    return render_template('signin.html')

@app.route('/handle_signin',  methods=['POST'])
def handle_signin():
    username = request.form['signin_username']
    password = request.form['signin_password']

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM users WHERE username=\"{}\" AND password=\"{}\";".format(username, password))

    if cur.fetchone():
        return render_template('success.html')
    else:
        return render_template('signin.html', error_message="Incorrect login credentials.")

@app.route('/handle_signup', methods=['POST', 'GET'])
def handle_signup():
    username = request.form['signup_username']
    password = request.form['signup_password']

    #add entry to users table
    #create table named what the username is
    return ""



# winpty mysql -u Kevin -p
# to login to mysql from windows git bash
