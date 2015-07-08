#Generic Item/Catalog Application
This provides a simple, plug and play, webapp to store and display items, sorted by the categories they belong to. The most recently added items are displayed on the landing page. The application integrates Open Authentication through facebook. New users are automatically added to the application user list, if authenticated by the OAuth provider. Only authenticated users are allowed to update content (Add/Edit/Delete).

###Requires
This webapp is built using python, the flask framework, Jinja and a few other technologies. Please make sure that the python libraries for the following are installed on your operating system

*jinja[http://jinja.pocoo.org]

*oauth[https://pypi.python.org/pypi/oauthlib]

*bleach[https://pypi.python.org/pypi/bleach]

*flask[http://flask.pocoo.org]

*sqlalchemy[http://www.sqlalchemy.org]

*httplib2[https://pypi.python.org/pypi/httplib2]

*requests[http://docs.python-requests.org/en/latest/]


```
Example for a linux system:
  
  apt-get -qqy install python-sqlalchemy
  apt-get -qqy install python-pip
  pip install werkzeug==0.8.3
  pip install flask==0.9
  pip install Flask-Login==0.1.3
  pip install oauth2client
  pip install requests
  pip install httplib2
  pip install bleach
```

###Installation
1. Download the application : git clone https://github.com/yamrock/itemcatalog.git
2. execute: python database_setup.py (sets up the catalog.db)
3. Optional: python database_populate (adds some arbitary sample data)

*CAUTION: The facebook app client secret is being published in this repository, since this is for Udacity eval. In reality, you will need to register the app using your facebook credentials and update the fbclientsecrets.json file with your info and save it securely on your server*

###API Extension
The app provides a /catalog.json URI to present the entire catalog of items and associated categories as a JSON file, for any RESTful integration.

```
Example JSON output
   {
     "categories": [
       {
         "desc": "Bats are used for hitti
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

```

###To Do

Create URLs for updating categories. The python code is in place. Only the HTML rendering remains. Leaving this out for now to accomodate for project delviery deadlines :) (Not in the requirements spec)

