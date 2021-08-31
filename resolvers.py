import json
import pymongo
from flask import Flask, request, render_template, flash, redirect, json, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/CFA"
mongo = PyMongo(app)

def resolve_animaltype_in_animals(animal, info):
    animaltype = mongo.db["AnimalTypes"].find_one({"_id":animal["AnimalTypeID"]})
    return animaltype

def resolve_journal_in_orders(order, info):
    journals = mongo.db["Journals"].find_one({"OrderID":order["_id"]})
    return journals

def resolve_client_in_orders(order, info):
    client = mongo.db["Persons"].find_one({"_id":order["ClientID"]})
    return client

def resolve_animal_in_orders(order, info):
    animal = mongo.db["Animals"].find_one({"_id":order["AnimalID"]})
    return animal

def resolve_client_in_reviews(review, info):
    person = mongo.db["Persons"].find_one({"_id":review["ClientID"]})
    return person

def resolve_animaltype_in_reviews(review, info):
    animaltype = mongo.db["AnimalTypes"].find_one({"_id":review["AnimalTypeID"]})
    return animaltype

def resolve_client_in_animals(animal, info):
    person = mongo.db["Persons"].find_one({"_id":animal["ClientID"]})
    return person

def resolve_order_in_journals(journal, info):
    order = mongo.db["Orders"].find_one({"_id":journal["OrderID"]})
    return order

def resolve_worker_in_journals(journal, info):
    person = mongo.db["Persons"].find_one({"_id":journal["WorkerID"]})
    return person

# def resolve_messages_in_chat(chat, info):
#     messages = mongo.db["ChatMessages"].find({"ChatID":chat["_id"]})
#     return messages

def resolve_chat_in_message(message, info):
    chat = mongo.db["Chats"].find_one({"_id":message["ChatID"]})
    return chat
    
def resolve_person_in_chat(chat, info):
    person = mongo.db["Persons"].find_one({"_id":chat["ClientID"]})
    return person