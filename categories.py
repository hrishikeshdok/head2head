from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class MainHandler(webapp.RequestHandler):
    def get(self):
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('you are in categories')


app = webapp.WSGIApplication([('/categories', MainHandler)], debug=True)

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()
