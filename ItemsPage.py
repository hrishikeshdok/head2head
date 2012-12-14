'''
Created on Dec 13, 2012

@author: Hrishikesh
'''
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from Helper import Helper, Category
from Helper import Item

import os

class ItemsPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            
            category = self.request.get("category")
            newCategoryName = self.request.get("newCategoryName")
            
            newItemName = self.request.get("newItemName")
            oldItemName = self.request.get("oldItemName")
            
            displayItems = True
          
            if newCategoryName:
                if newCategoryName != "delete":
                    newCategory = Category(parent=Helper.getUserKey(user.email()))
                    newCategory.name = newCategoryName
                    newCategory.put()
                    
                    items = Item.gql("WHERE ANCESTOR IS :1", Helper.getCategoryKey(user.email(), category))
                    
                    for item in items:
                        newItem = Item(parent=Helper.getCategoryKey(user.email(), newCategory.name))
                        newItem.name = item.name
                        newItem.wins = item.wins
                        newItem.loses = item.loses
                        newItem.put()
                        Item.delete(item)
                    
                    categoryToEdit =  Category.gql("WHERE name = :1 and ANCESTOR IS :2",category,Helper.getUserKey(user.email()))[0]
                    Category.delete(categoryToEdit)

                    message = category + " renamed to " + newCategoryName
                    category = newCategoryName
                    displayItems = True
                    
                else:
                    categoryToDelete =  Category.gql("WHERE name = :1 and ANCESTOR IS :2",category,Helper.getUserKey(user.email()))[0]
                    
                    items = Item.gql("WHERE ANCESTOR IS :1", Helper.getCategoryKey(user.email(), category))
                    
                    for item in items:
                        Item.delete(item)
                    
                    Category.delete(categoryToDelete)
                    message = category + " deleted " 
                    #self.redirect("./categories", permanent=False)
                    categories = db.GqlQuery("SELECT * "
                                    "FROM Category "
                                    "WHERE ANCESTOR IS :1",
                                    Helper.getUserKey(user.email()))
                    
                    template_values = {
                                       'categories' : categories,
                                       'logoutURL' : users.create_logout_url(self.request.uri),
                                       'message' : message
                                       }
                    displayItems = False
                    path = os.path.join(os.path.dirname(__file__), './html/category.html')
                    self.response.out.write(template.render(path, template_values))
                
            if newItemName:
                if newItemName != "delete":
                    itemToEdit = Item.gql("WHERE name = :1 and ANCESTOR IS :2",oldItemName, Helper.getCategoryKey(user.email(), category))[0]
                    itemToEdit.name = newItemName
                    itemToEdit.put()
                    message = oldItemName + " renamed to " + newItemName
                    displayItems = True
                else:
                    itemToDelete = Item.gql("WHERE name = :1 and ANCESTOR IS :2",oldItemName, Helper.getCategoryKey(user.email(), category))[0]
                    Item.delete(itemToDelete)
                    message = oldItemName + " deleted "
                    displayItems = True
            
            if displayItems:
                items = db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",Helper.getCategoryKey(user.email(), category))
                
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
            
            item = Item(parent=Helper.getCategoryKey(user.email(), category))
            item.name = self.request.get("item_name")
            item.wins = 0
            item.loses = 0
            item.put()
            
            items = db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",Helper.getCategoryKey(user.email(), category))
            
            template_values = {
                               'items' : items,
                               'category' : category,
                               'logoutURL' : users.create_logout_url(self.request.uri)
                               }
            
            path = os.path.join(os.path.dirname(__file__), './html/items.html')
            self.response.out.write(template.render(path, template_values))
        
        else:
            self.redirect(users.create_login_url(self.request.uri))
