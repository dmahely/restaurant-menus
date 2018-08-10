from flask import Flask, render_template, url_for, redirect, request, jsonify, flash
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# imports for OAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, session as login_session
import requests
import random, string

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Restaurant Menu Web Application'


# login page
@app.route('/login/')
def show_login():
    # generates random anti-forgery state token and
    # saves it in Flask's session object
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# page accepting post requests
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # obtain authorization code
    code = request.data

    try:
        # upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there's an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            'Token\'s user ID does not match given user ID'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            'Token\s client ID des not match the app\'s'), 401)
        print 'Token\s client ID des not match the app\'s'
        response.headers['Content-Type'] = 'application/json'
        return response

    # check if user is already logged in
    # stored_credentials = login_session.get('credentials')
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'User is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store access token in the session for later use
    #login_session['credentials'] = credentials
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # gets user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token,
              'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    #data = json.loads(answer.text)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Revokes a current user's token and resets the login_session object (logs them out)
@app.route('/gdisconnect')
def gdisconnect():
	# Check if user is logged in
	#credentials = login_session.get('credentials')
	access_token = login_session.get('access_token')
	# If user is not logged in
	#if credentials is None:
	if access_token is None:
		response = make_response(json.dumps(
			'Current user not connected'), 401)
		response.headers['Content-type'] = 'application/json'
		return response

	print('In gdisconnect access token is %s', access_token)
	print('User name is:')
	print(login_session['username'])

	# Execute HTTP GET request to revoke current user
	#access_token = credentials.access_token
	# google page that revokes access tokens
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print('result is' + str(result))

	if result['status'] == '200':
		# Reset user's session
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['picture']
		del login_session['email']

		response = make_response(json.dumps(
			'Successully disconnected'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	else:
		# Invalid token
		response = make_response(json.dumps(
			'Failed to revoke token for given user', 400))
		response.headers['Content-Type'] = 'application/json'
		return response

# API endpoint for a restaurant's menu
@app.route('/restaurants/<int:restaurant_id>/json/')
@app.route('/restaurants/<int:restaurant_id>/menu/json/')
def restaurant_menu_json(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

# API endpoint for a menu item
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/json/')
def menu_item_json(restaurant_id, menu_item_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id,
                                                  id = menu_item_id).one()
    return jsonify(MenuItem = menu_item.serialize)


# list of restaurants
@app.route('/')
@app.route('/restaurants/')
def show_restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)

# adding new restaurant
@app.route('/restaurant/new/', methods = ['GET', 'POST'])
def new_restaurant():
    if request.method == 'POST':
        new_entry = Restaurant(name=request.form.get('name'))
        session.add(new_entry)
        session.commit()
        flash('New restaurant sucessfully added!')
        return redirect(url_for('show_restaurants'))
    if request.method == 'GET':
        return render_template('newRestaurant.html')

# editing existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def edit_restaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        restaurant.name = request.form.get('name')
        session.add(restaurant)
        session.commit()
        flash('Restaurant\'s information sucessfully edited!')
        return redirect(url_for('show_restaurants'))
    if request.method == 'GET':
        return render_template('editRestaurant.html', restaurant = restaurant)

# deleting existing restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET', 'POST'])
def delete_restaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash('Restaurant successfully deleted!')
        return redirect(url_for('show_restaurants'))
    if request.method == 'GET':
        return render_template('deleteRestaurant.html', restaurant = restaurant)

# showing menu of a restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/')
@app.route('/restaurant/<int:restaurant_id>/')
def show_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id).all()
    return render_template('menu.html', restaurant = restaurant, items = items)

# adding a menu item to an existing restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def new_menu_item(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        menu_item = MenuItem(name = request.form.get('name'),
                             price = request.form.get('price'),
                             description = request.form.get('description'))
        session.add(menu_item)
        session.commit()
        flash('New menu item successfully added!')
        return redirect(url_for('show_menu', restaurant_id = restaurant_id))
    if request.method == 'GET':
        return render_template('newMenuItem.html', restaurant = restaurant)


# editing a menu item of an existing restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_item_id>/edit/',
           methods = ['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_item_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_item_id).one()
    if request.method == 'POST':
        menu_item.name = request.form.get('name')
        menu_item.price = request.form.get('price')
        menu_item.description = request.form.get('description')
        session.add(menu_item)
        session.commit()
        flash('Menu item\'s information successfully edited!')
        return redirect(url_for('show_menu', restaurant_id = restaurant_id))
    if request.method == 'GET':
        return render_template('editMenuItem.html', restaurant = restaurant, menu_item = menu_item)

# deleting a menu item from an existing restaurant
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_item_id>/delete/',
           methods = ['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_item_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(restaurant_id = restaurant_id, id = menu_item_id).one()
    if request.method == 'POST':
        session.delete(menu_item)
        session.commit()
        flash('Menu item successfully deleted!')
        return redirect(url_for('show_menu', restaurant_id = restaurant_id))
    if request.method == 'GET':
        return render_template('deleteMenuItem.html', restaurant = restaurant, menu_item = menu_item)

# will only run from python interpretor
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 9998)
