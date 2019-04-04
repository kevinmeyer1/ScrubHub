from flask import Flask, render_template, request, redirect, url_for, session, app
import mysql.connector, ssl, smtplib, schedule, time, sys
from datetime import datetime
from twilio.rest import Client


######madj had to change it to mysql-connector-python for msq connector to work#####

###### instead of check_for_reminders, I am going to have a test button that allows users to get an email or text vs
###### having to wait for one to show up, better for demos and presentations.

app = Flask(__name__)
app.secret_key = 'some secret key?' #This is needed to make my session work. what do i do for this?

#Variables -- database needs to be changed to ScrubHub as reflection of the project name
mysql_config = {
    'user': 'Kevin',
    'password': 'kevin11',
    'host': 'localhost',
    'database': 'Scrubhub'
}

#Variables needed for the texting function
twilio_sid = 'ACd28df43aa8b7a9d5ffe1fb74d98be3a6'
twilio_auth_token = '7188d25025fbef6d7838eed5dc1a9e4f'

#---Working----- fix subject
#send_email("Chegg", 'Kevin', 'Meyer', '3/25', 'kpm216@gmail.com')

#----Working----
#send_text("9194515213", 'Chegg', '3/25')

#Home page, shows up when you go to localhost:5000
@app.route('/')
def home():
    session['logged_in'] = False
    return render_template('frontPage.html')

##### Here we will keep our list of subscription types
def get_sub_type(name):
    type = ""
    educational = ['chegg', 'zybooks']
    entertainment = ['netflix', 'hulu', 'amazon']

    if name in educational:
        type = 'Education'
    elif name in entertainment:
        type = 'Entertainment'
    else:
        type = 'Other'

    return type

#signs in user when they exist in the users table -- may change in the future with database
@app.route('/handle_signin',  methods=['POST', 'GET'])
def handle_signin():
    if request.method == 'POST':
        username = request.form['signin_username']
        password = request.form['signin_password']

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute(f"SELECT username, password FROM users WHERE username='{username}' AND password='{password}';")

        if cur.fetchone():
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('user_data'))
        else:
            return render_template('login.html', error_message="Incorrect login credentials.")
    else:
        return render_template('login.html')

#handle signup and creates a new user table -- may change in the future with database
@app.route('/handle_signup', methods=['POST', 'GET'])
def handle_signup():
    if request.method == 'POST':
        #method is post, data is recieved
        form_username = request.form['username']
        form_password = request.form['password']
        form_phone_number = request.form['phone_number']
        form_email = request.form['email']

        #Add new user to users table
        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        #Add other stuff to the table from front end
        cur.execute(f"INSERT INTO users (username, email, phone_number, password) \
                      VALUES ('{form_username}', '{form_email}', '{form_phone_number}', '{form_password}');")
        conn.commit()

        #send user back to signin page
        return render_template('frontPage.html', account_creation="Account successfully created.")
    else:
        #signup page is served when getting handle_signup
        return render_template('createAccount.html')

#grabs all the subscriptions for a user - may change in the future with database
@app.route('/user', methods=['POST', 'GET'])
def user_data():
    if session['logged_in'] == False:
        return redirect(url_for('handle_signin'))

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM subscription where USERNAME='{session['username']}';")
    data = cur.fetchall()

    #sends all user data to the user.html page
    return render_template('user.html', data=data, username=session['username'])

#adds a subscription - will change in future with database - extra feilds and stuff
@app.route('/add_subscription', methods=['POST', 'GET'])
def add_subscription():
    if session['logged_in'] == False:
        return redirect(url_for('handle_signin'))

    if request.method == 'POST':
        sub_name = request.form['sub_name']
        sub_price = request.form['sub_price']
        sub_purchase_date = request.form['sub_purchase_date']
        sub_renewal_date = request.form['sub_renewal_date']
        notification_type = request.form['notification_type']
        subscription_type = get_sub_type(sub_name);
        active_sub = 1

        ######
        # Need to do a bunch of error handling here at some point - dont use Date for sql or just fuck with the formatting
        ######

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO subscription ('{session['username']}', '{sub_name}', {sub_price}, {sub_purchase_date}, {sub_renewal_date}, '{notification_type}', '{subscription_type}', {active_sub});")
        conn.commit()

        return redirect(url_for('user_data', username=session['username']))
    else:
        return render_template('add_subscription.html', username=session['username'])

#log out function, logs them out and sends them back to signing
@app.route('/logout')
def logout():
    session.pop('username')
    session['logged_in'] = False
    return redirect(url_for('handle_signin'))

#this is the set 404 page so when a user tries to go somewhere that doesnt exist we can just send them this
#@app.errorhandler(404)
#def page_not_found(e):
    #return render_template('404.html')

#this will send a text when called - not actually used in site yet
def send_text(phone_number, sub_name, sub_renewal_date):
    client = Client(twilio_sid, twilio_auth_token)
    message = client.messages.create(
        body = f"Reminder: Your subscription to {sub_name} is set to renew on {sub_renewal_date}",
        from_ = "+19196291256",
        to = f"+1{phone_number}"
    )
    return

#this will send an email when called - not actually used in site yet
def send_email(sub_name, first_name, last_name, sub_renewal_date, email_address):
    port = 465 #i can probably change this who knows
    password = 'kPm130806!' #password for scrubhubreminders@gmail.com
    smtp_server = "smtp.gmail.com" #this is needed and doesnt change
    sender_email = 'ScrubHubReminders@gmail.com'
    message = f"""\
    ScrubHubReminders
    \n
    Subject: Reminder - Your {sub_name} subscription is renewing soon!
    \n
    Dear {first_name} {last_name},

    Your subscription {sub_name} is set to renew on {sub_renewal_date}.

    From your friends at ScrubHub.
    """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, email_address, message)
        server.quit()

# here we check each day if users in our database have subscriptions that are renewing soon, if so we send them an email or text
def check_for_reminders():
    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()

    cur.execute('SELECT username FROM users;')
    data = cur.fetchall()
    for row in data:
        '''
        here Im going to get each usesrname in our users table
        then for each username, im going to call their table and grab their subscriptions and renewal dates
        if the renewal date is one day from today, it will send them a reminder
        if they match up, i use the method of reminder to either
        send_text() or send_email()
        '''
    return

# here we get all personal user information, name, location, profile picture, so we can send it to the front end for it to display
#we also grab and add up the amounts for each of our sub types
def get_user_profile():
    entertainment_amount = 0;
    education_amount = 0;
    #these are the only two things we have as of now

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM users WHERE username='{session['userame']}';")
    user_data = cur.fetchall()
    #this is all of the users personal information

    cur.execute(f"SELECT * FROM subscription WHERE username='{session['username']}';")
    sub_data = cur.fetchall()

    for row in sub_data:
        if (row[6] == "entertainment"):
            entertainment_amount += row[2]
        elif (row[6] == "education"):
            education_amount += row[2]

    return (user_data, entertainment_amount, education_amount)

#Get a list of all of the subscriptions a user has.
def get_user_subscriptions():
    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()

    cur.execute(f"SELECT sub_name FROM subscription where username='{session['username']}';")
    sub_data = cur.fetchall()

    return sub_data


def cancel_subscription():
    #here we get the subscription, change its active sub field to false or whatever

    return

#this stuff runs the check_for_reminders function every day
#schedule.every().day.do(check_for_reminders)

#i think this is a needed part of the schedule thing, not really sure it was on the internet
#while True:
    #schedule.run_pending()
