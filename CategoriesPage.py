from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from Helper import Helper
from Helper import Category
from Helper import Item


import os
from xml.etree import ElementTree as ET


class CategoriesPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            categories = db.GqlQuery("SELECT * "
                                "FROM Category ")
                                #"WHERE ANCESTOR IS :1",
                                #Helper.getUserKey(user.email()))
            
            template_values = {
                'categories': categories,
                'logoutURL' : users.create_logout_url('./')
                        }
            path = os.path.join(os.path.dirname(__file__), './html/category.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
    def post(self):
        user = users.get_current_user()
        action = self.request.get("action")
        inputXML = self.request.get("chooseFile")
        if user:
            if (action == "import"):
                if inputXML:
                    try:
                        root = ET.fromstring(inputXML)
                        
                        if root is not None:
                            cat = root.find('NAME')
                            
                            if cat is not None:
                                category = Category.gql("WHERE name = :1 and ANCESTOR IS :2", cat.text ,Helper.getUserKey(user.email()))
                                
                                if category.count() == 0:
                                    self.response.out.write( "Cat doesnt exist. Creating new category and adding all new items")
                                    category = Category(parent=Helper.getUserKey(user.email()))
                                    category.name = cat.text
                                    category.put()
                                    
                                    for item in root.findall('ITEM'):
                                        itemName = item.find('NAME').text
                                        newItem = Item(parent=Helper.getCategoryKey(user.email(), category.name))
                                        newItem.name = itemName
                                        newItem.wins = 0
                                        newItem.loses = 0 
                                        newItem.put()
                                else:
                                    category = category[0]
                                    self.response.out.write("<br/>Category already exists<br/>")
                                    #check for new items in XML and add them in datastore
                                    itemsInXml = []
                                    itemsSaved = []
                                    for item in root.findall('ITEM'):
                                        itemName = item.find('NAME').text
                                        self.response.out.write("Checking for Item "+itemName + "<br/>")
                                        newItem = Item.gql("WHERE name = :1 AND ANCESTOR IS :2",itemName,Helper.getCategoryKey(user.email(), category.name))
                                        self.response.out.write("Count " + str(newItem.count()) +"<br/>")
                                        if  newItem.count() == 0:
                                            self.response.out.write("Item "+ itemName+ " doesnot exist. Adding it<br/>")
                                            newItem = Item(parent=Helper.getCategoryKey(user.email(), category.name))
                                            newItem.name = itemName
                                            newItem.wins = 0
                                            newItem.loses = 0
                                            newItem.put()
                                        itemsSaved.append(item)
                                        itemsInXml.append(itemName)
                                            
                                    #check for items in Datastore that are not in XML. Delete them
                                    items = Item.all()
                                    
                                    for item in items:
                                        self.response.out.write("Checking for  "+ item.name + " in XML <br/>")
                                        try:
                                            itemsInXml.remove(item.name)
                                            self.response.out.write(item.name + " is there in XML. Retain it <br/>")
                                        except ValueError:
                                            self.response.out.write("Item "+ item.name+ " is not there in XML. Deleting<br/>")
                                            Item.delete(item)
    
                            else:
                                self.response.out.write("Invalid XML")
                        else:
                            self.response.out.write("Invalid XML")
                       
                    except :
                        self.response.out.write("Invalid File")
                else:
                    y=2
                    self.response.out.write("Please choose file")
                
                
                categories = db.GqlQuery("SELECT * "
                                    "FROM Category ")
                #message = "invalid xml"
                template_values = {
                    'categories': categories,
                    'user':user,
                    'logoutURL' : users.create_logout_url('./')
                            }
                path = os.path.join(os.path.dirname(__file__), './html/category.html')
                self.response.out.write(template.render(path, template_values))
                
                #self.redirect('./categories', permanent=False)
            else:
                category = Category(parent=Helper.getUserKey(user.email()))
                category.name = self.request.get("category_name")
                category.put()
                categories = db.GqlQuery("SELECT * "
                                    "FROM Category ")
    #                                "WHERE ANCESTOR IS :1",
    #                                Helper.getUserKey(user.email()))
                
                template_values = {
                    'categories': categories,
                    'user':user,
                    'logoutURL' : users.create_logout_url('./')
                            }
                path = os.path.join(os.path.dirname(__file__), './html/category.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

