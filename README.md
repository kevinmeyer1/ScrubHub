# How to hopefully get this to work

Download this from github

To get this to work you must have the following installed:

    python
    pip (a python installer, used to install the following)
    mysql (pip install mysql)
    mysql-connector-python (pip install mysql-connector-python)
    flask (pip install flask)

Dont forget to add the python path into your system variables. That was a pain for me and I had to google a bunch of stuff cause it didn't work for a while. You can check if python and pip are accessible by typing 'python' or 'pip' into your console and it should give you a bunch of help options and stuff

Once those are downloaded you need to create a user in your mysql workbench. Make sure there is a Local Instance of mysql running on your computer. If not click the plus button in MySQL workbench and name it something and hit ok. It defaults to localhost (127.0.0.1)

You can name the user anything you want but if you dont make it U:Kevin P:kevin11 you need to change those in the mysql_config variable in main.py so that it will successfully log in

Then create the database (subhub - can be changed but mysql_config needs to reflect it) and load in a users table.

These commands are in the populatedatabase.txt file in this folder

Once all those are done, you need to add an environment varaible called FLASK_APP and set it to 'main.py'. In windows you do that by typing 'export FLASK_APP=main.py' into the console. Not sure what it is for MacOS.

Change directory into the folder you downloaded (cd C:/Documents/SubHub - where ever you put the file)

Type 'flask run' into your console

Some stuff should pop up then it should just sit there and do nothing

Go to your web browser and go to 'localhost:5000' or what ever port the flask ouput tells you it's listening on.

Sign in with what ever user you created (default is Kevin kevin11 as per the database.txt thing)

it should pop up with one entry being chegg and some other information

## Comments

Thats the basic bare bones functionality of the website. Theres no CSS and the html is extremely ugly. You can sign up and itll create a new user and a new table for that user however there wont be any data in it unless you add it through mysql workbench. Theres a tiny bit of error handling but not a log so I'm sure you can probably break it. If it does break, CTRL+c the console and just run 'flask run' again then itll start.
