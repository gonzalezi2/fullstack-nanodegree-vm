from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]

@app.route('/')
@app.route('/restaurants')
def showRestaurants():
  restaurants = session.query(Restaurant).all()
  return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurants/JSON')
def showRestaurantsJSON():
  restaurants = session.query(Restaurant).all()
  return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
  if request.method == 'POST':
    newRestaurant = Restaurant(name = request.form['name'])
    session.add(newRestaurant)
    session.commit()
    flash("New Restaurant Created - %s" % newRestaurant.name)
    return redirect(url_for('showRestaurants'))
  else:
    return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
  if request.method == 'POST':
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    editedRestaurant.name = request.form['name']
    session.commit()
    flash("Restaurant Successfully Edited - %s" % editedRestaurant.name)
    return redirect(url_for('showRestaurants'))
  else:
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('editRestaurant.html', restaurant = editedRestaurant)

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
  if request.method == 'POST':
    deletedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    session.delete(deletedRestaurant)
    session.commit()
    flash("Restaurant Successfully Deleted - %s" % deletedRestaurant.name)
    return redirect(url_for('showRestaurants'))
  else:
    restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('deleteRestaurant.html', restaurant = restaurantToDelete)

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
  menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
  return jsonify(MenuItems=[i.serialize for i in menuItems])


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
  menuItems = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
  restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
  return render_template('menu.html', restaurant = restaurant, items = menuItems)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def showMenuItemJSON(restaurant_id, menu_id):
  menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
  return jsonify(MenuItem=[menuItem.serialize])

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
  if request.method == 'POST':
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    newMenuItem = MenuItem(
      name = request.form['name'],
      description = request.form['description'],
      price = request.form['price'],
      course = request.form['course'],
      restaurant_id = restaurant_id
    )
    session.add(newMenuItem)
    session.commit()
    flash("Memu Item Created - %s" % newMenuItem.name)
    return redirect(url_for('showMenu', restaurant_id = restaurant.id))
  else:
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    return render_template('newmenuitem.html', restaurant = restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
  if request.method == 'POST':
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    editedMenuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    editedMenuItem.name = request.form['name']
    editMenuItem.description = request.form['description']
    editMenuItem.price = request.form['price']
    editMenuItem.course = request.form['course']
    session.commit()
    flash("Memu Item Successfully Edited - %s" % editedMenuItem.name)
    return redirect(url_for('showMenu', restaurant_id = restaurant_id))
  else:
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItemToEdit = session.query(MenuItem).filter_by(id = menu_id).one()
    return render_template('editmenuitem.html', restaurant = restaurant, item = menuItemToEdit)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
  if request.method == 'POST':
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    session.delete(menuItem)
    session.commit()
    flash("Memu Item Successfully Deleted - %s" % menuItem.name)
    return redirect(url_for('showMenu', restaurant_id = restaurant_id))
  else:
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menuItemToDelete = session.query(MenuItem).filter_by(id = menu_id).one()
    return render_template('deletemenuitem.html', restaurant = restaurant, item = menuItemToDelete)

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)