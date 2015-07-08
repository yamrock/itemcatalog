from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random, string
#Sanitize data to protect agains SQL injection/Cross Site Scripting etc.
import bleach
#IMPORTS to handle OAuth
import httplib2
import json
from flask import make_response
import requests

def create_session():
    #Call the create_engine to connect o the database
    DB_engine = create_engine('sqlite:///catalog.db')
    Base.metadata.bind = DB_engine
    #The sessionmaker call, creates a factory which is named DB_Session
    #This factory, when called, will create new DB_Session objects with the arguments give (Connect to DB_Engine) 
    DBSession = sessionmaker(bind = DB_engine)
    return DBSession()


app = Flask(__name__)
app.secret_key = 'something_strong'

@app.route('/catalog.json')
def catalogJSON():
    '''
    Returns JSON data for the entire catalog
    '''
    #Here, we use a 2D array. We iterate through each category, serialize it and hold it in the catalog[]. Then, within each 
    #category, we iterate through the items within that category and collect the serialized version of each items inside items_per_category[]
    #We then append this list to the catalog[]
    ''' SAMPLE
    {
      "categories": [
        {
          "desc": "Bats are used for hitting balls",
          "name": "Bats",
          "id": 2
        },
        [
          {
            "cat_id": 2,
            "desc": "light and netty",
            "id": 4,
            "name": "badminton bat"
          }
        ],
        [
          {   
            "cat_id": 2,
            "desc": "kdlkjldkf",
            "id": 5,
            "name": "klakj"
          }
        ],
      ]
     }

    '''
    session = create_session()
    #First, collect all category objects to iterate
    categories = session.query(Category).all()
    #Initialize the 2D array
    catalog = []
    for category in categories:
        #intitialize the items per category for each category
        items_per_category = []
        catalog.append(category.serialize)
        for item in category.items:
            items_per_category.append(item.serialize)
        catalog.append(items_per_category)
    return jsonify(categories = catalog)

@app.route('/')
@app.route('/catalog/')
def showCatalog():
    '''
    Landing page for the app. It lists the categories and the most recently added
    items and renders this through templates/catalog.html
    '''
    session = create_session()
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.creation_time.desc())
    session.close()
    if 'username' not in login_session:
        return render_template("publiccatalog.html", categories = categories, items = items)
    else:
        return render_template("catalog.html", categories = categories, items = items)

@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    '''Allows authenticated users to add new categories. 
    Category Add/Delete/Edit is not required per P3 submission eval matrix
    '''
    if request.method == 'POST':
        session = create_session()
        newCategory = Category(name = str(bleach.clean( request.form['category'])), description = str(bleach.clean(request.form['description'])))
        session.add(newCategory)
        session.commit()
        session.close()
        return redirect(url_for('showCatalog'))
    else:
        #It is a GET request
        if 'username' not in login_session:
            return("<h1> You have to be logged in to add a new catalog item</h1")
        else:
            return render_template('newcategory.html')

@app.route('/catalog/<int:category_id>/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
    '''Allows authenticated users to edit exiting category names and description. 
    Category Add/Delete/Edit is not required per P3 submission eval matrix
    '''
    session = create_session()
    editedCategory = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['category']:
            editedCategory.name = str(bleach.clean(request.form['category']))
        if request.form['description']:
            editedCategory.description = str(bleach.clean(request.form['description']))
        session.commit()
        session.close()
        return redirect(url_for('showCatalog'))
    else:
        #GET request, display the edit form
        session.close()
        if 'username' not in login_session:
            return("<h1> You have to be logged in to edit a catalog item</h1")
        else:
            return render_template('editCategory.html', category_id = category_id, current_category = editedCategory)

@app.route('/catalog/<int:category_id>/delete/', methods = ['GET', 'POST'])
def deleteCategory(category_id):
    '''Allows authenticated users to delete exiting categories in the catalog. 
    Category Add/Delete/Edit is not required per P3 submission eval matrix
    '''
    session = create_session()

    session = create_session()
    categoryToDelete = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        categoryToDelete = session.query(Category).filter_by(id = category_id).one()
        session.delete(categoryToDelete)
        session.commit()
        session.close()
        flash("You have deleted the category")
        return redirect(url_for('showCatalog'))
    else:
        #GET, display the form to delete the selected category
        session.close()
        if 'username' not in login_session:
            return("<h1> You have to be logged in to delete a catalog item</h1")
        return render_template('deleteCategory.html', category_id = category_id, current_category = categoryToDelete)

@app.route('/catalog/<path:category_name>/')
@app.route('/catalog/<path:category_name>/items/')
def showItems(category_name):
    '''Allows users to view exiting categories and their items in the catalog. 
    Use the URI instead of an integer to locate category items
    '''
    session = create_session()
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id).all()
    numberOfItems = session.query(Item).filter_by(category_id = category.id).count()
    session.close()
    if 'username' not in login_session:
        return render_template('publicitems.html', items = items, numItems = numberOfItems, category = category, categories = categories)
    else:
        return render_template('items.html', items = items, numItems = numberOfItems, category = category, categories = categories)
                
@app.route('/catalog/<path:category_name>/<path:item_name>/')
def showItemDetail(category_name, item_name):
    '''Allows users to view the details of a catalog item on selecting it. 
    Use the URI instead of an integer to locate category items
    '''
    session = create_session()
    category = session.query(Category).filter_by(name = category_name).one()
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(category_id = category.id, name = item_name  ).one()
    session.close()
    if 'username' not in login_session:
        return render_template('publicitemDetails.html', item = item, category = category, categories = categories)
    else:
        return render_template('itemDetails.html', item = item, category = category, categories = categories)

@app.route('/catalog/<path:category_name>/new', methods = ['GET', 'POST'])
def newItem(category_name):
    '''Allows users to add a new item to the catalog from within the category. 
    Use the URI instead of an integer to locate category items
    '''
    if request.method == 'POST':
        session = create_session()
        category = session.query(Category).filter_by(name = category_name).one()
        newItem = Item(name = str(bleach.clean(request.form['itemName'])), description = str(bleach.clean(request.form['description'])), category_id = category.id)
        session.add(newItem)
        session.commit()
        session.close()
        flash("You have successfully created the new item")
        return redirect(url_for('showCatalog'))
    else:
        #GET method, display the item add form
        if 'username' not in login_session:
            return("<h1>You need to login in order to add new items</h1>")
        else:
            return render_template('newItem.html', category_name = category_name)

@app.route('/catalog/newitem/', methods = ['GET', 'POST'])
def newItemCategory():
    '''Allows users to add a new item to the catalog without having to first select the category. 
    It allows the users to select the category through a drop down list
    Use the URI instead of an integer to locate category items
    '''
    session = create_session()
    categories = session.query(Category).all()
    if request.method == 'POST':
        category_name = request.form['categoryName']
        category = session.query(Category).filter_by(name = category_name).one()
        newItem = Item(name = str(bleach.clean(request.form['itemName'])), description = str(bleach.clean(request.form['description'])), category_id = category.id)
        session.add(newItem)
        session.commit()
        session.close()
        flash("You have successfully created the new item")
        return redirect(url_for('showCatalog'))
    else:
        #GET method, display the new item/category form
        session.close()
        if 'username' not in login_session:
            return("<h1>You need to login in order to add new items</h1>")
        else:
            return render_template('newItemCategory.html', categories = categories)

@app.route('/catalog/<path:category_name>/<path:item_name>/edit/', methods = ['GET', 'POST'])
def editItem(category_name, item_name):
    '''Allows authenticated users to edit exiting item names and description. 
    '''
    session = create_session()
    category = session.query(Category).filter_by(name = category_name).one()
    categories = session.query(Category).all()
    editedItem = session.query(Item).filter_by(name = item_name, category_id = category.id).one()
    if request.method == 'POST':
        category_name = str(bleach.clean(request.form['categoryName']))
        category = session.query(Category).filter_by(name = category_name).one()
        if request.form['itemName']:
            editedItem.name = str(bleach.clean(request.form['itemName']))
        if request.form['description']:
            editedItem.description = str(bleach.clean(request.form['description']))
        editedItem.category_id = category.id
        session.commit()
        session.close()
        flash("You have successfully updated the item")
        return redirect(url_for('showCatalog'))
    else:
        #GET request, display the edit form
        session.close()
        if 'username' not in login_session:
            return("<h1>You are not logged in. Please login to edit an item</h1>")
        else:
            return render_template('editItem.html', category_name = category_name, item_name = item_name, item = editedItem,  categories = categories)


@app.route('/catalog/<path:category_name>/<path:item_name>/delete/', methods = ['GET', 'POST'])
def deleteItem(category_name, item_name):
    if request.method == 'POST':
        session = create_session()
        category = session.query(Category).filter_by(name = category_name).one()
        itemToDelete = session.query(Item).filter_by(name = item_name, category_id = category.id).one()
        session.delete(itemToDelete)
        session.commit()
        session.close()
        flash("You have successfully deleted the item")
        return redirect(url_for('showCatalog'))
    else:
        if 'username' not in login_session:
            return("<h1>You are not logged in. Please login to delete an item</h1>")
        else:
            return render_template('deleteItem.html', category_name = category_name, item_name = item_name)
 
#OAuth Login Intergration
@app.route('/login')
@app.route('/catalog/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# HELPER FUNCTIONS
# These functions help interact with the DB to help validate/create users
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


@app.route('/fbconnect', methods = ['POST'])
def fbconnect():
    if(request.args.get('state') != login_session['state']):
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Else validate one-time code between FB/Client against FB
    # if not successful, throw an error
    # Else set the result to something and return it back to login.html, which will then call '/restaurant'
    access_token = request.data 
    
    #access_token is what was generated through the browser for the client. 
    #Use this token to exchange it for a server side token for that user (this token has a longer expiry)

    app_id = json.loads(open('fbclientsecrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fbclientsecrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    #Extract the token from the result
    token = result.split("&")[0]

    userinfo_url = 'https://graph.facebook.com/v2.2/me?%s' % token
    h = httplib2.Http()
    result = h.request(userinfo_url, 'GET')[1]
    #Store the JSON result as a dict
    data = json.loads(result)
    login_session['provider'] = "facebook"
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    #Get the FB profile pic
    url = 'https://graph.facebook.com/v2.2/me/picture%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    if data.get('error') is not None:
        login_session['picture'] = "https://placeimg.com/200/200"
    else:
        login_session['picture'] = data["data"]["url"]

    ## Create the user if she does not exist
    if getUserID(login_session['email']) is not None:
        #User exists, so set the login_session['user_id']
        login_session['user_id'] = getUserID(login_session['email'])
    else:
        #Create the new User and set the userID
        login_session['user_id'] = createUser(login_session)

    
    ## Return HTTP response to the POST request, with user info, if successful
    output = ' '
    output += '<h1> Welcome'
    output += login_session['username']
    output += '</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['provider']
    del login_session['username']
    del login_session['picture']
    del login_session['email']
    del login_session['user_id']
    del login_session['facebook_id']
    return "You have been logged out"

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == "google":
            gdisconnect()
        if login_session['provider'] == "facebook":
            fbdisconnect()
        #flash("You have successfully been logged out")
        return redirect(url_for('showCatalog'))
    else:
        #You are not currently logged in
        response = make_response(json.dumps("No user logged in"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response


if (__name__ == '__main__'):
    app.debug = False
    app.run(host = '0.0.0.0', port = 5000)

