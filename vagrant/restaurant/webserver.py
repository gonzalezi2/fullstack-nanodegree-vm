#!/usr/bin/python
# -*- coding: utf-8 -*-
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
#session.commit()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith('/delete'):
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()

                    output = '<html><body>'
                    output += '<h1>Are you sure you want to delete this restaurant?</h1>'
                    output += '<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/delete">' % restaurantIDPath
                    output += '<input type="submit" value="Delete">'
                    output += '</form>'
                    output += '</body></html>'

                    self.wfile.write(output)

            if self.path.endswith('/edit'):
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()

                    output = '<html><body>'
                    output += '<h1>Rename %s' % myRestaurantQuery.name
                    output += '<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/edit">' % restaurantIDPath
                    output += '<input name="newRestaurantName" type="text" placeholder="%s">' % myRestaurantQuery.name
                    output += '<input type="submit" value="Rename">'
                    output += '</form>'
                    output += '</body></html>'

                    self.wfile.write(output)

            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                output = ''
                output += '<html><body>'
                output += \
                   """<form method='POST' enctype='multipart/form-data'
					action='/restaurants/new'><h1>Make a New Restaurant</h1>
					<input name='newRestaurantName' type='text'><input type='submit' value='Create'></form>"""
                output += '</html></body>'
                
                self.wfile.write(output)


            if self.path.endswith('/restaurants'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                restaurants = session.query(Restaurant).all()

                output = ''
                output = '<html><body>'
                output = '<br><a href="/restaurants/new">Add a new restaurant</a><br>'
                for rest in restaurants:
                    output += '<p> %s </p>' % rest.name
                    output += '<a href="/restaurants/%s/edit">Edit</a> <br>' % rest.id
                    output += '<a href="/restaurants/%s/delete">Delete</a>' % rest.id
                #output += '<html><body>Hello!'
                #output += \
                #    """<form method='POST' enctype='multipart/form-data'
				#	action='/hello'><h2>What would you like me to say?</h2>
				#	<input name='message' type='text'><input type='submit' value='Submit'></form>"""

                output += '</body></html>'
                self.wfile.write(output)
                print(output)
                return
        except IOError:
            self.send_error(404, 'File Not Found %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/delete'):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                if myRestaurantQuery != []:

                    session.delete(myRestaurantQuery)
                    session.commit()
                    
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith('/edit'):
                (ctype, pdict) = \
                    cgi.parse_header(self.headers.getheader('content-type'
                        ))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantName = fields.get('newRestaurantName')
                newRestaurant = Restaurant(name = restaurantName[0])
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()

                if myRestaurantQuery != []:
                    myRestaurantQuery.name = restaurantName[0]
                    session.add(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith('/restaurants/new'):
                (ctype, pdict) = \
                    cgi.parse_header(self.headers.getheader('content-type'
                        ))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantName = fields.get('newRestaurantName')
                newRestaurant = Restaurant(name = restaurantName[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                

            # self.send_response(301)
            # self.send_header('Content-type', 'text/html')
            # self.end_headers()
            # (ctype, pdict) = \
            #     cgi.parse_header(self.headers.getheader('content-type'
            #         ))
            # if ctype == 'multipart/form-data':
            #     fields = cgi.parse_multipart(self.rfile, pdict)
            #     messagecontent = fields.get('message')
            # output = ''
            # output += '<html><body>'
            # output += ' <h2> Okay, how about this: </h2>'
            # output += '<h1> %s </h1>' % messagecontent[0]
            # output += \
            #     '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            # output += '</body></html>'
            # self.wfile.write(output)
            # print(output)
        except:

            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print('Web Server running on port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(' ^C entered, stopping web server....')
        server.socket.close()


if __name__ == '__main__':
    main()
