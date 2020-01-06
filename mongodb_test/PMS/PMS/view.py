from django.http import HttpResponse
import json
import time
from pymongo import MongoClient
import hashlib
import os

DEFAULT_TOKEN_TIME = 24 * 60 * 60 * 1000

class Mongo:
    def __init__(self):
        self.client = MongoClient(['mongodb://localhost:21000/', 'mongodb://localhost:31000/', 'mongodb://localhost:41000/'])
        pms = self.client.pms3
        utoken = self.client.utoken

        self.prison = pms.prison
        self.user_t = utoken.token
        self.info = utoken.info

    def verify_token(self, token, username):
        '''
        Authentication token, If there is no such token
        or the token times out, access is denied
        '''
        t = self.user_t.find_one({"token":token, "username":username})
        now_time = int(round(time.time() * 1000))
        if t is None or now_time - t['timestamp'] > DEFAULT_TOKEN_TIME:
            # verify failed
            return 101, False
        return 100, True

    def add_token(self, token, username, timestamp):
        # remove old token
        self.user_t.delete_one({"username" : username})
        # add new token
        user_token = {"token": token,
                "timestamp": timestamp,
                "userid": username,}
        self.user_t.insert_one(user_token)
        return 100, True

    def verify_user(self, username, password):
        userinfo = self.info.find_one({"username":username})
        print(userinfo)
        if userinfo is None or password != userinfo['password']:
            return 101, False
        else:
            return 100, True

    def add_criminal(self, numbering, fristname, lastname, age, gender, description, status):
        criminal = {"numbering" : numbering,
                    "fristname" : fristname,
                    "lastname" : lastname,
                    "age" : age,
                    "gender" : gender,
                    "description" : description,
                    "status" : status,
                    }
        self.prison.insert_one(criminal)
        return 100, True

    def remove_criminal(self, numbering):
        print(numbering)
        rs = self.prison.delete_one({"numbering" : numbering})
        print(rs.acknowledged)
        if rs.acknowledged:
            return 100, True
        else:
            return 101, False

    def update_criminal(self, numbering, fristname, lastname, age, gender, description, status):
        criminal = {"numbering" : numbering}
        if self.prison.find_one_and_update({"numbering": numbering}, {'$set': {'fristname':fristname, 'lastname':lastname, 'age':age, 'gender':gender, 'description':description,'status':status}}):
            return 100, True
        else:
            # do not have this criminal
            return 101, False

    def find_criminal(self, data=None, page=0):
        rs = self.prison.find(limit=20)
        datas = {}
        for r in rs:
            temp = {}
            temp['numbering'] = r['numbering']
            temp['fristname'] = r['fristname']
            temp['lastname'] = r['lastname']
            temp['age'] = r['age']
            temp['gender'] = r['gender']
            temp['status'] = r['status']
            datas[r['numbering']] = temp
        return datas

    def get_info_by_numbering(self, numbering):
        rs =  self.prison.find_one({'numbering': numbering})
        return rs

mongo = Mongo()

def gen_token():
    return hashlib.sha1(os.urandom(24)).hexdigest()

def registered(request):
    pass

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        _, flag = mongo.verify_user(username, password)
        if flag:
            # gen token
            token = gen_token()
            timestamp = int(round(time.time() * 1000))
            # add token to db
            # mongo.add_token(username, token, timestamp)
            rs = {'code':100, 'des':'success','token':token}
        else:
            rs = {'code':101, 'des':'Useless username or password!', 'token':''}
    else:
        rs = {'code':109, 'des':'Not accepting get requests', 'token':''}
    return HttpResponse(json.dumps(rs))

def regist(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        # regist user
        rs = {'code': 100, 'des': 'success'}
    else:
        rs = {'code':109, 'des':'Not accepting get requests'}
    return HttpResponse(json.dumps(rs))

def insert(request):
    if request.method == 'POST':
        numbering = request.POST.get('numbering', '')
        fristname = request.POST.get('fristname', '')
        lastname = request.POST.get('lastname', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        description = request.POST.get('description', '')
        status = request.POST.get('status', '')
        _, flag = mongo.add_criminal(numbering, fristname, lastname, age, gender, description, status)
        if flag is True:
            rs = {'code': 100, 'des': 'success'}
        else:
            rs = {'code': 101, 'des': 'fail'}
    else:
        rs = {'code':109, 'des':'Not accepting get requests'}
    return HttpResponse(json.dumps(rs))

def remove(request):
    if request.method == 'POST':
        print(request.body)
        print(request.POST)
        numbering = request.POST.get('numbering', '')
        numbering = request.POST.get('numbering', '')
        code, flag = mongo.remove_criminal(numbering)
        if flag is True:
            rs = {'code': code, 'des': 'success'}
        else:
            rs = {'code': code, 'des': 'fail'}
    else:
        rs = {'code':109, 'des':'Not accepting get requests'}
    return HttpResponse(json.dumps(rs))

def update(request):
    if request.method == 'POST':
        numbering = request.POST.get('numbering', '')
        fristname = request.POST.get('fristname', '')
        lastname = request.POST.get('lastname', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')
        description = request.POST.get('description', '')
        status = request.POST.get('status', '')
        data = {
            "fristname" : fristname,
            "lastname" : lastname,
            "age" : age,
            "gender" : gender,
            "description" : description,
            "status" : status,
        }
        code, flag = mongo.update_criminal(numbering, fristname, lastname, age, gender, description, status)
        if flag is True:
            rs = {'code': code, 'des': 'success'}
        else:
            rs = {'code': code, 'des': 'fail'}
    else:
        rs = {'code':109, 'des':'Not accepting get requests'}
    return HttpResponse(json.dumps(rs))

def show(request):
    if request.method == 'POST':
        data = mongo.find_criminal()
        rs =  {'code': 100, 'des': 'succes', 'data': data}
    else:
        rs = {'code':109, 'des':'Not accepting get requests', 'data':''}
    return HttpResponse(json.dumps(rs))

def detail(request):
    if request.method == 'POST':
        numbering = request.POST.get('numbering', '')
        data = mongo.get_info_by_numbering(numbering)
        if data:
            info = {}
            info['numbering'] = data['numbering']
            info['fristname'] = data['fristname']
            info['lastname'] = data['lastname']
            info['age'] = data['age']
            info['gender'] = data['gender']
            info['status'] = data['status']
            info['description'] = data['description']
            rs =  {'code': 100, 'des': 'succes', 'info':info}
        else:
            rs = {'code': 101, 'des': 'failed', 'info':{}}
    else:
        rs = {'code':109, 'des':'Not accepting get requests', 'info':''}
    return HttpResponse(json.dumps(rs))
