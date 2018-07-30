from flask import Flask, render_template, url_for, redirect, request
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db?check_same_thread=False')
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
@app.route('/restaurant/new/', methods = ['GET', 'POST'])
def new_restaurant():
    if request.method == 'POST':
        new_entry = Restaurant(name=request.form.get('name'))
        session.add(new_entry)
        session.commit()
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
        return redirect(url_for('show_restaurants'))
    if request.method == 'GET':
        return render_template('deleteRestaurant.html', restaurant = restaurant)

# will only run from python interpretor
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 9998)
