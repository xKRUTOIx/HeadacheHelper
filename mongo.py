import datetime
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.headachehelper
users = db.users

SET = '$set'

USER_ID = 'user_id'
TIME = 'time'
RATE = 'rate'
ATE_PILLOWS = 'ate_pillows'
CREATED_AT = 'createdAt'
HEADACHE_HISTORY = 'headache_history'


def add_user(user_id):
    users.update_one({
        USER_ID: user_id,
    }, {
        SET: {
            USER_ID: user_id
        }
    }, upsert=True)


def set_time(user_id, time=None):
    users.update_one({
        USER_ID: user_id,
    }, {
        SET: {
            TIME: time,
        }
    })
