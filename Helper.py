'''
Created on Dec 13, 2012

@author: Hrishikesh
'''
from google.appengine.ext import db

class Category(db.Model):
    name = db.StringProperty()

class Item(db.Model):
    name = db.StringProperty()
    wins = db.IntegerProperty()
    loses = db.IntegerProperty()


class Helper:
    @staticmethod
    def getUserKey(userEmail):
        return db.Key.from_path('User', userEmail)
    
    @staticmethod
    def getCategoryKey(userEmail,category):
        return db.Key.from_path('User', userEmail,'Category',category)