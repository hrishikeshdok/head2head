from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

	
	

class MainPage(webapp.RequestHandler):
	def get(self):

		user = users.get_current_user()        
		if user:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('Hello, ' + user.nickname() + '<br/>')
			self.response.out.write('<br/><a href="./categories">Categories</a><br/>')
		else:
			self.redirect(users.create_login_url(self.request.uri))

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
	print 'in main'
	run_wsgi_app(application)

if __name__ == "__main__":
    main()

