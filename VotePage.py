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
from Helper import Item

import os
import random

class VotePage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            #check for key, if not exist show all categories from all users
            key = self.request.get("key")
            wKey = self.request.get("wKey")
            lKey = self.request.get("lKey")
            
            
            if (key and ( not (wKey and lKey) ) ):
                #item_1 = Item.all().order('rand_num').filter('rand_num >=', rand_num).filter(k, value) .get()
                key = db.Key(key)
                parentCategory = Category.gql("WHERE __key__ = :1",key)
                
               
                categoryUser = key.parent().name()

                items =  db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",Helper.getCategoryKey(categoryUser, parentCategory[0].name))
                
               
                item_1 = "Not Enough Items"
                item_2 = "Not Enough Items"                
                
               
                if( items.count() != 0):
                    randomNumber_1 = random.randint(0,items.count() - 1 )
                    randomNumber_2 = randomNumber_1
                     
                    while(randomNumber_1 == randomNumber_2):
                        randomNumber_2 = random.randint(0,items.count() - 1 )
                    
                    item_1 = items[randomNumber_1]
                    item_2 = items[randomNumber_2]
                    
                template_values = {
                                    'item_1': item_1,
                                    'item_2': item_2,
                                    'key':key,
                                   'logoutURL' : users.create_logout_url(self.request.uri)
                                   }
                
                path = os.path.join(os.path.dirname(__file__), './html/vote.html')
                self.response.out.write(template.render(path, template_values))
            
            elif (key and ( (wKey and lKey)  )):
                
                key = db.Key(key)
                wKey = db.Key(wKey)
                lKey = db.Key(lKey)
              
                winningItem = Item.gql("WHERE __key__ = :1",wKey)[0]
                losingItem = Item.gql("WHERE __key__ = :1",lKey)[0]

                
                winningItem.wins = winningItem.wins + 1
                winningItem.put()
                
                losingItem.loses = losingItem.loses + 1
                losingItem.put() 
                
                #self.redirect("./vote?category=%s", permanent=False)
                
                message = winningItem.name + ' wins over ' + losingItem.name
                
                #get 2 new random items
                key = self.request.get("key")
                key = db.Key(key)
                parentCategory = Category.gql("WHERE __key__ = :1",key)
                
               
                categoryUser = key.parent().name()

                items =  db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",Helper.getCategoryKey(categoryUser, parentCategory[0].name))
                
               
                item_1 = "Not Enough Items"
                item_2 = "Not Enough Items"                
                
               
                if( items.count() != 0):
                    randomNumber_1 = random.randint(0,items.count() - 1 )
                    randomNumber_2 = randomNumber_1
                     
                    while(randomNumber_1 == randomNumber_2):
                        randomNumber_2 = random.randint(0,items.count() - 1 )
                    
                    item_1 = items[randomNumber_1]
                    item_2 = items[randomNumber_2]

                    
                              
                template_values = {
                                    'item_1': item_1,
                                    'item_2': item_2,
                                    'key':key,
                                    'logoutURL' : users.create_logout_url(self.request.uri),
                                    'message' : message
                                   }
                
                path = os.path.join(os.path.dirname(__file__), './html/vote.html')
                self.response.out.write(template.render(path, template_values)) 
                
                
            
            else:
                categories = Category.all() 
                template_values = {
                                   'categories': categories
                                   }
                
                path = os.path.join(os.path.dirname(__file__), './html/vote.html')
                self.response.out.write(template.render(path, template_values))
                
                
        else:
            self.redirect(users.create_login_url(self.request.uri))
            