import datetime
import constants

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.headachehelper
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


def update_data(user_id, answer, hurt_rate=None, pills=None, comment=None):
    if answer == constants.NO_HURT_CB:
        users.update_one({
            USER_ID: user_id,
        }, {
            PUSH: {
                HEADACHE_HISTORY: {
                    DID_HURT: answer,
                    TIME: datetime.datetime.now(),
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
                    TIME: datetime.datetime.now(),
                    HURT_RATE: hurt_rate,
                    ATE_PILLS: pills,
                    COMMENT: comment,
                }
            }
        })
