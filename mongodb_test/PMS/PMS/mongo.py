import time
from pymongo import MongoClient

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
        rs = self.prison.delete_one({"numering" : numbering})

        if rs > 0:
            return 100, True
        else:
            return 101, False

    def update_criminal(self, numbering, data):
        criminal = {"numbering" : numbering}
        if self.prison.find_one(criminal):
            self.prison.update_one({"number": numbering}, {'$inc' : data})
            return 100, True
        else:
            # do not have this criminal
            return 101, False

    def find_criminal(self, data=None, page=0):
        rs = self.prison.find(limit=20)
        datas = {}
        for r in rs:
            temp = {}
            temp['fristname'] = r['fristname']
            temp['lastname'] = r['lastname']
            temp['age'] = r['age']
            temp['gender'] = r['gender']
            temp['status'] = r['status']
            datas[r['numbering']] = temp
        return datas

    def get_info_by_numbering(self, numbering):
        return self.prison.find_one({'numbering': numbering})
  
