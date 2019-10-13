import datetime
import constants

from pymongo import MongoClient
from config import MONGO_LOGIN, MONGO_PASSWORD

uri = "mongodb://{}:{}@127.0.0.1/headachehelper?authSource=test".format(MONGO_LOGIN, MONGO_PASSWORD)
# client = MongoClient(host="127.0.0.1",
#                      port=27017,
#                      username=MONGO_LOGIN,
#                      password=MONGO_PASSWORD,
#                      authSource="headachehelper")
client = MongoClient(uri)
db = client['headachehelper']
users = db.users

SET = '$set'
PUSH = '$push'

USER_ID = 'user_id'
TIME = 'time'
HURT_RATE = 'hurt_rate'
ATE_PILLS = 'ate_pills'
CREATED_AT = 'createdAt'
HEADACHE_HISTORY = 'headache_history'
DID_HURT = 'did_hurt'
COMMENT = 'note'


def add_user(user_id):
    users.update_one({
        USER_ID: user_id,
    }, {
        "$setOnInsert": {
            USER_ID: user_id,
            CREATED_AT: datetime.datetime.now(),
            HEADACHE_HISTORY: [],
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


def update_data(user_id, answer, timestamp, hurt_rate=None, pills=None, comment=None):
    if answer == constants.NO_HURT_CB:
        users.update_one({
            USER_ID: user_id,
        }, {
            PUSH: {
                HEADACHE_HISTORY: {
                    DID_HURT: answer,
                    TIME: timestamp,
                }
            }
        })

    elif answer == constants.YES_HURT_CB:
        users.update_one({
            USER_ID: user_id,
        }, {
            PUSH: {
                HEADACHE_HISTORY: {
                    DID_HURT: answer,
                    TIME: timestamp,
                    HURT_RATE: hurt_rate,
                    ATE_PILLS: pills,
                    COMMENT: comment,
                }
            }
        })


def get_all_users():
    return users.find({}, {USER_ID: 1, TIME: 1})


def get_statistic(user_id, period=None):
    if period is None:
        return None

    last_month_end = (datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1))
    last_month_start = last_month_end.replace(day=1)
    this_month_start = datetime.datetime.today().replace(day=1)
    if period == constants.LAST_MONTH_CB:
        condition = {'headache_history.time': {'$gte': last_month_start, '$lte': last_month_end}}
    elif period == constants.THIS_MONTH_CB:
        condition = {'headache_history.time': {'$gte': this_month_start}}
    else:
        condition = {}
    return users.aggregate([
        {'$match': {USER_ID: user_id}},
        {'$unwind': '$' + HEADACHE_HISTORY},
        {'$project': {HEADACHE_HISTORY: 1, '_id': 0}},
        {'$match': condition}
    ])


def get_time(user_id):
    q = users.find_one({USER_ID: user_id}, {TIME: 1})
    return q['time']
