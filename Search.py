'''
Created on Dec 15, 2012

@author: Hrishikesh
'''
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from Helper import Helper
from Helper import Category
from Helper import Item

import re
import os

class SearchPage(webapp.RequestHandler):
    def post(self):
        searchItem = self.request.get("searchBox")
        matchedCategories = []
        matchedItems = []
        searchFound=False
        if searchItem:
            #find matching categories
            cats = Category.all()
            
            
            
            for cat in cats:
                searchresult = re.search(str(searchItem).lower(),str(cat.name).lower())
                if searchresult is not None:
                    matchedCategories.append(cat)
                    searchFound = True
                    
            #find matching items
            items = Item.all()
            
            
            
            for item in items:
                searchresult = re.search(str(searchItem).lower(),str(item.name).lower())
                if searchresult is not None:
                    matchedItems.append(item)
                    searchFound = True
                    
        template_values = {
                'matchedCategories': matchedCategories,
                'matchedItems': matchedItems,
                'logoutURL' : users.create_logout_url('./'),
                'searchItem':searchItem,
                'searchFound':searchFound
                        }
        path = os.path.join(os.path.dirname(__file__), './html/search.html')
        self.response.out.write(template.render(path, template_values))
        
        #below query looks from abc at beginning of string
        #db.GqlQuery("SELECT * FROM MyModel WHERE prop >= :1 AND prop < :2", "abc", u"abc" + u"\ufffd")
        
        
        
        