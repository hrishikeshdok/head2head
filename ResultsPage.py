'''
Created on Dec 13, 2012

@author: Hrishikesh
'''

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from Helper import Helper
from Helper import Category

import os


class ResultsPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        if user:
            key = self.request.get('key')
            
            if key:
                #do something
                key = db.Key(key)
                parentCategory = Category.gql("WHERE __key__ = :1",key)
                categoryUser = key.parent().name()
                items =  db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1 ORDER BY wins DESC",Helper.getCategoryKey(categoryUser, parentCategory[0].name))

                
#                items = Item.gql("WHERE ANCESTOR IS :1",getCategoryKey(user.email(), category))
                template_values = {
                                   'items': items,
                                   'logoutURL' : users.create_logout_url('./')
                                   }
            else:
                categories = db.GqlQuery("SELECT * FROM Category")
                
                template_values = {
                                   'categories': categories,
                                   'logoutURL' : users.create_logout_url('./')
                                   }
                
            path = os.path.join(os.path.dirname(__file__), './html/results.html')
            self.response.out.write(template.render(path, template_values))
        
        else:
            
            self.redirect(users.create_login_url(self.request.uri))
