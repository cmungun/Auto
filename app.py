import csv
import json
from random import randint
from urllib import response

from flask import Flask, g, render_template, Response, redirect, request, jsonify, session, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, login_manager
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, RadioField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length, Regexp, ValidationError

import sys
import sqlite3
import os
import logging

DATABASE = "./data/database.db"
console = logging.getLogger('console')
console.setLevel(logging.DEBUG)
# Create app
app = Flask(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'processLogin'
app.config['USE_SESSION_FOR_NEXT'] = True

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


# @app.route("/static/<string:cssFile>")
# def cssFile(cssFile):
#     cssAddress = os.path.join(os.getcwd(), 'templates', 'css', cssFile)
#     handler = open(cssAddress, 'r')
#     data = handler.read()
#     handler.close()
#     return Response(data, mimetype='text/css')
#
#


class contactRecommendationForm(FlaskForm):
    subject = StringField('Subject', validators=[])
    name = StringField('Name', validators=[InputRequired(), Length(4, 64),  Regexp('^[A-Za-z][A-Za-z0-9_. ]*$', 0, 'Unless you a king, your name cant contain letters, numbers, dots or underscores')])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    message = TextAreaField('Message', validators=[InputRequired()])


class videoConferenceForm(FlaskForm):

    name = StringField('Name', validators=[InputRequired()])
    year = SelectField('Year',  default="0",choices=[ ('0', '0'), ('1', '1'), ('2', '2'),('3', '3'), ('4', '4'),('5', '5')])
    characteristic =RadioField('Characteristic for Call', choices=[('normal', 'Normal Talk'), ('hwk', 'Home Work'),('TalkAboutLife', 'Talk about life'), ('otherReasons', 'other Reasons')])
    picture = TextAreaField('Other details you want to specify', validators=[])

class User(UserMixin):
    def __init__(self, username, email= "", phone="", password=""):
        self.id = username
        self.email = email
        self.phone = phone
        self.password = password


# this is used by flask_login to get a user object for the current user
# @login_manager.user_loader
# def load_user(user_id):
#     user = find_user(user_id)
#     # user could be None
#     if user:
#         # if not None, hide the password by setting it to None
#         user.password = None
#     return user


def find_user(username):
    with open('data/users.json') as f:
        for user in json.reader(f):
            if username == user[0]:
                return User(*user)
    return None


# check if the database exist, if not create the table and insert a few lines of data
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    app.logger.info('Processing default request')
    print("Opened database successfully")
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (fname TEXT, lname TEXT, age INTEGER, pword TEXT);")
    conn.commit()
    cur.execute("CREATE table Recommendation(id INTEGER  primary key autoincrement,     email   VARCHAR(30),    name    VARCHAR(20),    subject VARCHAR(1000),     message VARCHAR(1000));")
    conn.commit()
    cur.execute("INSERT INTO users VALUES('Mike', 'Tyson', '40', '1234ABCD');")
    cur.execute("INSERT INTO users VALUES('Thomas', 'Jasper', '40', '1234ABCD');")
    cur.execute("INSERT INTO users VALUES('Jerry', 'Mouse', '40', '1234ABCD');")
    cur.execute("INSERT INTO users VALUES('Peter123', 'Pan', '40', '1234ABCD');")
    cur.execute("INSERT INTO users VALUES('Peter123', 'Pan', '40', '1234ABCD');")

    conn.commit()
    conn.close()


# helper method to get the database since calls are per thread,
# and everything function is a new thread when called
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        app.logger.info('Processing default request')
        db = g._database = sqlite3.connect(DATABASE)
        print(db)
    return db


# helper to close
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    app.logger.info('Processing default request')
    if db is not None:
        db.close()




def save_changes(form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object

    name = form.name
    email = form.email
    subject = form.subject
    message = form.message
    year = form.message
    characteristic = form.message
    picture = form.message
    cur = get_db().cursor()

    cur.execute("INSERT INTO Recommendation (name,email,message,subject) VALUES (?,?,?,?)",
                (name, email, message, subject))
    # cur.commit()


@app.route("/")
def index(messages= ""):
    cur = get_db().cursor()
    print(messages)

    res = cur.execute("select * from users")

    return render_template("index.html", users=res, messages =messages)


@app.route("/timeline")
def timeline():
    return render_template("Timeline.html")

@app.route("/videoConferencing")
@login_required
def videoConferencing():
    url =" https://appr.tc/r/"+str(randint(100, 10000))
    return render_template("videoConferencing.html", video_link=url)


@app.route("/contactRecommendation", methods=['GET','POST'])
def contactRecommendation():
    form = contactRecommendationForm()
    print(form.errors)
    if request.method == 'POST' :
        if form.validate_on_submit():


            name = form.name.data
            email = form.email.data
            subject = form.subject.data
            message = form.message.data

            print(name)
            print(email)
            cur = get_db().cursor()

            cur.execute("INSERT INTO Recommendation (name,email,message,subject) VALUES (?,?,?,?)",
                        (name, email, message, subject))
            get_db().commit()
            # cur.

            # save_changes( form, new=True)
            messages = [['success', 'Your comments will be taken into consideration!']]
            # flash('comments saved.')
            return redirect(url_for('index', messages=messages))
        else:
            print(form.errors)
            print( type(form.errors))
            messages = [['danger', form.errors]]
            print(messages[0][0])
            # messages = [['danger', form.errors]] for this to work, uncomment button with class FormErrors in contact.html {It will show errors in messages in DOM}
            return render_template("contact.html", messages=messages, form=form)

    elif request.method == 'GET' :
        messages =""

    else:

        messages = [['danger', 'Sorry' + str(form.name.data) + 'but your comments were not able to be communicated Please try again later' ]]

    return render_template("contact.html", messages=messages, form=form)


@app.route("/videoRequest", methods=['GET', 'POST'])
@login_required
def videoRequest():
    form = videoConferenceForm()
    form.name.data = session['username']
    print(form.errors)
    if request.method == 'POST':
        if form.validate_on_submit():

            name = session['username']
            year = form.year.data
            characteristic = form.characteristic.data
            picture = form.picture.data

            # print(name)
            # print(email)
            # cur = get_db().cursor()
            #
            # cur.execute("INSERT INTO Recommendation (name,email,message,subject) VALUES (?,?,?,?)",
            #             (name, email, message, subject))
            # get_db().commit()
            # cur.

            # save_changes( form, new=True)
            messages = [['success', 'Success!']]
            return redirect(url_for('videoConferencing', messages=messages))
        else:
            print(form.errors)
            print(type(form.errors))
            messages = [['danger', form.errors]]
            print(messages[0][0])
            # messages = [['danger', form.errors]] for this to work, uncomment button with class FormErrors in contact.html {It will show errors in messages in DOM}
            return render_template("videoRequest.html", messages=messages, form=form)

    elif request.method == 'GET':
        messages = ""

    else:

        messages = [['danger', 'Sorry' + str(
            form.name.data) + 'but your comments were not able to be communicated Please try again later']]

    return render_template("videoRequest.html", messages=messages, form=form)






@app.route("/gallery")
def gallery():
    return render_template("Gallery.html")

@app.route('/getAllUsers',methods= ['GET'])
@login_required
def getAllUsers():
    cur = get_db().cursor()

    res = cur.execute("select fname AS \"First Name\",lname AS \"Last Name\",age from users")



    items= [dict(zip([key[0] for key in cur.description], row)) for row in res]
    # print("jsonify(items)")
    # print(items)

    return jsonify(items)
    # return dict(res)
  # firstName = request.form['firstName']
  # lastName = request.form['lastName']
  # output = firstName + lastName
  # if firstName and lastName:



@app.route('/getCalendar',methods= ['GET'])
def getCalendar():
    requestData = request.args.getlist('data')

    print("***********getting calendar*******************")
    data = json.loads(requestData[0])
    print(data['subject'])
    # for x in data:
    #     print("??????????????????")
    #     print(x.courseID)
    # print(request.args.getlist('data'))
    # print(request.form)
    # print(request.is_json)
    with open('data/googleCalendar.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([data['subject'], data['classStartDate'] , data['classStartTime'],data['classEndDate'] , data['classEndTime'] ])
    return jsonify(data)

    # return jsonify({'error' : 'Missing data!'})


# @app.route("/login", methods=['POST', 'GET'])
@app.route("/processLogin", methods=["POST", 'GET'])
def processLogin():
    messages =""
    form = LoginForm()
    print("form")
    print(form.password)
    if request.method == 'POST':
        # print(form.validate_on_submit())
        # print(form.validate_on_submit())
        if form.validate_on_submit():
            print("form2")
            print(form)
            # _username = request.form['txt_username']
            # _password = request.form['txt_password']
            # user = find_user(form.username.data)
            cur = get_db().cursor()

            res = cur.execute("select fname ,pword from users")
            rows = res.fetchall()
            for row in rows:
                dbUser = row[0]
                print(dbUser)
                dbPass = row[1]
                print(dbPass)
                if dbUser == form.username.data:
                    # completion = check_password(dbPass, password)
                    if dbPass == form.password.data:

                        login_user(User(form.username.data))
                        session['username'] = form.username.data

                        messages = [['success', 'Welcome!']]
                        next_page = session.get('next', '/')
                        # reset the next page to default '/'
                        session['next'] = '/'
                        return redirect(next_page)
                else:
                    messages = [['danger', 'User Doesnot exist!!']]
    return render_template('login.html', messages=messages, form=form)




@app.route("/logout")
def logout():
    session.clear()
    messages=[['success','Logout successful!']]
    return render_template('index.html',messages=messages)


@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html')

@app.route('/documents')
# @login_required
def documents():

    with open('data/projectReq.csv') as f:
        doc_list = list(csv.reader(f))[1:]
    return render_template('documents.html', doc_list=doc_list )



if __name__ == "__main__":
    """
	Use python sqlite3 to create a local database, insert some basic data and then
	display the data using the flask templating.
	
	http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
    """
    app.run(host='', port=8081)
