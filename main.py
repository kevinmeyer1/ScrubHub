from flask import Flask, render_template, request, redirect, url_for, session, app
import mysql.connector, ssl, smtplib, sys, json
from decimal import *
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

        if email == "" or password == "":
            return render_template('login.html', error_message="Missing required values.")

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
    notification_method = "text"
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
        cur.execute(f"INSERT INTO subscription VALUES ('{session['email']}', 'Netflix', '8.99', '1/1', 'Text', 'Entertainment', 1);")
        conn.commit()
        session.pop('personal')
        session.pop('notification_method')

    if session['logged_in'] == False:
        return redirect(url_for('Sign_In'))

    cur.execute(f"SELECT * FROM subscription where email='{session['email']}';")
    data = cur.fetchall()

    profile = get_user_profile()
    #sends all user data to the user.html page
    return render_template('home.html', data=data, email=session['email'], name=session['name'], entertainment_amount=profile[0],
        education_amount=profile[1], total_sub_amount=profile[2], total_subs=profile[3], active_subs=profile[4], entertainment_subs=profile[5],
        education_subs=profile[6])

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

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO subscription VALUES ('{session['email']}', '{sub_name}', {sub_price}, {sub_renewal_date}, '{notification_type}', '{subscription_type}', 1);")
        conn.commit()

        return redirect(url_for('user_data', email=session['email'], name=session['name']))
    else:
        amounts = get_user_profile()
        return render_template('newSubscription.html', email=session['email'], name=session['name'], entertainment_amount=amounts[0],
            education_amount=amounts[1], total_sub_amount=amounts[2], total_subs=amounts[3])

#log out function, logs them out and sends them back to signin page. removes identification from session
@app.route('/logout')
def logout():
    session.pop('email')
    session.pop('name')
    session['logged_in'] = False
    return redirect(url_for('home'))

#takes user to manage a single subscription
@app.route('/manage_subscription/<sub_name>')
def manage_subscription(sub_name):
    amounts = get_user_profile()

    if session.get('renewal_error'):
        renewal_error = session['renewal_error']
        session.pop('renewal_error')
        return render_template('homeManage.html', name=session['name'], entertainment_amount=amounts[0],
            education_amount=amounts[1], total_sub_amount=amounts[2], total_subs=amounts[3], sub_name=sub_name, renewal_error=renewal_error)
    else:
        return render_template('homeManage.html', name=session['name'], entertainment_amount=amounts[0],
            education_amount=amounts[1], total_sub_amount=amounts[2], total_subs=amounts[3], sub_name=sub_name)

#response from confirm/renew button in manage page
@app.route('/confirm_renewal', methods=['POST', 'GET'])
def renew_subscription():

    if request.method == "POST":
        sub_name = request.form['sub_name']
        sub_price = request.form['sub_price']
        sub_renewal_date = request.form['sub_renewal_date']
        notification_type = request.form['notification_type']
        subscription_type = request.form['sub_type']
        active_sub = 1

        if (sub_name == "" or sub_price == "" or sub_renewal_date == "" or notification_type == "" or subscription_type == ""):
            session['renewal_error'] = "Please fill out all of the fields before submitting."
            return redirect(url_for('manage_subscription', sub_name=sub_name))

        conn = mysql.connector.connect(**mysql_config)
        cur = conn.cursor()
        cur.execute(f"DELETE FROM subscription WHERE email='{session['email']}' AND sub_name='{sub_name}';")
        conn.commit()
        cur.execute(f"INSERT INTO subscription VALUES ('{session['email']}', '{sub_name}', {sub_price}, {sub_renewal_date}, '{notification_type}', '{subscription_type}', 1);")
        conn.commit()
    #Code to be added in the future

    return render_template('homeConfirm.html', name=session['name'])

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

@app.route('/settings')
def user_settings():
    return render_template('userSettings.html', name=session['name'])

@app.route('/cancelplan/<sub_name>')
def cancel_subscription(sub_name):
    amounts = get_user_profile()
    return render_template('cancelPlan.html', name=session['name'], entertainment_amount=amounts[0],
        education_amount=amounts[1], total_sub_amount=amounts[2], total_subs=amounts[3], sub_name=sub_name)

@app.route('/password_change', methods=['POST'])
def change_password():
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if (new_password == "" or confirm_password == ""):
        password_error_message = "Please fill out both inputs."
        return render_template('userSettings.html', password_error_message=password_error_message)

    if (new_password != confirm_password):
        password_error_message = "Passwords do not match."
        return render_template('userSettings.html', password_error_message=password_error_message)

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET password='{new_password}' WHERE email='{session['email']}';")
    conn.commit()
    return redirect(url_for('user_data'))
    return

@app.route('/email_change', methods=['POST'])
def change_email():
    new_email = request.form['new_email']
    confirm_email = request.form['confirm_email']

    if (new_email == "" or confirm_email == ""):
        email_error_message = "Please fill out both inputs."
        return render_template('userSettings.html', email_error_message=email_error_message)

    if (new_email != confirm_email):
        email_error_message = "Emails do not match."
        return render_template('userSettings.html', email_error_message=email_error_message)

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM users WHERE email='{new_email}';")
    if cur.fetchone():
        email_error_message="An account with the previously entered email already exists. Please use a different email."
        return render_template('userSettings.html', email_error_message=email_error_message)

    cur.execute(f"UPDATE users SET email='{new_email}' WHERE email='{session['email']}';")
    session['email'] = new_email

    conn.commit()
    return redirect(url_for('user_data'))

@app.route('/confirm_cancel/<sub_name>')
def confirm_cancel(sub_name):
    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    cur.execute(f"UPDATE subscription SET active_sub=0 WHERE email='{session['email']}' AND sub_name='{sub_name}'")
    conn.commit()

    return redirect(url_for('user_data'))

@app.route('/delete/<sub_name>')
def delete_subscription(sub_name):
    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM subscription WHERE email='{session['email']}' AND sub_name='{sub_name}'")
    conn.commit()
    return redirect(url_for('user_data'))

#gets total number of subs and amounts for each sub type
def get_user_profile():
    entertainment_amount = Decimal(0.00)
    education_amount = Decimal(0.00)
    total_sub_amount = Decimal(0.00)
    total_subs = 0
    active_subs = []
    entertainment_subs = []
    education_subs = []
    #these are the only two things we have as of now

    conn = mysql.connector.connect(**mysql_config)
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM subscription WHERE email='{session['email']}';")
    sub_data = cur.fetchall()

    for row in sub_data:
        if (row[6] == 1):
            active_subs.append(row)

            if (row[5] == "Entertainment"):
                entertainment_amount += Decimal(row[2])
                entertainment_subs.append(row)
            elif (row[5] == "Education"):
                education_amount += Decimal(row[2])
                education_subs.append(row)
            total_sub_amount += Decimal(row[2])
            total_subs += 1
        else:
            if (row[5] == "Entertainment"):
                entertainment_subs.append(row)
            elif (row[5] == "Education"):
                education_subs.append(row)

    return (entertainment_amount, education_amount, total_sub_amount, total_subs, active_subs, entertainment_subs, education_subs)

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
