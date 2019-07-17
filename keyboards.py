import constants
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# keyboard buttons
SETTINGS = InlineKeyboardButton(constants.SETTINGS_TEXT, callback_data=constants.SETTINGS_CB)
YES_HURT = InlineKeyboardButton(constants.YES_HURT_TEXT, callback_data=constants.YES_HURT_CB)
NO_HURT = InlineKeyboardButton(constants.NO_HURT_TEXT, callback_data=constants.NO_HURT_CB)
YES_PILLS = InlineKeyboardButton(constants.YES_PILLS_TEXT, callback_data=constants.YES_PILLS_CB)
NO_PILLS = InlineKeyboardButton(constants.NO_PILLS_TEXT, callback_data=constants.NO_PILLS_CB)


# keyboards
RATE_YOUR_PAIN = InlineKeyboardMarkup(
    [[InlineKeyboardButton(str(btn+row), callback_data=constants.HURT_RATE + str(btn+row)) for btn in range(3)] for row in range(0, 9, 3)])
MAIN_QUESTION = InlineKeyboardMarkup([[YES_HURT, NO_HURT]])
PILLS_QUESTION = InlineKeyboardMarkup([[YES_PILLS, NO_PILLS]])
START = InlineKeyboardMarkup([[SETTINGS]])
