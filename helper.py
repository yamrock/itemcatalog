
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User
from flask import flash, redirect, url_for, session as login_session
#Imports for 'login required', decorator
from functools import wraps


# HELPER FUNCTIONS
# These functions help interact with the DB to help validate/create users

def create_session():
    #Call the create_engine to connect o the database
    DB_engine = create_engine('sqlite:///catalog.db')
    Base.metadata.bind = DB_engine
    #The sessionmaker call, creates a factory which is named DB_Session
    #This factory, when called, will create new DB_Session objects with the arguments give (Connect to DB_Engine) 
    DBSession = sessionmaker(bind = DB_engine)
    return DBSession()

def createUser(login_session):
    session = create_session()
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    session.close()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    session = create_session()
    user = session.query(User).filter_by(id = user_id).one()
    session.close()
    return user

def getUserID(email):
    session = create_session()
    try:
        user = session.query(User).filter_by(email = email).one()
        session.close()
        return user.id
    except:
        session.close()
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            flash("You need to be logged in to make that change")
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


