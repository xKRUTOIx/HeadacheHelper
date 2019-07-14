from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import constants

SETTINGS = InlineKeyboardButton(constants.SETTINGS_TEXT, callback_data=constants.SETTINGS_CB)

START = InlineKeyboardMarkup([[SETTINGS]])
