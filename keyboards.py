import constants
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# keyboard buttons
SETTINGS = InlineKeyboardButton(constants.SETTINGS_TEXT, callback_data=constants.SETTINGS_CB)
YES_HURT = InlineKeyboardButton(constants.YES_HURT_TEXT, callback_data=constants.YES_HURT_CB)
NO_HURT = InlineKeyboardButton(constants.NO_HURT_TEXT, callback_data=constants.NO_HURT_CB)
YES_PILLS = InlineKeyboardButton(constants.YES_PILLS_TEXT, callback_data=constants.YES_PILLS_CB)
NO_PILLS = InlineKeyboardButton(constants.NO_PILLS_TEXT, callback_data=constants.NO_PILLS_CB)
YES_COMMENT = InlineKeyboardButton(constants.YES_PILLS_TEXT, callback_data=constants.YES_COMMENT)
NO_COMMENT = InlineKeyboardButton(constants.NO_PILLS_TEXT, callback_data=constants.NO_COMMENT)
LAST_MONTH = InlineKeyboardButton(constants.LAST_MONTH_TEXT, callback_data=constants.LAST_MONTH_CB)
THIS_MONTH = InlineKeyboardButton(constants.THIS_MONTH_TEXT, callback_data=constants.THIS_MONTH_CB)
ALL_TIME = InlineKeyboardButton(constants.ALL_TIME_TEXT, callback_data=constants.ALL_TIME_CB)
PAINFREE = InlineKeyboardButton(constants.DETAILED_HISTORY_PAINFREE_TEXT, callback_data=constants.DETAILED_HISTORY_PAINFREE_CB)
PAINFUL = InlineKeyboardButton(constants.DETAILED_HISTORY_PAINFUL_TEXT, callback_data=constants.DETAILED_HISTORY_PAINFUL_CB)


# keyboards
RATE_YOUR_PAIN = InlineKeyboardMarkup(
    [[InlineKeyboardButton(str(btn+row), callback_data=constants.HURT_RATE + str(btn+row)) for btn in range(1, 4)] for row in range(0, 9, 3)])
MAIN_QUESTION = InlineKeyboardMarkup([[YES_HURT, NO_HURT]])
PILLS_QUESTION = InlineKeyboardMarkup([[YES_PILLS, NO_PILLS]])
COMMENT_QUESTION = InlineKeyboardMarkup([[YES_COMMENT, NO_COMMENT]])
START = InlineKeyboardMarkup([[SETTINGS]])
STATISTIC = InlineKeyboardMarkup([[LAST_MONTH, THIS_MONTH], [ALL_TIME]])
HISTORY_KEYBOARD = InlineKeyboardMarkup([[PAINFUL]])
