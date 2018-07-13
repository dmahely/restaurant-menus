from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
# interface between html and python
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # page listing restaurant names
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurants = session.query(Restaurant).all()
                output = "<html><body>"
                output += "<a href='/restaurants/new'> Make a New Restaurant Here</a><br>"
                for restaurant in restaurants:
                    output += "<p> " + restaurant.name + "</p>"
                    output += "<a href='#'>Edit</a><br>"
                    output += "<a href='#'>Delete</a>"
                    output += "<br>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            
            # page allowing user to add restaurant via form
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                form = "<html><body><form action='/restaurants/new' method='POST' enctype='multipart/form-data'>"
                form += "<input type='text' name='newRestaurantName' placeholder='New Restaurant Name'>"
                form += "<input type='submit' value='Create'>"
                form += "</form></body></html>"
                self.wfile.write(form)
                print(form)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            # adds new restaurant named in the form in the database, and returns to restaurant page
            if self.path.endswith('/restaurants/new'):
                ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                userRestaurant = Restaurant(name = messagecontent[0])
                session.add(userRestaurant)
                session.commit()
                
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        port = 9999
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
