import logging
import messages
import commands
import keyboards
import mongo
import constants

from config import BOT_TOKEN
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher
jobq = updater.job_queue

waiting_flags = {}


def start(bot, update):
    user_id = update.message.chat.id
    mongo.add_user(user_id)
    bot.send_message(chat_id=user_id, text=messages.START, reply_markup=keyboards.START)


def callbacks(bot, update):
    callback_data = update.callback_query.data
    user_id = update.callback_query.message.chat.id
    msg_id = update.callback_query.message.message_id

    if callback_data == constants.SETTINGS_CB:
        waiting_flags[user_id] = {constants.WAITING_FOR_TIME: True}
        bot.edit_message_text(chat_id=user_id, text=messages.SET_TIME, message_id=msg_id)
    return


def messages_handler(bot, update):
    user_id = update.message.chat.id
    msg_id = update.message.message_id
    user_flags = waiting_flags.get(user_id)

    if user_flags is None:
        # TODO: handle this case
        return

    # handle case where user wants to change schedule
    if user_flags.get(constants.WAITING_FOR_TIME) is not None and user_flags.get(constants.WAITING_FOR_TIME):
        message_text = update.message.text
        time = message_text.split(':')

        if not check_time_format(time):
            bot.send_message(chat_id=user_id, text=messages.WRONG_TIME)
            return

        mongo.set_time(user_id, message_text)
        waiting_flags[user_id][constants.WAITING_FOR_TIME] = False
        bot.send_message(chat_id=user_id, text=messages.ADDED_TIME(message_text))


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


if __name__ == '__main__':
    dispatcher.add_handler(CommandHandler(commands.START, start))
    dispatcher.add_handler(CallbackQueryHandler(callbacks))
    dispatcher.add_handler(MessageHandler(Filters.text, messages_handler))

    updater.start_polling()
