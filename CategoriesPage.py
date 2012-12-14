from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from Helper import Helper
from Helper import Category

import os


class CategoriesPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            categories = db.GqlQuery("SELECT * "
                                "FROM Category "
                                "WHERE ANCESTOR IS :1",
                                Helper.getUserKey(user.email()))
            
            template_values = {
                'categories': categories,
                'logoutURL' : users.create_logout_url(self.request.uri)
                        }
            path = os.path.join(os.path.dirname(__file__), './html/category.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
    def post(self):
        user = users.get_current_user()
        if user:
            category = Category(parent=Helper.getUserKey(user.email()))
            category.name = self.request.get("category_name")
            category.put()
            categories = db.GqlQuery("SELECT * "
                                "FROM Category "
                                "WHERE ANCESTOR IS :1",
                                Helper.getUserKey(user.email()))
            
            template_values = {
                'categories': categories,
                'logoutURL' : users.create_logout_url(self.request.uri)
                        }
            path = os.path.join(os.path.dirname(__file__), './html/category.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

