from flask import Flask, render_template
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# list of restaurants
@app.route('/')
@app.route('/restaurants/')
def show_restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants = restaurants)

# adding new restaurant
@app.route('/restaurant/new/')
def new_restaurant():
    return render_template('newRestaurant.html')

# editing existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/')
def edit_restaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('editRestaurant.html', restaurant = restaurant)

# deleting restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/')
def delete_restaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('deleteRestaurant.html', restaurant = restaurant)

# showing menu of a restaurant
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def show_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return render_template('menu.html', restaurant = restaurant, items = menu_items)

# adding new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def new_menu_item(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('newMenuItem.html', restaurant = restaurant)

# editing existing menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def edit_menu_item(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id = menu_id).one()
    return render_template('editMenuItem.html', restaurant = restaurant, item = menu_item)

# deleting menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def delete_menu_item(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id = menu_id).one()
    return render_template('deleteMenuItem.html', restaurant = restaurant, item = menu_item)


# will only run from python interpretor
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 9998)
