import os
# to manipulate run-time environment
import sys
# all are classes
from sqlalchemy import Column, ForeignKey, Integer, String
# to write config and class code
from sqlalchemy.ext.declarative import declarative_base
# to write mapper
from sqlalchemy.orm import relationship
# to write config file
from sqlalchemy import create_engine

Base = declarative_base()

class Restaurant(Base):
	# Corresponds to restaurant table
	__tablename__ = 'restaurant'
	# name attribute is a string with max of 80 chars
	# and it cannot be null
	name = Column(String(80), nullable = False)
	# id attribute is an int and a PK of its table
	id = Column(Integer, primary_key = True)

class MenuItem(Base):
	# Corresponds to menu_item table
	__tablename__ = 'menu_item'
	id = Column(Integer, primary_key = True)
	course = Column(String(250))
	price = Column(String(8))
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
	# represents relationship between MenuItem and Restaurant
	restaurant = relationship(Restaurant)


# points to the db we'll use and create file we can use as db
engine = create_engine('sqlite:///restaurantmenu.db')
# adds the classes we'll create as tables in our db
Base.metadata.create_all(engine)