from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import os
import random

class Category(db.Model):
    name = db.StringProperty()

class Item(db.Model):
    name = db.StringProperty()
    wins = db.IntegerProperty()
    loses = db.IntegerProperty()

def getUserKey(userEmail):
    return db.Key.from_path('User', userEmail)

def getCategoryKey(userEmail,category):
    return db.Key.from_path('User', userEmail,'Category',category)

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
    


class CategoriesPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            categories = db.GqlQuery("SELECT * "
                                "FROM Category "
                                "WHERE ANCESTOR IS :1",
                                getUserKey(user.email()))
            
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
            category = Category(parent=getUserKey(user.email()))
            category.name = self.request.get("category_name")
            category.put()
            categories = db.GqlQuery("SELECT * "
                                "FROM Category "
                                "WHERE ANCESTOR IS :1",
                                getUserKey(user.email()))
            
            template_values = {
                'categories': categories,
                'logoutURL' : users.create_logout_url(self.request.uri)
                        }
            path = os.path.join(os.path.dirname(__file__), './html/category.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class ItemsPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            category = self.request.get("category")
            user = users.get_current_user()

            items = db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",getCategoryKey(user.email(), category))
            
            template_values = {
                               'items' : items,
                               'category' : category,
                               'logoutURL' : users.create_logout_url(self.request.uri)
                               }
            path = os.path.join(os.path.dirname(__file__), './html/items.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
        
    def post(self):
        user = users.get_current_user()
        
        if user:
            category = self.request.get("category")
            
            item = Item(parent=getCategoryKey(user.email(), category))
            item.name = self.request.get("item_name")
            item.wins = 0
            item.loses = 0
            item.put()
            
            items = db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",getCategoryKey(user.email(), category))
            
            template_values = {
                               'items' : items,
                               'category' : category,
                               'logoutURL' : users.create_logout_url(self.request.uri)
                               }
            
            path = os.path.join(os.path.dirname(__file__), './html/items.html')
            self.response.out.write(template.render(path, template_values))
        
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
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

                items =  db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",getCategoryKey(categoryUser, parentCategory[0].name))
                
               
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

                items =  db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",getCategoryKey(categoryUser, parentCategory[0].name))
                
               
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
                items =  db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",getCategoryKey(categoryUser, parentCategory[0].name))

                
#                items = Item.gql("WHERE ANCESTOR IS :1",getCategoryKey(user.email(), category))
                template_values = {
                                   'items': items,
                                   'logoutURL' : users.create_logout_url(self.request.uri)
                                   }
            else:
                categories = db.GqlQuery("SELECT * FROM Category")
                
                template_values = {
                                   'categories': categories,
                                   'logoutURL' : users.create_logout_url(self.request.uri)
                                   }
                
            path = os.path.join(os.path.dirname(__file__), './html/results.html')
            self.response.out.write(template.render(path, template_values))
        
        else:
            
            self.redirect(users.create_login_url(self.request.uri))
        

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/categories', CategoriesPage),
                                      ('/items', ItemsPage),
                                      ('/vote', VotePage),
                                      ('/results', ResultsPage)]
                                     , debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
