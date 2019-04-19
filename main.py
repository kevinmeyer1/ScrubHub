from flask import Flask, render_template, request, redirect, url_for, session, app
import mysql.connector, ssl, smtplib, sys, json
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = 'some secret key?' #This is needed to make my session work. what do i do for this?

#Variables -- database needs to be changed to ScrubHub as reflection of the project name

#reads variables from config.json file
with open('./config.json') as json_file:
    json_data = json.load(json_file)

#sets config values for mysql
mysql_config = {
    'user': json_data['user'],
    'password': json_data['password'],
    'host': json_data['host'],
    'database': json_data['database']
}

#Home page, shows up when you go to localhost:5000
@app.route('/')
def home():
    session['logged_in'] = False
    return render_template('frontPage.html')

#signs in user when they exist in the users table -- may change in the future with database
@app.route('/Sign_In',  methods=['POST', 'GET'])
def Sign_In():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute(f"SELECT email, name, password FROM users WHERE email='{email}' AND password='{password}';")

        if cur.fetchone():
            session['email'] = email
            session['logged_in'] = True
            cur.execute(f"SELECT name FROM users WHERE email='{email}'")
            session['name'] = cur.fetchone()[0]
            return redirect(url_for('user_data'))
        else:
            return render_template('login.html', error_message="Incorrect login credentials.")
    else:
        return render_template('login.html')

#handle signup and creates a new user table -- may change in the future with database
@app.route('/Sign_Up', methods=['POST', 'GET'])
def Sign_Up():
    if request.method == 'POST':
        #send user back to signin page
        return render_template('frontPage.html')
    else:
        #signup page is served when getting Sign_Up
        return render_template('createAccount.html')

#saves personal information in signup sequence
@app.route('/notification_method', methods=['POST'])
def notification_method():
    complete = True

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone_number = request.form['phone_number']
    terms_and_conditions = request.form.get('terms_and_conditions')

    session['personal'] = [name, email, phone_number, password, terms_and_conditions]

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()

    #Check if user already exists
    cur.execute(f"SELECT * FROM users WHERE email='{email}';")
    if cur.fetchone():
        #if it gets a result, the email exists
        return render_template('createAccount.html', error_message="An account with the previously entered email already exists. Login or use a different email.")

    #make sure all inputs are filled out or checked
    for x in session['personal']:
        if x == "":
            complete = False

    #return user to creat account if there are inputs missing
    if complete == False:
        return render_template('createAccount.html', error_message="Please make sure to fill out all inputs and check the terms and conditions box.")

    return render_template('notificationMethod.html')

#saves notif method in signup sequence
@app.route('/select_subscriptions', methods=['POST'])
def select_subscriptions():
    notification_method = request.form['notification_method']
    session['notification_method'] = notification_method
    return render_template('manageSubscription.html')

#grabs all the subscriptions for a user - may change in the future with database
@app.route('/user', methods=['POST', 'GET'])
def user_data():
    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()

    if request.method == 'POST':
        session['logged_in'] = True
        session['email'] = session['personal'][1]
        session['name'] = session['personal'][0]
        cur.execute(f"INSERT INTO users VALUES ('{session['personal'][0]}', '{session['personal'][1]}', '{session['personal'][2]}', '{session['notification_method']}', '{session['personal'][3]}')")
        conn.commit()
        session.pop('personal')
        session.pop('notification_method')

    if session['logged_in'] == False:
        return redirect(url_for('Sign_In'))

    cur.execute(f"SELECT * FROM subscription where email='{session['email']}';")
    data = cur.fetchall()

    #sends all user data to the user.html page
    return render_template('home.html', data=data, email=session['email'], name=session['name'])

#adds a subscription - simplified for now
@app.route('/add_subscription', methods=['POST', 'GET'])
def add_subscription():
    if session['logged_in'] == False:
        return redirect(url_for('Sign_In'))

    if request.method == 'POST':
        sub_name = request.form['sub_name']
        sub_price = request.form['sub_price']
        sub_renewal_date = request.form['sub_renewal_date']
        notification_type = request.form['notification_type']
        subscription_type = request.form['sub_type']
        active_sub = 1

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO subscription VALUES ('{session['email']}', '{sub_name}', {sub_price}, {sub_renewal_date}, '{notification_type}', '{subscription_type}', 1);")
        conn.commit()

        return redirect(url_for('user_data', email=session['email']))
    else:
        return render_template('newSubscription.html', email=session['email'])

#log out function, logs them out and sends them back to signin page. removes identification from session
@app.route('/logout')
def logout():
    session.pop('email')
    session.pop('name')
    session['logged_in'] = False
    return redirect(url_for('home'))

#takes user to manage a single subscription
@app.route('/manage_subscription')
def manage_subscription():

    #code to be added in the future

    return render_template('homeManage.html', name=session['name'])

#response from confirm/renew button in manage page
@app.route('/confirm_renewal')
def renew_subscription():

    #Code to be added in the future

    return render_template('homeConfirm.html', name=session['name'])

#this is the set 404 page so when a user tries to go somewhere that doesnt exist we can just send them this
@app.errorhandler(404)
def page_not_found(e):
    return render_template('old/404.html')

#grabs users phone number and sends a text to them
@app.route('/test_text')
def test_text():
    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    cur.execute(f"select phone_number from users where email='{session['email']}'")
    phone_number = cur.fetchone()[0]
    send_text(phone_number, "[Subscription Placeholder]", "[Date Placeholder]")
    return redirect(url_for('user_data'))

#function to demonstrate email capabilites
@app.route('/test_email')
def test_email():
    send_email("[Subscription Placerholder]", session['name'], '[Date Placeholder]', session['email'])
    return redirect(url_for('user_data'))

#this will send a text when called
def send_text(phone_number, sub_name, sub_renewal_date):
    client = Client(json_data['twilio_sid'], json_data['twilio_auth_token'])
    message = client.messages.create(
        body = f"Reminder: Your subscription to {sub_name} is set to renew on {sub_renewal_date}",
        from_ = "+19196291256",
        to = f"+1{phone_number}"
    )
    return

#this will send an email when called - not actually used in site yet
def send_email(sub_name, name, sub_renewal_date, email_address):
    port = 465 #i can probably change this who knows
    password = 'kPm130806!' #password for scrubhubreminders@gmail.com
    smtp_server = "smtp.gmail.com" #this is needed and doesnt change
    sender_email = 'ScrubHubReminders@gmail.com'
    message = f"""\
    ScrubHubReminders
    \n
    Subject: Reminder - Your {sub_name} subscription is renewing soon!
    \n
    Dear {name},

    Your subscription {sub_name} is set to renew on {sub_renewal_date}.

    From your friends at ScrubHub.
    """
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, email_address, message)
        server.quit()


#-------------------------------------------------------------------------------------------------
#           UNUSED FUNCTIONS BELOW - POSSIBLE IMPLEMENTATION OPTIONS
#-------------------------------------------------------------------------------------------------

##### Here we will keep our list of subscription types - eh maybe not, that might be done within the html
def get_sub_type(name):
    type = ""
    educational = ['chegg', 'zybooks'] # lists imcomplete - probably a bad idea
    entertainment = ['netflix', 'hulu', 'amazon']

    if name in educational:
        type = 'Education'
    elif name in entertainment:
        type = 'Entertainment'
    else:
        type = 'Other'

    return type

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

    cur.execute(f"SELECT * FROM users WHERE email='{session['email']}';")
    user_data = cur.fetchall()
    #this is all of the users personal information

    cur.execute(f"SELECT * FROM subscription WHERE email='{session['email']}';")
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

    cur.execute(f"SELECT sub_name FROM subscription where email='{session['email']}';")
    sub_data = cur.fetchall()

    return sub_data


def cancel_subscription():
    #here we get the subscription, change its active sub field to false or whatever
    return
