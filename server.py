# -*- coding: utf-8 -*-
import random
import string
import datetime
import json  # Подключаем библиотеку для преобразования данных в формат JSON
import os # Подключаем библиотеку для работы с функциями операционной системы (для проверки файла)
import pymongo
from bson.json_util import dumps, loads
from bson import json_util
import win32event
import win32api
from winerror import ERROR_ALREADY_EXISTS
from sys import exit
from flask import Flask, request, render_template, flash, redirect, json, jsonify
from flask_pymongo import PyMongo
from ariadne import ObjectType, QueryType, graphql_sync, make_executable_schema, MutationType, load_schema_from_path
from ariadne.constants import PLAYGROUND_HTML
import sys
import resolvers as r

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/CFA"
mongo = PyMongo(app)
type_defs = load_schema_from_path('schema.graphql')
query = QueryType()
mutation = MutationType()

person = ObjectType("Person")
journal= ObjectType("Journal")
order = ObjectType("Order")
review = ObjectType("Review")
animal = ObjectType("Animal")
message = ObjectType("ChatMessage")
animaltype = ObjectType("AnimalType")
chat = ObjectType("Chat")

review.set_field('AnimalType', r.resolve_animaltype_in_reviews)
review.set_field('Client', r.resolve_client_in_reviews)
animal.set_field('AnimalType', r.resolve_animaltype_in_animals)
animal.set_field('Client', r.resolve_client_in_animals)
order.set_field('Client', r.resolve_client_in_orders)
order.set_field('Animal', r.resolve_animal_in_orders)
order.set_field('Journals', r.resolve_journal_in_orders)#в orders поле Journal
journal.set_field('Order', r.resolve_order_in_journals)
journal.set_field('Worker', r.resolve_worker_in_journals)
message.set_field('Chat', r.resolve_chat_in_message)
# chat.set_field('Messages', r.resolve_messages_in_chat)
chat.set_field('Person', r.resolve_person_in_chat)



def check_token(token):
    if ((len(token)) > 0):
        col = mongo.db["Persons"].find_one({"Token":str(token)})
        if col != None:
            chekingToken = col["Token"]
            if chekingToken == token:
                return True
    return False

def user_auth(login, password):
    col = mongo.db["Persons"]
    for x in col.find():
        if x["Login"] == login and x["Password"] == password:
            return True
    return False

@mutation.field("authorization")#авторизация
def authorization(_, info, login, password):
    add_operation_in_journal('authorization')
    token = ""
    if user_auth(login, password) == True:
        print("Попытка авторизоваться прошла успешно")
        token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
        x = mongo.db["Persons"].find_one({"Login":login, "Password":password})
        x["Token"] = token
        x["DateOfIssueToken"] = datetime.datetime.now()
        mongo.db["Persons"].save(x)
        return {"Token":token}
    else: 
        raise Exception("Ошибка авторизации!")

@mutation.field("add_person")#регистрация пользователя
def add_person(_, info, input):
    add_operation_in_journal('add_person')
    newperson = {}
    newperson["_id"] = (get_max_id("Persons")) + 1
    newperson["Token"] = None
    newperson["DateOfIssueToken"] = None
    newperson["State"] = 1
    newperson["Login"] = str(input["Login"])
    newperson["Password"] = str(input["Password"])
    newperson["Name"] = str(input["Name"])
    newperson["Phone"] = str(input["Phone"])
    newperson["Email"] = str(input["Email"])
    newperson["Birthday"] = str(input["Birthday"])
    newperson["Address"] = str(input["Address"])
    mongo.db["Persons"].save(newperson)
    newchat = {}
    newchat["_id"] = (get_max_id("Chats")) + 1
    newchat["DelTime"] = None
    newchat["Client"] = newperson["_id"]
    mongo.db["Chats"].save(newchat)
    return "Пользователь успешно зарегестрирован."

@mutation.field("add_order")#добавление заказа
def add_order(_, info, input):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('add_order')
        token = request.headers['Token']
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            neworder = {}
            neworder["_id"] = (get_max_id("Orders")) + 1
            neworder["Status"] = "В обработке"
            datest = str(input["DateStart"]).split('-')
            dateend = str(input["DateEnd"]).split('-')
            neworder["DateStart"] = datetime.datetime(int(datest[0]), int(datest[1]), int(datest[2]))
            neworder["DateEnd"] = datetime.datetime(int(dateend[0]), int(dateend[1]), int(dateend[2]))
            neworder["ClientID"] = person["_id"]
            neworder["AnimalID"] = int(input["AnimalID"])
            neworder["DeliveryToTheHotel"] = str(input["DeliveryToTheHotel"])
            neworder["FromDeliveryAddress"] = str(input["FromDeliveryAddress"])
            neworder["FromDeliveryTime"] = str(input["FromDeliveryTime"])
            neworder["DeliveryFromHotel"] = str(input["DeliveryFromHotel"])
            neworder["ToDeliveryAddress"] = str(input["ToDeliveryAddress"])
            neworder["ToDeliveryTime"] = str(input["ToDeliveryTime"])
            neworder["Comment"] = str(input["Comment"])
            neworder["DelTime"] = None
            neworder["Price"] = 5000
            mongo.db["Orders"].save(neworder)
            return "Заказ успешно добавлен."
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")


@mutation.field("add_review")#!добавление отзыва
def add_review(_, info, input):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('add_review')
        token = request.headers['Token']
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            newreview = {}
            newreview["_id"] = (get_max_id("Reviews")) + 1
            newreview["AnimalTypeID"] = int(input['AnimalTypeID'])
            newreview["Body"] = str(input["Body"])
            newreview["AddTime"] = datetime.datetime.now()
            newreview["DelTime"] = None
            newreview["ClientID"] = person["_id"]
            mongo.db["Reviews"].save(newreview)
            return "Отзыв успешно добавлен."
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")
@mutation.field("add_animal")#!добавление животного
def add_animal(_, info, input):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('add_animal')
        token = request.headers["Token"]
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            newanimal={}
            newanimal["_id"] = (get_max_id("Animals")) + 1
            newanimal["Name"] = str(input["Name"])
            newanimal["AnimalTypeID"] = int(input["AnimalTypeID"])
            newanimal["Sex"] = int(input["Sex"])
            newanimal["Comment"] = str(input["Comment"])
            newanimal["Birthday"] = str(input["Birthday"])
            newanimal["ClientID"] = person["_id"]
            newanimal["DelTime"] = None
            mongo.db["Animals"].save(newanimal)
            return "Животное успешно добавлено."
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@mutation.field("add_message")#!добавление сообщения
def add_message(_, info, input):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('add_message')
        token = request.headers["Token"]
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            newmessage = {}
            chat = mongo.db["Chats"].find_one({"ClientID":person["_id"]})
            newmessage["_id"] = (get_max_id("ChatMessages")) + 1
            newmessage["ChatID"] = chat["_id"]
            newmessage["Time"] = datetime.datetime.now()
            newmessage["Text"] = str(input['Text'])
            newmessage["FilePath"] = str(input['FilePath'])
            newmessage["DelTime"] = None
            newmessage["Unread"] = 1 #непрочитано
            mongo.db["ChatMessages"].save(newmessage)
            return "Сообщение успешно отправлено!"
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("read_reviews")#просмотр отзывов
def read_reviews(_, info):
    add_operation_in_journal('read_reviews')
    answer = mongo.db["Reviews"].find()
    return answer

@query.field("read_animals")#просмотр списка животных
def read_animals(_, info):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('read_animals')
        token = request.headers['Token']
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            answer = mongo.db["Animals"].find({"ClientID":person["_id"]})
            return answer
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")


@query.field("read_journals")#чтение журнала
def read_journals(_, info):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('read_journals')
        token = request.headers["Token"]
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            answer = []
            for x in mongo.db["Orders"].find({"ClientID":person["_id"]}):
                for y in mongo.db["Journals"].find({"OrderID":x["_id"]}):
                    print(y)
                    answer.append(y)
            return answer
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("read_journals_by_animalid")#!чтение журнала по id животного
def read_journals_by_animalid(_, info, animalid):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('read_journals_by_animalid')
        token = request.headers["Token"]
        animalid = int(animalid)
        if check_token(token):
            answer = []
            if mongo.db["Orders"].find_one({"AnimalID":animalid})!= None:
                for order in mongo.db["Orders"].find({"AnimalID":animalid}):
                    for journal in mongo.db["Journals"].find({"OrderID":order["_id"]}):
                        print(journal)
                        answer.append(journal)
                return answer
            else:
                raise Exception('Ошибка, бронирование данного животного не найдено.')
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("read_orders")#!просмотр заказов
def read_orders(_, info, datestart, dateend):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('read_orders')
        token = request.headers['Token']
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            if (datestart != "") & (dateend != ""):
                date1 = datestart.split('-')
                date2 = dateend.split('-')
                from_date = datetime.datetime(int(date1[0]), int(date1[1]), int(date1[2]))
                to_date = datetime.datetime(int(date2[0]), int(date2[1]), int(date2[2]))
                answer = mongo.db["Orders"].find({"DateStart": {"$gte": from_date, "$lt": to_date}, "DateEnd": {"$gte": from_date, "$lt": to_date}, "ClientID":person["_id"]})
            else:
                answer = mongo.db["Orders"].find({"ClientID":person["_id"]})
            return answer
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("read_animals_in_hotel")#просмотр животных в отеле
def read_animals_in_hotel(_, info):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('read_animals_in_hotel')
        token = request.headers["Token"]
        if check_token(token):
            person = mongo.db["Persons"].find_one({"Token":token})
            answer = []
            for z in mongo.db["Orders"].find({"ClientID" : person["_id"], "DateStart": {"$lt": datetime.datetime.now()}, "DateEnd": {"$gte": datetime.datetime.now()}}):
                for y in mongo.db["Animals"].find({"_id" : z["AnimalID"]}):
                    answer.append(y)
                    print(y)
            return answer
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("read_messages")#!просмотр сообщений
def read_messages(_, info, unread, datestart, dateend):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('read_messages')
        unread = int(unread)
        token = str(request.headers["Token"])
        if check_token(token):
            answer = []
            person = mongo.db["Persons"].find_one({"Token":token})
            messages = mongo.db["ChatMessages"]
            chat = mongo.db["Chats"].find_one({"ClientID":person["_id"]})
            if (unread == 1 and datestart == "" and dateend == ""):#непрочитанные смс и нет дат для сортировки
                answer = []
                for msg in messages.find({"ChatID":chat["_id"] , "Unread":1}):
                    print (msg)
                    answer.append(msg)
                    mongo.db["ChatMessages"].update({"Unread" : 1},{"$set": {"Unread" : 0}})
                return answer
            elif (unread == 1 and datestart != "" and dateend != ""):#непрочитанные смс и есть дата для сортировки
                answer = []
                date1 = datestart.split('-')
                date2 = dateend.split('-')
                from_date = datetime.datetime(int(date1[0]), int(date1[1]), int(date1[2]), int(date1[3]), int(date1[4]))
                to_date = datetime.datetime(int(date2[0]), int(date2[1]), int(date2[2]), int(date2[3]), int(date2[4]))
                for msg in messages.find({"Time": {"$gte": from_date, "$lt": to_date}, "ChatID":chat["_id"], "Unread": 1}):
                    print (msg)
                    answer.append(msg)
                    messages.update( {"Time": {"$gte": from_date, "$lt": to_date}, "ChatID":chat["_id"],"Unread" : 1} , { "$set": { "Unread" : 0} })
                return answer
            elif (unread == 0 and datestart != "" and dateend != ""):#все смс и есть дата для сортировки
                answer = []
                date1 = datestart.split('-')
                date2 = dateend.split('-')
                from_date = datetime.datetime(int(date1[0]), int(date1[1]), int(date1[2]), int(date1[3]), int(date1[4]))
                to_date = datetime.datetime(int(date2[0]), int(date2[1]), int(date2[2]), int(date2[3]), int(date2[4]))
                for msg in messages.find({"Time": {"$gte": from_date, "$lt": to_date}, "ChatID":chat["_id"]}):
                    print(msg)
                    answer.append(msg)
                return answer
            else:#все смс и нет даты для сортировки
                answer = []
                for msg in messages.find({"ChatID":chat["_id"]}):
                    print(msg)
                    answer.append(msg)
                return answer
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("look_account")#просмотр аккаунта
def look_account(_, info):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('look_account')
        token = request.headers['Token']
        if check_token(token):
            answer = []
            for x in mongo.db["Persons"].find({"Token":token}):
                print(x)
                answer.append(x)
            return answer
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("look_workers")
def look_workers(_, info):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('look_workers')
        token = request.headers['Token']
        if check_token(token):
            answer = []
            for x in mongo.db["Persons"].find({"State": 0}):
                print(x)
                answer.append(x)
            return answer
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")

@query.field("look_worker_by_id")#!просмотр аккаунта работника
def look_worker_by_id(_, info, workerid):
    if ("Token" in request.headers.keys()):
        add_operation_in_journal('look_worker_by_id')
        token = request.headers['Token']
        if check_token(token):
            answer = []
            if mongo.db["Persons"].find_one({"_id": int(workerid), "State": 0})!= None:
                for person in mongo.db["Persons"].find({"_id": int(workerid), "State": 0}):
                    answer.append(person)
                    print(person)
                return answer
            else:
                raise Exception('Ошибка, работник не найден.')
        else:
            raise Exception("Ошибка доступа.")
    else:
        raise Exception("Ошибка получения данных.")
@mutation.field("changepass")#смена пароля
def changepass(_, info, input):
    add_operation_in_journal('changepass')
    token = request.headers['Token']
    if check_token(token):
        password = str(input['Password'])
        person = mongo.db["Persons"].find_one({"Token":token})
        person["Password"] = password
        mongo.db["Persons"].save(person)
        print("Попытка смены пароля прошла успешно ")
        return "Ваш пароль был успешно изменён"
    else:
        print("Ошибка доступа")

@mutation.field("logout")
def logout(_, info, token):
    if check_token(token):
        add_operation_in_journal('logout')
        person = mongo.db["Persons"].find_one({"Token":token})
        person["Token"] = None
        person["DateOfIssueToken"] = None
        mongo.db["Persons"].save(person)
        return "Выход был произведен успешно!"
    else:
        print("Ошибка доступа")
        return("Ошибка доступа")
def get_max_id(collection):
    col = mongo.db[collection]
    maxid = 0
    for x in col.find().sort("_id"):
        maxid = x["_id"]
    return maxid
def find_by_id(id, collection):
    col = mongo.db[collection]
    obj = {}
    for x in col.find():
        if x["_id"] == id:
            obj = x
    return obj

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()
# Create executable GraphQL schema
schema = make_executable_schema(type_defs, [query, mutation, person, order, journal, review, animal, animaltype, message, chat])#, user, order1, journal1
@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code

class FileMutex:
    def __init__(self):
        self.mutexname = "chillFA_filemutex"

        self.mutex = win32event.CreateMutex(None, 1, self.mutexname)
        self.lasterror = win32api.GetLastError()
    
    def release(self):
        return win32event.ReleaseMutex(self.mutex)

mutex = FileMutex()
mutex.release()

def add_operation_in_journal(opeartion):
    import time
    mutex = FileMutex()
    date=datetime.datetime.now()
    date = str(date)
    row = str(opeartion) + "=====" + str(date) + '\n'
    while True:
        win32event.WaitForSingleObject(mutex.mutex, win32event.INFINITE )
        f = open('journalflask.txt', 'a')
        f.write(row)
        f.close()
        mutex.release()
        return

class singleinstance:
    """ Limits application to single instance """

    def __init__(self):
        self.mutexname = "testmutex_{87c75f97-7a06-47c0-accf-0d139e50328d}" #GUID сгенерирован онлайн генератором
        self.mutex = win32event.CreateMutex(None, False, self.mutexname)
        self.lasterror = win32api.GetLastError()
    
    def aleradyrunning(self):
        return (self.lasterror == ERROR_ALREADY_EXISTS)
        
    def __del__(self):
        if self.mutex:
            win32api.CloseHandle(self.mutex)


from sys import exit
myapp = singleinstance()


if myapp.aleradyrunning():
    print("Another instance of this program is already running")
    exit(0)


if __name__ == '__main__':
    app.run()