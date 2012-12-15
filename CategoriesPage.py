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
        message=" "
        if user:
            if (action == "import"):
                if inputXML:
                    try:
                        root = ET.fromstring(inputXML)
                        #self.response.out.write("ROOT IS - "+ root.tag)
                        if (root is not None) and (root.tag == "CATEGORY"):
                            cat = root.find('NAME')
                            
                            if (cat is not None) and (cat.text):
                                category = Category.gql("WHERE name = :1 and ANCESTOR IS :2", cat.text ,Helper.getUserKey(user.email()))
                                
                                if category.count() == 0:
                                    #self.response.out.write( "Cat doesnt exist. Creating new category and adding all new items")
                                    category = Category(parent=Helper.getUserKey(user.email()))
                                    category.name = cat.text
                                    category.put()
                                    
                                    for item in root.findall('ITEM'):
                                        if len(item.findall('NAME')) == 1 and (item.find('NAME').text):
                                            itemName = item.find('NAME').text
                                            newItem = Item(parent=Helper.getCategoryKey(user.email(), category.name))
                                            newItem.name = itemName
                                            newItem.wins = 0
                                            newItem.loses = 0 
                                            newItem.put()
                                        else:
                                            #self.response.out.write("Invalid XML more/less than one name for Item")
                                            message= "Invalid XML more/less than one name for Item"
                                            Category.delete(category)
                                else:
                                    category = category[0]
                                    #self.response.out.write("<br/>Category already exists<br/>")
                                    #check for new items in XML and add them in datastore
                                    itemsInXml = []
                                    itemsSaved = []
                                    escape = False
                                    for item in root.findall('ITEM'):
                                        #check if there are more than one Item names
                                        if (len(item.findall('NAME')) == 1) and (item.find('NAME').text):
                                            itemName = item.find('NAME').text
                                            #self.response.out.write("Checking for Item "+itemName + "<br/>")
                                            newItem = Item.gql("WHERE name = :1 AND ANCESTOR IS :2",itemName,Helper.getCategoryKey(user.email(), category.name))
                                            #self.response.out.write("Count " + str(newItem.count()) +"<br/>")
                                            if  newItem.count() == 0:
#                                                self.response.out.write("Item "+ itemName+ " doesnot exist. Adding it<br/>")
                                                newItem = Item(parent=Helper.getCategoryKey(user.email(), category.name))
                                                newItem.name = itemName
                                                newItem.wins = 0
                                                newItem.loses = 0
                                                newItem.put()
                                            itemsSaved.append(item)
                                            itemsInXml.append(itemName)
                                        
                                        else:
#                                            self.response.out.write("Invalid XML more/less than one name for Item")
                                            message = "Invalid XML more/less than one name for Item"
                                            for item in itemsSaved:
                                                Item.delete(item)
                                                escape = True
                                            #raise Exception("IGNORE")
                                            
                                    if not escape:
                                        #check for items in Datastore that are not in XML. Delete them
                                        #items = Item.all()
                                        items = Item.gql("WHERE ANCESTOR IS :1",Helper.getCategoryKey(user.email(), category.name))
                                        for item in items:
                                            self.response.out.write("Checking for  "+ item.name + " in XML <br/>")
                                            try:
                                                itemsInXml.remove(item.name)
    #                                            self.response.out.write(item.name + " is there in XML. Retain it <br/>")
                                            except ValueError:
    #                                            self.response.out.write("Item "+ item.name+ " is not there in XML. Deleting<br/>")
                                                Item.delete(item)
                                            
                                        

                            else:
                                #self.response.out.write("Invalid XML no Cat name")
                                message = "Invalid XML no Cat name"
                        else:
#                            self.response.out.write("Invalid XML")
                            message = "Invalid XML"
                       
                    except:
#                        self.response.out.write("Invalid File")
                        message = "Invalid File"
                else:
                    #self.response.out.write("Please choose file")
                    message = "Please choose a file"
                
                
                categories = db.GqlQuery("SELECT * "
                                    "FROM Category ")
                #message = "invalid xml"
                template_values = {
                    'categories': categories,
                    'user':user,
                    'message':message,
                    'logoutURL' : users.create_logout_url('./')
                            }
                path = os.path.join(os.path.dirname(__file__), './html/category.html')
                self.response.out.write(template.render(path, template_values))
                
                #self.redirect('./categories', permanent=False)
            else:
                newCategoryName=self.request.get("category_name").strip()
                ifAlreadyExists = Category.gql("WHERE name = :1 AND ANCESTOR IS :2",newCategoryName,Helper.getUserKey(user.email()))
                if (ifAlreadyExists.count() == 0) and newCategoryName:
                    category = Category(parent=Helper.getUserKey(user.email()))
                    category.name = self.request.get("category_name")
                    category.put()
                else:
                    if newCategoryName:
                        message = "Category already exists"
                    else:
                        message = "Category name cannot be empty" 
                categories = db.GqlQuery("SELECT * "
                                    "FROM Category ")
    #                                "WHERE ANCESTOR IS :1",
    #                                Helper.getUserKey(user.email()))
                
                template_values = {
                    'categories': categories,
                    'user':user,
                    'message':message,
                    'logoutURL' : users.create_logout_url('./')
                            }
                path = os.path.join(os.path.dirname(__file__), './html/category.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

