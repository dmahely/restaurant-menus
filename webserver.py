from flask import Flask, render_template, url_for, redirect, request, jsonify, flash
from database_setup import Base, Restaurant, MenuItem, User
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

# from google.oauth2 import id_token
# from google.auth.transport import requests

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

engine = create_engine('sqlite:///restaurantmenuwithusers.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

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
    if 'username' not in login_session:
        return render_template('publicrestaurants.html',
            restaurants = restaurants)
    return render_template('restaurants.html', restaurants = restaurants)

# adding new restaurant
@app.route('/restaurants/new/', methods = ['GET', 'POST'])
def new_restaurant():
    if request.method == 'POST':
        new_entry = Restaurant(name=request.form.get('name'),
            user_id = login_session['user_id'])
        session.add(new_entry)
        session.commit()
        flash('New restaurant sucessfully added!')
        return redirect(url_for('show_restaurants'))
    if request.method == 'GET':
        return render_template('newRestaurant.html')

# editing existing restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
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
@app.route('/restaurants/<int:restaurant_id>/delete/', methods = ['GET', 'POST'])
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
@app.route('/restaurants/<int:restaurant_id>/menu/')
@app.route('/restaurants/<int:restaurant_id>/')
def show_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    creator = get_user_info(restaurant.user_id)
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicmenu.html', items = items,
            restaurant = restaurant, creator = creator)
    return render_template('menu.html', restaurant = restaurant, items = items)

# adding a menu item to an existing restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def new_menu_item(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        menu_item = MenuItem(name = request.form.get('name'),
                             price = request.form.get('price'),
                             description = request.form.get('description'),
                             user_id = login_session['user_id'])
        session.add(menu_item)
        session.commit()
        flash('New menu item successfully added!')
        return redirect(url_for('show_menu', restaurant_id = restaurant_id))
    if request.method == 'GET':
        return render_template('newMenuItem.html', restaurant = restaurant)


# editing a menu item of an existing restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/edit/',
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
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/delete/',
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
