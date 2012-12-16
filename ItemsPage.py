'''
Created on Dec 13, 2012

@author: Hrishikesh
'''
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from Helper import Helper, Category, ItemComment
from Helper import Item

from xml.etree.ElementTree import Element, SubElement, tostring, XML, fromstring



import os

class ItemsPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            
            category = self.request.get("category")
            owner = self.request.get("owner")
            
            newCategoryName = self.request.get("newCategoryName").strip()
            
            newItemName = self.request.get("newItemName").strip()
            oldItemName = self.request.get("oldItemName").strip()
            
            displayItems = True
          
            if newCategoryName:
                owner = user.email()
                if newCategoryName != "delete":
                    ifAlreadyExists = Category.gql("WHERE name = :1 and ANCESTOR IS :2",newCategoryName,Helper.getUserKey(user.email()))
                    if ifAlreadyExists.count() == 0:
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
                    else:
                        message = "Category already exists"
                        
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
                                    "FROM Category ")
#                                    "WHERE ANCESTOR IS :1",
#                                    Helper.getUserKey(user.email()))
                    
                    template_values = {
                                       'categories' : categories,
                                       'user':user,
                                       'logoutURL' : users.create_logout_url('./'),
                                       'message' : message
                                       }
                    displayItems = False
                    path = os.path.join(os.path.dirname(__file__), './html/category.html')
                    self.response.out.write(template.render(path, template_values))
                
            if newItemName:
                owner = user.email()
                if newItemName != "delete":
                    ifAlreadyExists = Item.gql("WHERE name = :1 and ANCESTOR IS :2",newItemName, Helper.getCategoryKey(user.email(), category))
                    if ifAlreadyExists.count() == 0:
                        itemToEdit = Item.gql("WHERE name = :1 and ANCESTOR IS :2",oldItemName, Helper.getCategoryKey(user.email(), category))[0]
                        itemToEdit.name = newItemName
                        itemToEdit.wins = 0
                        itemToEdit.loses = 0
                        itemToEdit.put()
                        message = oldItemName + " renamed to " + newItemName
                    else:
                        message = "Item already exists"
                    displayItems = True
                else:
                    itemToDelete = Item.gql("WHERE name = :1 and ANCESTOR IS :2",oldItemName, Helper.getCategoryKey(user.email(), category))[0]
                    Item.delete(itemToDelete)
                    message = oldItemName + " deleted "
                    displayItems = True
            
            if displayItems:
                items = db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",Helper.getCategoryKey(owner, category))
                
                template_values = {
                                   'items' : items,
                                   'owner': owner,
                                   'user' : user,
                                   'category' : category,
                                   'logoutURL' : users.create_logout_url('./'),
                                   'ItemComment':ItemComment,
                                   'Helper':Helper
                                   }
                path = os.path.join(os.path.dirname(__file__), './html/items.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
    
    def exportToXml(self, owner, category):
        self.response.headers['Content-Type'] = 'text/xml'
        file_name = category.replace(' ', '_')
        self.response.headers['Content-Disposition'] = "attachment; filename=" + str(file_name) + ".xml"
        
        # create xml file        
        # get all items in the chosen category
        items = db.GqlQuery("SELECT * "
                             "FROM Item "
                             "WHERE ANCESTOR IS :1 ",
                             Helper.getCategoryKey(owner, category))
                                                    
        root = Element('CATEGORY')
        categoryName = SubElement(root, 'NAME')
        categoryName.text = category
        
        # create intermediate nodes for each item
        for item in items:
            itemTag = SubElement(root, 'ITEM')
            itemNameTag = SubElement(itemTag, 'NAME')
            itemNameTag.text = item.name
            
        self.response.out.write(tostring(root, encoding="us-ascii", method="xml"))
    
    def post(self):
        user = users.get_current_user()
        message=""
        if user:
            category = self.request.get("category")
            isExport = self.request.get("isExport")
            owner = self.request.get("owner")
            
            if isExport:
                self.exportToXml(owner,category)
            else:
                newItemName = self.request.get("item_name").strip()
                ifAlreadyExists  = Item.gql("WHERE name = :1 AND ANCESTOR IS :2",newItemName,Helper.getCategoryKey(user.email(), category))
                
                if (ifAlreadyExists.count() == 0) and newItemName:
                    item = Item(parent=Helper.getCategoryKey(user.email(), category))
                    item.name = self.request.get("item_name")
                    item.wins = 0
                    item.loses = 0
                    item.put()
                else:
                    if newItemName:
                        message = "Item already exists"
                    else:
                        message = "Item name cannot be empty or spaces"
                
                items = db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1",Helper.getCategoryKey(user.email(), category))
                
                template_values = {
                                   'items' : items,
                                   'category' : category,
                                   'message' : message,
                                   'logoutURL' : users.create_logout_url('./'),
                                   'user':user,
                                   'owner' : owner
                                   }
                
                path = os.path.join(os.path.dirname(__file__), './html/items.html')
                self.response.out.write(template.render(path, template_values))
        
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
    