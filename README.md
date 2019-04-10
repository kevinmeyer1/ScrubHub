# How to hopefully get this to work

Follow the following steps to install and run this application on your own computer

Download the zip file (or clone it if you are git smart) found on this GitHub page and extract the files onto your computer.

Now that you have all of the necessary files, install the following things that are needed to run the application through your computers terminal:

    python3 (older versions will not work as python3 exclusive code is used)
    pip (a python installer that will make installing the next services easier)
    mysql (pip install mysql)
    mysql-connector-python (pip install mysql-connector-python)
    flask (pip install flask)
    twilio (pip install twilio)
    MySQL Workbench

Once all of these are successfully installed, you will need to create a database.

Open MySQL Workbench. Open a local instance of MySQL in the application. Copy and execute the text inside of the `CreateDatabase.txt` file found in the ScrubHub folder to create the ScrubHub database and tables.

You will need to go into the `config.json` file and update the values labeled `user` and `password`. These values will reflect the username and password that you use to sign into your localhost instance of mysql on your computer.

Once your database, user, and password are all set up, you should be able to `cd` into the ScrubHub folder that you downloaded within your terminal.

Now you need to set up an environment varaible called `FLASK_APP`. In a linux terminal this can be done by entering `export FLASK_APP=main.py`. I'm not sure how to do it on a Mac. I think `set` is used instead of `export`. What ever method you use, `FLASK_APP=main.py` is needed.

Once your environment varaible is set, run the command 'flask run' in your terminal. Some text should pop up along the lines of:

    Serving Flask app "main.py"
    ~~~~~Some other stuff~~~~~
    Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

Go to your web browser and go to the address `localhost:5000`

You should see the ScrubHub website. Now you can create an account and test everything out.

# Warning

The application still has plenty of opportunities for it to crash. Multiple accounts created with the same email may cause some issues. The email and phone number provided during account creation will be used to send texts or emails so make sure you use working emails and phone numbers.
