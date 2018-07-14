from flask import Flask
from database_setup import Restaurant, MenuItem

app = Flask(__name__)

# list of restaurants
@app.route('/')
@app.route('/restaurants/')
def show_restaurants():
    return 'This page will show all my restaurants'

# adding new restaurant
@app.route('/restaurant/new/')
def new_restaurant():
    return 'This page will be for making a new restaurant'

# editing existing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/')
def edit_restaurant(restaurant_id):
    return 'This page will be for editing restaurant %s' % restaurant_id

# deleting restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/')
def delete_restaurant(restaurant_id):
    return 'This page will be for deleting restaurant %s' % restaurant_id

# showing menu of a restaurant
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def show_menu(restaurant_id):
    return 'This page is the menu for restaurant %s' % restaurant_id

# adding new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def new_menu_item(restaurant_id):
    return 'This page is for making a new menu item for restaurant %s' % restaurant_id

# editing existing menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def edit_menu_item(restaurant_id, menu_id):
    return 'This page is for editing menu item %s' % menu_id

# deleting menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def delete_menu_item(restaurant_id, menu_id):
    return 'This page is for deleting menu item %s' % menu_id


# will only run from python interpretor
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 9998)
