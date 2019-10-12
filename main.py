import logging
import messages
import commands
import keyboards
import mongo
import constants
import datetime
import redis_key
import ujson
import pytz

from config import BOT_TOKEN
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackQueryHandler
from babel.dates import format_datetime
from telegram import ParseMode
from db import get_redis_connection

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

r = get_redis_connection()

waiting_flags = {}

# TODO: change time
# TODO: save date to mongo according to bot's timestmap instead of .now()


def start(bot, update):
    user_id = update.message.chat.id
    mongo.add_user(user_id)
    bot.send_message(chat_id=user_id, text=messages.START, reply_markup=keyboards.START)


def callbacks(bot, update):
    callback_data = update.callback_query.data
    user_id = update.callback_query.message.chat.id
    msg_id = update.callback_query.message.message_id

    if callback_data == constants.SETTINGS_CB:
        r.set(redis_key.WAITING_FOR_TIME + str(user_id), 1)
        bot.edit_message_text(chat_id=user_id, text=messages.SET_TIME, message_id=msg_id)
        return

    elif callback_data == constants.YES_HURT_CB:
        bot.edit_message_text(chat_id=user_id, text=messages.YES_HURT, message_id=msg_id, reply_markup=keyboards.RATE_YOUR_PAIN)
    elif callback_data == constants.NO_HURT_CB:
        bot.edit_message_text(chat_id=user_id, text=messages.NO_HURT, message_id=msg_id)
        mongo.update_data(user_id, answer=constants.NO_HURT_CB, timestamp=get_timestamp(user_id))
        return

    elif callback_data.startswith(constants.HURT_RATE):
        hurt_rate = callback_data.replace(constants.HURT_RATE, '')
        r.set(redis_key.HURT_RATE + str(user_id), hurt_rate)
        bot.edit_message_text(chat_id=user_id, text=messages.PILLS, message_id=msg_id, reply_markup=keyboards.PILLS_QUESTION)

    elif callback_data in (constants.YES_PILLS_CB, constants.NO_PILLS_CB):
        r.set(redis_key.PILLS + str(user_id), callback_data)
        bot.edit_message_text(chat_id=user_id, text=messages.COMMENT, message_id=msg_id, reply_markup=keyboards.COMMENT_QUESTION)

    elif callback_data == constants.NO_COMMENT:
        mongo.update_data(user_id, constants.YES_HURT_CB, hurt_rate=r.get(redis_key.HURT_RATE + str(user_id)),
                          pills=callback_data, timestamp=get_timestamp(user_id))
        r.delete(redis_key.HURT_RATE + str(user_id))
        bot.edit_message_text(chat_id=user_id, text=messages.THANKS_MESSAGE, message_id=msg_id)

    elif callback_data == constants.YES_COMMENT:
        r.set(redis_key.WAITING_FOR_COMMENT + str(user_id), 1)
        bot.edit_message_text(chat_id=user_id, text=messages.YES_COMMENT, message_id=msg_id)

    elif callback_data.startswith(constants.HISTORY):
        results = mongo.get_statistic(user_id, callback_data)
        if results is not None:
            results = list(results)
            r.set(redis_key.HISTORY_REQUEST + str(user_id), ujson.dumps(results))
            pretty_history_msg = pretty_history(results, callback_data)
            bot.edit_message_text(chat_id=user_id, text=pretty_history_msg, message_id=msg_id, reply_markup=keyboards.HISTORY_KEYBOARD, parse_mode=ParseMode.MARKDOWN)
    elif callback_data.startswith(constants.DETAILED_HISTORY):
        if callback_data == constants.DETAILED_HISTORY_PAINFREE_CB:
            filter_res = constants.NO_HURT_CB
        else:
            filter_res = constants.YES_HURT_CB

        results = r.get(redis_key.HISTORY_REQUEST + str(user_id))
        if results is None:
            bot.send_message(user_id, "Ошибка при попытке получить информацию из базы данных.")
        results = ujson.loads(results)
        msg_text = pretty_detailed_history(results, filter_res)
        bot.send_message(user_id, msg_text, parse_mode=ParseMode.MARKDOWN)

    return


def pretty_detailed_history(results, filter_res):
    reply_text = "*Детальная статистика.*\n"

    for res in results:
        history_data = res[mongo.HEADACHE_HISTORY]
        did_hurt = history_data[mongo.DID_HURT]
        res_date = datetime.datetime.fromtimestamp(history_data[mongo.TIME])
        pretty_date = format_datetime(res_date, "dd MMMM YYYY", locale="ru_RU")

        if filter_res == did_hurt:
            pills = history_data[mongo.ATE_PILLS]
            if pills == constants.YES_PILLS_CB:
                pills_text = "да"
            else:
                pills_text = "нет"
            reply_text += "[{}]: баллы: {}, таблетки: {}, комментарий: {}\n".\
                format(pretty_date, history_data[mongo.HURT_RATE], pills_text, history_data[mongo.COMMENT])

    return reply_text


def get_timestamp(user_id):
    timestamp = r.get(redis_key.LAST_DAY_TIMESTAMP + str(user_id))
    if timestamp is not None:
        timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        return timestamp
    else:
        return datetime.datetime.now()


def messages_handler(bot, update):
    user_id = update.message.chat.id
    msg_id = update.message.message_id
    # handle case when user wants to change schedule
    if r.get(redis_key.WAITING_FOR_TIME + str(user_id)) is not None:
        message_text = update.message.text
        time = message_text.split(':')

        if not check_time_format(time):
            bot.send_message(chat_id=user_id, text=messages.WRONG_TIME)
            return

        mongo.set_time(user_id, message_text)
        r.delete(redis_key.WAITING_FOR_TIME + str(user_id))
        bot.send_message(chat_id=user_id, text=messages.ADDED_TIME(message_text))
        job_queue.run_daily(ask_condition, datetime.time(hour=int(time[0]), minute=int(time[1])), context=user_id, name=constants.CB_NAME)

    # when user wants to leave a note
    if r.get(redis_key.WAITING_FOR_COMMENT + str(user_id)):
        message_text = update.message.text
        mongo.update_data(user_id, constants.YES_HURT_CB, hurt_rate=r.get(redis_key.HURT_RATE + str(user_id)),
                          pills=r.get(redis_key.PILLS + str(user_id)), comment=message_text, timestamp=get_timestamp(user_id))
        bot.send_message(chat_id=user_id, text=messages.THANKS_MESSAGE)
        r.delete(redis_key.WAITING_FOR_COMMENT + str(user_id))
        r.delete(redis_key.PILLS + str(user_id))
        r.delete(redis_key.HURT_RATE + str(user_id))


def ask_condition(bot, job):
    r.set(redis_key.LAST_DAY_TIMESTAMP + str(job.context), str(datetime.datetime.now()))
    bot.send_message(chat_id=job.context, text=messages.WAS_IT_HURT, reply_markup=keyboards.MAIN_QUESTION)
    return


def check_time_format(time):
    if len(time) != 2:
        return False
    try:
        hours = int(time[0])
        minutes = int(time[1])
    except ValueError:
        return False

    if not 0 <= hours <= 24:
        return False

    if not 0 <= minutes <= 59:
        return False

    return True


def restart_jobs():
    users = mongo.get_all_users()
    for user in users:
        time = user.get(mongo.TIME)
        if time is not None:
            job_queue.run_daily(ask_condition, datetime.time(hour=int(time.split(':')[0]),
                                                             minute=int(time.split(':')[1])),
                                context=user[mongo.USER_ID], name=constants.CB_NAME)
    return


def show_statistic(bot, update):
    user_id = update.message.chat.id
    bot.send_message(chat_id=user_id, text=messages.STATISTIC, reply_markup=keyboards.STATISTIC)
    return


def settings(bot, update):
    user_id = update.message.chat.id
    bot.send_message(chat_id=user_id, text=messages.SETTINGS, reply_markup=keyboards.STATISTIC)
    return


def pretty_history(history, period):
    painful_days = 0
    painfree_days = 0
    if period == constants.ALL_TIME_CB:
        start_date = history[0][mongo.HEADACHE_HISTORY][mongo.TIME]
        end_date = history[len(history) - 1][mongo.HEADACHE_HISTORY][mongo.TIME]
    elif period == constants.THIS_MONTH_CB:
        start_date = datetime.datetime.today().replace(day=1)
        end_date = datetime.datetime.today()
    elif period == constants.LAST_MONTH_CB:
        end_date = (datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1))
        start_date = end_date.replace(day=1)
    else:
        return "Ошибка, что-то сломалось в pretty_history()"

    start_date_pretty = format_datetime(start_date, "dd MMMM YYYY", locale="ru_RU")
    end_date_pretty = format_datetime(end_date, "dd MMMM YYYY", locale="ru_RU")
    amount_of_days = (end_date - start_date).days
    missed_days = amount_of_days - len(history) + 1

    for res in history:
        did_hurt = res[mongo.HEADACHE_HISTORY][mongo.DID_HURT]
        if did_hurt == constants.YES_HURT_CB:
            painful_days += 1
        else:
            painfree_days += 1
    msg_text = "Статистика за выбранный период [{} – {}].\n" \
               "Дней за отчетный период: *{}*\n" \
               "Голова болела: *{}*.\n" \
               "Голова не болела: *{}*.\n" \
               "Выставлено оценок: *{}*.\n" \
               "Пропущено дней: *{}*.\n".format(start_date_pretty, end_date_pretty, amount_of_days, painful_days, painfree_days, len(history), missed_days)
    return msg_text


if __name__ == '__main__':
    restart_jobs()
    dispatcher.add_handler(CommandHandler(commands.START, start))
    dispatcher.add_handler(CallbackQueryHandler(callbacks))
    dispatcher.add_handler(MessageHandler(Filters.text, messages_handler))
    dispatcher.add_handler(CommandHandler(commands.HISTORY, show_statistic))

    updater.start_polling()
