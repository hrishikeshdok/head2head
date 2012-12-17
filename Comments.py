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
from Helper import ItemComment

import os

class ShowCommentsPage(webapp.RequestHandler):
    def post(self):
        itemName = self.request.get("itemName")
        categoryName = self.request.get("categoryName")
        userEmail = self.request.get("userEmail")
        
#        comments = ItemComment.gql("WHERE ANCESTOR IS :1",Helper.getItemKey(userEmail, categoryName, itemName))
        comments = ItemComment.all()
        commentsList = []
        for comment in comments:
            if (comment.category == categoryName) and (comment.item == itemName): 
                commentsList.append(comment)
        
       
        items =  db.GqlQuery("SELECT * FROM Item WHERE ANCESTOR IS :1 ORDER BY wins DESC",Helper.getCategoryKey(userEmail, categoryName))
        
        template_values = {
                           'items': items,
                           'logoutURL' : users.create_logout_url('./'),
                           'comments':commentsList
                           }
        path = os.path.join(os.path.dirname(__file__), './html/results.html')
        self.response.out.write(template.render(path, template_values))

class AddCommentsPage(webapp.RequestHandler):
    def post(self):
        itemName = self.request.get("itemName")
        categoryName = self.request.get("categoryName")
        userEmail = self.request.get("userEmail")
        comment = self.request.get("comment")
        owner = self.request.get("owner")
        
        comment = str(comment).strip()
        message = ""
        if comment:
            ifAlreadyExists = []
            
            #self.response.out.write("Key is "+ str(Helper.getItemKey(userEmail, categoryName, itemName)))
            ifAlreadyExists = ItemComment.gql("WHERE ANCESTOR IS :1",Helper.getItemKey(userEmail, categoryName, itemName))
            
            #self.response.out.write("Key is "+ str(Helper.getItemKey(userEmail, categoryName, itemName)))
            #self.response.out.write("Count is "+ str(ifAlreadyExists.count()))
    
            
                    
            if (ifAlreadyExists.count() == 0):
                #self.response.out.write("Adding comment for " + itemName + " " + categoryName + " " + userEmail)
                itemComment = ItemComment(parent=Helper.getItemKey(userEmail, categoryName, itemName))
                itemComment.comment = comment
                itemComment.commenter = userEmail
                itemComment.item = itemName
                itemComment.category = categoryName
                itemComment.put()
                message="Comment Saved"
            else:
                message="You can comment only once on an item"

        else:
            #self.response.out.write("empty comment")
            message = "Cannot enter empty comment"
            
            
        items = Item.gql("WHERE ANCESTOR IS :1",Helper.getCategoryKey(owner, categoryName))
        template_values = {
                           'items' : items,
                           'owner': owner,
                           'user' : users.get_current_user(),
                           'category' : categoryName,
                           'logoutURL' : users.create_logout_url('./'),
                           'message' : message
                  }
        path = os.path.join(os.path.dirname(__file__), './html/items.html')
        self.response.out.write(template.render(path, template_values))
