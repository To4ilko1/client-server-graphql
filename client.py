import random
import string
import json
import requests
from bson.json_util import dumps, loads
from bson import json_util
from datetime import datetime# реализовать всё для клиента добавление удаление заказов, просмотр услуг, скидок, заказов, чатов и тд
import re
from sys import exit
import sys
global URL

URL = 'http://127.0.0.1:5000/graphql'
token = ''

def print_messages(messages):
    print("="*20)
    for message in messages:
        time = str(message["Time"])[0:10] + " " + str(message["Time"])[11:19]
        if message["FilePath"] == "":
            print("Время: %s\nТекст: %s\nОтправитель: %s\n" %(time, message["Text"], message["Chat"]["Person"]["Name"]))
        else:
            print("Время: %s\nТекст: %s\nОтправитель: %s\nФото: %s\n" % (time, message["Text"], message["Chat"]["Person"]["Name"], message["FilePath"]))

def print_animals(animals):
    print("="*20)
    for animal in animals:
        if animal["Sex"] == 0:
            animalsex = "Мужской"
        else:
            animalsex = "Женский"
        print("ID животного: %s\nКличка: %s\nХозяин: %s\nТип животного: %s\nПол: %s\nКомментарий: %s\nДата рождения: %s\n" % (animal["_id"], animal["Name"], animal["Client"]["Name"], animal["AnimalType"]["NameIfType"], animalsex, animal["Comment"], animal["Birthday"]))
def print_animals_in_hotel(animals):
    print("="*20)
    for animal in animals:
        if animal["Sex"] == 0:
            animalsex = "Мужской"
        else:
            animalsex = "Женский"
        print("ID животного: %s\nКличка: %s\nХозяин: %s\nТип животного: %s\nПол: %s\nКомментарий: %s\nДата рождения: %s\n" % (animal["_id"], animal["Name"], animal["Client"]["Name"], animal["AnimalType"]["NameIfType"], animalsex, animal["Comment"], animal["Birthday"]))

def print_journals(journals):
    print("="*20)
    for journal in journals:
        date = str(journal["TimeStart"])[0:10]
        timestart = str(journal["TimeStart"])[11:19]
        timeend = str(journal["TimeEnd"])[11:19]
        if journal["Filepath"] != "":
            print("ID журнала: %s\nДата: %s\nВремя начала: %s\nВремя конца: %s\nID заказа: %s\nКличка животного: %s\nРаботник: %s\nПоручение: %s\nКомментарий: %s\nФото: %s\n" % (journal["_id"], date, timestart, timeend, journal["Order"]["_id"], journal["Order"]["Animal"]["Name"], journal["Worker"]["Name"], journal["Task"], journal["Comment"], journal["Filepath"]))
        else:
            print("ID журнала: %s\nДата: %s\nВремя начала: %s\nВремя конца: %s\nID заказа: %s\nID животного: %s\nРаботник: %s\nПоручение: %s\nКомментарий: %s\n" % (journal["_id"], date, timestart, timeend, journal["Order"]["_id"], journal["Order"]["Animal"]["Name"], journal["Worker"]["Name"], journal["Task"], journal["Comment"]))

def print_orders(orders):
    print("="*20)
    for order in orders:
        datestart = str(order["DateStart"])[0:10]
        dateend = str(order["DateEnd"])[0:10]
        if (int(order["DeliveryToTheHotel"]) == 1) & (int(order["DeliveryFromHotel"]) == 1):
            print("ID заказа: %s\nЦена: %s\nКличка животного: %s\nДата заезда: %s\nДата выезда: %s\nДоставка до отеля: %s\nДоставка из отеля: %s\nАдрес доставки до отеля: %s\nАдрес доставки из отеля: %s\nВремя доставки до отеля: %s\nВремя доставки из отеля: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["Animal"]["Name"], datestart, dateend, order["DeliveryToTheHotel"], order["DeliveryFromHotel"], order["FromDeliveryAddress"], order["ToDeliveryAddress"], order["FromDeliveryTime"], order["ToDeliveryTime"], order["Comment"], order["Status"]))
        if (int(order["DeliveryToTheHotel"]) == 0) & (int(order["DeliveryFromHotel"]) == 0):
            print("ID заказа: %s\nЦена: %s\nКличка животного: %s\nДата заезда: %s\nДата выезда: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["Animal"]["Name"], datestart, dateend, order["Comment"], order["Status"]))
        if (int(order["DeliveryToTheHotel"]) == 1) & (int(order["DeliveryFromHotel"]) == 0):
            print("ID заказа: %s\nЦена: %s\nКличка животного: %s\nДата заезда: %s\nДата выезда: %s\nДоставка до отеля: %s\nАдрес доставки до отеля: %s\nВремя доставки до отеля: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["Animal"]["Name"], datestart, dateend, order["DeliveryToTheHotel"], order["FromDeliveryAddress"], order["FromDeliveryTime"], order["Comment"], order["Status"]))
        if (int(order["DeliveryToTheHotel"]) == 0) & (int(order["DeliveryFromHotel"]) == 1):
            print("ID заказа: %s\nЦена: %s\nКличка животного: %s\nДата заезда: %s\nДата выезда: %s\nДоставка из отеля: %s\nАдрес доставки из отеля: %s\nВремя доставки из отеля: %s\nКомментарий: %s\nСтатус: %s\n" % (
                order["_id"], order["Price"], order["Animal"]["Name"], datestart, dateend,  order["DeliveryFromHotel"], order["ToDeliveryAddress"], order["ToDeliveryTime"], order["Comment"], order["Status"]))

def print_reviews(reviews):
    print("="*20)
    for review in reviews:
        time = str(review["AddTime"])[0:10] + " " + str(review["AddTime"])[11:19]
        # time = datetime.strptime(review["AddTime"],"%Y-%m-%d %I:%M")
        print("ID отзыва: %s\nТекст: %s\nТип животного: %s\nХозяин: %s\nВремя добавления: %s\n" % (review["_id"], review["Body"],  review["AnimalType"]["NameIfType"], review["Client"]["Name"], time))

def print_account(account):
    for acc in account:
        print("ID: %s\nФИО: %s\nАдрес: %s\nТелефон: %s\nE-mail: %s\nДата рождения: %s\n" %(acc["_id"], acc["Name"], acc["Address"], acc["Phone"], acc["Email"], acc["Birthday"]))
def start_client():  # Основная функция, запускающая клиента. Эта функция вызывается в конце файла, после определения всех нужных деталей

    token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16)) 
    isauth = 0
    print("Подключились к серверу")
    while True:
        print("Главное меню:")
        print("1 - Авторизоваться")
        print("2 - Зарегистрироваться")
        print("3 - Посмотреть отзывы")
        print("4 - Выйти из программмы")
        if isauth == 1:
            print("5 - Просмотреть список животных")
            print("6 - Добавить заказ")
            print("7 - Добавить животное")
            print("8 - Добавить отзыв")
            print("9 - Смотреть свой профиль")
            print("10 - Выйти из профиля")
            print("11 - Просмотреть журнал")
            print("12 - Смена пароля")
            print("13 - Посмотреть заказы")
            print("14 - Отправить сообщение в чат")
            print("15 - Смотреть чат")
            print("16 - Смотреть список животных в отеле")
            print("17 - Смотреть информацию о работнике")
        task = input()
        if not task.isdigit() or int(task) > 17:
            print("Неправильная команда!")
            continue
        task = int(task)
        if task == 1 and isauth == 0:#авторизация пользователя
            login = str(input("Введите логин:\n"))
            password = str(input("Введите пароль:\n"))
            headers = {'Content-type': 'application/json'}
            query = {
                'query': 'mutation{authorization(login:"'+ login +'",password:"'+ password +'"){ Token }}'
                }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            answer = json.loads(response.text)
            if answer['data']['authorization']['Token'] == None:
                print("Неправильный логин или пароль")
            else: 
                print("Вы авторизовались!")
                token = answer['data']['authorization']['Token']
                isauth = 1
        if task == 2:#регистрация пользователя
            login = str(input("Введите логин:\n"))
            password = str(input("Введите пароль:\n"))
            Name = str(input("Введите ФИО:\n"))
            Phone = str(input("Введите телефон:\n"))
            Email = str(input("Введите e-mail:\n"))
            Birthday = str(input("Введите дату рождения:\n"))
            Address = str(input("Введите адрес:\n"))
            headers = {'Content-type': 'application/json'}
            query = {
                'query': 'mutation{add_person(input:{Login:"'+login+'" Password:"'+password+'" Name:"'+Name+'" Phone:"'+Phone+'" Email:"'+Email+'" Birthday: "'+Birthday+'" Address:"'+Address+'"})}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            print("Вы успешно прошли регистрацию!")
        if task == 3:#просмотр отзывов
            headers = {'Content-type': 'application/json'}
            query = {
                'query': '{read_reviews{ _id Body AnimalType {NameIfType} Client{Name} AddTime}}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            answer = json.loads(response.text)
            try:
                reviews = answer['data']['read_reviews']
                print_reviews(reviews)
            except Exception:
                print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
        if task == 4:#выход из программы
            exit(0)
        if task == 5 and isauth == 1:#просмотр животных
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': '{read_animals{ _id Name AnimalType {NameIfType} Sex Comment Birthday Client {Name}}}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            answer = json.loads(response.text)
            try:
                animals = answer['data']['read_animals']
                print_animals(animals)
            except Exception:
                print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
                # e = sys.exc_info()[1]
                # print(e.args[0])
            # if answer['data']==None:
            #     print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
            # # answer = json.loads(response.text)
        if task == 6 and isauth == 1:#добавление заказа
            AnimalID = input("Введите ID животного:")
            orderdatestart = input("Введите дату заезда в отель в формате\nгггг-мм-дд: ")
            while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdatestart) == []:
                orderdatestart = input("Неправильный формат! Введите дату заезда в отель в формате\nгггг-мм-дд: ")
            orderdateend = input("Введите дату отъезда из отеля в формате\nгггг-мм-дд: ")
            while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdateend) == []:
                orderdateend = input("Неправильный формат! Введите дату заезда в отель в формате\nгггг-мм-дд: ")
            DeliveryToTheHotel = input("Вы согласны на доставку животного до отеля: 0-нет, 1-да ")
            if DeliveryToTheHotel == "1":
                FromDeliveryAddress = input("Введите адрес, откуда мы сможем забрать вашего питомца: ")
                FromDeliveryTime = input("Во сколько мы можем забрать вашего питомца: ")
            else:
                FromDeliveryAddress = ""
                FromDeliveryTime = ""
            DeliveryFromHotel = input("Вы согласны на доставку животного из отеля к вам: 0-нет, 1-да ")
            if DeliveryFromHotel == "1":
                ToDeliveryAddress = input("Введите адрес, куда мы можем привезти вашего питомца: ")
                ToDeliveryTime = input("Во сколько мы можем привезти вашего питомца: ")
            else:
                ToDeliveryAddress = ""
                ToDeliveryTime = ""
            Comment = input("Введите комментарий к заказу: ")
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': 'mutation{add_order(input:{AnimalID:'+AnimalID+' DeliveryToTheHotel:"'+DeliveryToTheHotel+'" FromDeliveryAddress:"'+FromDeliveryAddress+'" FromDeliveryTime:"'+FromDeliveryTime+'" DeliveryFromHotel:"'+DeliveryFromHotel+'" ToDeliveryAddress:"'+ToDeliveryAddress+'" ToDeliveryTime:"'+ToDeliveryTime+'" DateStart:"'+orderdatestart+'" DateEnd:"'+orderdateend+'" Comment:"'+Comment+'"})}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            # answer = json.loads(response.text)
            # print(response.text)
            print('Заказ добавлен!')
        if task == 7 and isauth == 1:#добавление животного
            AnimalTypeID = input("Введите тип животного: 1-кошка\n2-собака\n3-попугай\n")
            Name = input("Введите кличку животного:\n")
            Sex = input("Введите пол животного: 0-мужской, 1-женский\n")
            Comment = input("Введите комментарий:\n")
            Birthday = input("Введите дату рождения:\n")
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': 'mutation{add_animal(input:{Name:"'+Name+'" AnimalTypeID:'+AnimalTypeID+' Sex:'+Sex+' Comment:"'+Comment+'" Birthday:"'+Birthday+'"})}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            # answer = json.loads(response.text)
            print('Животное добавлено!')
            # print(response.text)
        if task == 8 and isauth == 1:#добавление отзыва
            AnimalTypeID = input("Введите тип животного: 1-кошка\n2-собака\n3-попугай\n")
            Body = input("Введите текст отзыва:\n")
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': 'mutation{add_review(input:{AnimalTypeID:'+AnimalTypeID+' Body:"'+Body+'"})}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            answer = json.loads(response.text)
            print('Отзыв добавлен!')
            # print(response.text)
            # answer = json.loads(response.text)
            # print('Отзыв добавлен!')
        if task == 9 and isauth == 1:#просмотр аккаунта
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': '{look_account{ _id Name Phone Email Birthday Address}}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            answer = json.loads(response.text)
            try:
                account = answer['data']['look_account']
                print_account(account)
            except Exception:
                print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
        if task == 10 and isauth == 1:#выход из профиля
            headers = {'Content-type': 'application/json'}
            query = {
                'query': 'mutation{logout(token:"'+token+'")}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            isauth = 0
            print("Выход из профиля совершён.")
        if task == 11 and isauth == 1:#просмотр журнала
            answer= []
            AnimalID = str(input("Введите ID животного: "))
            headers = {'Content-type': 'application/json','Token': token}
            if AnimalID !="":
                query = {
                    'query': '{read_journals_by_animalid(animalid:'+ AnimalID +'){ _id TimeStart TimeEnd Order {_id} Order {Animal{Name}} Worker {Name} Task Comment Filepath}}'
                }
                response = requests.post(URL, data=json.dumps(query), headers=headers)
                answer = json.loads(response.text)
                try:
                    journals = answer['data']['read_journals_by_animalid']
                    print_journals(journals)
                except Exception:
                    print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
            else:
                query = {
                    'query': '{read_journals{ _id TimeStart TimeEnd Order {_id} Order {Animal{Name}} Worker {Name} Task Comment Filepath}}'
                }
                response = requests.post(URL, data=json.dumps(query), headers=headers)
                answer = json.loads(response.text)
                try:
                    journals = answer['data']['read_journals']
                    print_journals(journals)
                except Exception:
                    print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
            
        if task == 12 and isauth == 1:#смена пароля
            password = input("Введите новый пароль:")
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': 'mutation{changepass(input:{Password:"'+ password +'"})}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            print("Вы успешно изменили пароль")
        if task == 13 and isauth == 1:#просмотр заказов
            orderdatestart = ""
            orderdateend = ""
            orderdatestart = str(input("Введите начальную дату для поиска в формате\nгггг-мм-дд: "))
            if orderdatestart !="":
                while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdatestart) == []:
                    orderdatestart = str(input("Неправильный формат! Введите начальную дату для поиска в формате\nгггг-мм-дд: "))
            orderdateend = str(input("Введите конечную дату для поиска в формате\nгггг-мм-дд: "))
            if orderdateend !="":
                while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', orderdateend) == []:
                    orderdateend = str(input("Неправильный формат! Введите конечную дату для поиска в формате\nгггг-мм-дд: "))
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': '{read_orders(datestart:"'+orderdatestart+'",dateend:"'+orderdateend+'"){ _id Status DateStart DateEnd Client {Name} Animal {Name} DeliveryToTheHotel FromDeliveryAddress FromDeliveryTime DeliveryFromHotel ToDeliveryAddress ToDeliveryTime Comment Price}}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            answer = json.loads(response.text)
            try:
                orders = answer['data']['read_orders']
                print_orders(orders)
            except Exception:
                print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
        if task == 14 and isauth == 1:#добавление сообщения
            FilePath = input("Введите путь до файла:")
            Text = input("Введите текст сообщения:")
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': 'mutation{add_message(input:{FilePath:"'+FilePath+'" Text:"'+Text+'"})}'
            }
            response = requests.post(URL, data=json.dumps(query), headers=headers)
            answer = json.loads(response.text)
            print('Сообщение отправлено!')
        if task == 15 and isauth == 1:#просмотр сообщений
            DateStart =""
            DateEnd=""
            unread = str(input("Показать непрочитанные сообщения? 0 - нет, 1 - да: "))
            sorting = str(input("Отсортировать сообщения по дате? 0 - нет, 1 - да: "))
            if sorting == 1:
                msgdatestart = str(input("Введите начальную дату для поиска в формате\nгггг-мм-дд-чч-мм : "))
                while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}', msgdatestart) == []:
                    msgdatestart = input(("Неправильный формат! Введите начальную дату для поиска в формате\nгггг-мм-дд: "))
                DateStart = msgdatestart
                msgdateend = str(input("Введите конечную дату для поиска в формате\nгггг-мм-дд-чч-мм: "))
                while re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}', msgdateend) == []:
                    msgdateend = input(("Неправильный формат! Введите конечную дату для поиска в формате\nгггг-мм-дд-чч-мм: "))
                DateEnd = msgdateend
            headers = {'Content-type': 'application/json', 'Token':token}
            query = {
                'query': '{read_messages(unread:'+unread+', datestart:"'+DateStart+'",dateend:"'+DateEnd+'"){ _id Chat {Person{Name}} Time Text FilePath}}'
            }
            response = requests.post(URL, headers=headers, data=json.dumps(query))
            answer = json.loads(response.text)
            try:
                messages = answer['data']['read_messages']
                print_messages(messages)
            except Exception:
                print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
        if task == 16 and isauth == 1:#просмотр списка животных в отеле
            headers = {'Content-type': 'application/json', 'Token': token}
            query = {
                'query': '{read_animals_in_hotel{ _id Name AnimalType {NameIfType} Sex Comment Birthday Client {Name}}}'
            }
            response = requests.post(URL, headers=headers, data=json.dumps(query))
            answer = json.loads(response.text)
            try:
                animals = answer['data']['read_animals_in_hotel']
                print_animals(animals)
            except Exception:
                print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
            # response = requests.get(url, headers={'Token':str(token)})
        if task == 17 and isauth == 1:#просмотр аккаунта работника
            WorkerID = str(input("Введите ID работника: "))
            headers = {'Content-type': 'application/json', 'Token':token}
            if WorkerID != "":
                query = {
                    'query': '{look_worker_by_id(workerid:'+WorkerID+'){ _id Name Phone Email Birthday Address}}'
                }
                response = requests.post(URL, headers=headers, data=json.dumps(query))
                answer = json.loads(response.text)
                try:
                    account = answer['data']['look_worker_by_id']
                    print_account(account)
                except Exception:
                    print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
            else:
                query = {
                    'query': '{look_workers{ _id Name Phone Email Birthday Address}}'
                }
                response = requests.post(URL, headers=headers, data=json.dumps(query))
                answer = json.loads(response.text)
                try:
                    account = answer['data']['look_workers']
                    print_account(account)
                except Exception:
                    print("Ошибка доступа. Пожалуйста, авторизуйтесь заново.")
            
start_client()  # Запускаем функцию старта клиента. Вызов функции должен быть ниже, чем определение этой функции в файле
