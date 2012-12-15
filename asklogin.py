from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import os
import CategoriesPage
import ItemsPage
import VotePage
import ResultsPage
import Search
import Comments


class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template_values = {
                               'user':user ,
                               'logoutURL' : users.create_logout_url(self.request.uri) 
                               }
            
            path = os.path.join(os.path.dirname(__file__), './html/index.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
    


        

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/categories', CategoriesPage.CategoriesPage),
                                      ('/items', ItemsPage.ItemsPage),
                                      ('/vote', VotePage.VotePage),
                                      ('/results', ResultsPage.ResultsPage),
                                      ('/search', Search.SearchPage),
                                      ('/showComments', Comments.ShowCommentsPage),
                                      ('/addComment',Comments.AddCommentsPage)]
                                      ,debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
