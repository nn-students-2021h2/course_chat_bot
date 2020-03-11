#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import json
from datetime import datetime
from timeit import default_timer as timer
import requests
from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def average_time(function):
    def inner(update: Update, context: CallbackContext):
        t = timer()
        res = function(update, CallbackContext)
        t = (timer() - t)
        update.message.reply_text(f'Время: {t} s!')
        return res
    return inner

# TODO: количество логов в истории
# TODO: вывод логов только одного юзера, а не всех
# TODO: вывод всех логов по ключу


def addlogging(function):
    def wrapper(*args, **kwargs):
        new_log = {
            "user": args[0].effective_user.first_name,
            "function": function.__name__,
            "message": args[0].message.text,
            "time": args[0].message.date.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        }
        with open("logs.json", "a") as write_file:
            write_file.write(json.dumps(new_log)+"\n")
        return function(*args, **kwargs)
    return wrapper


@average_time
@addlogging
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


@average_time
@addlogging
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи команду /start для начала. ')


@average_time
@addlogging
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


@average_time
@addlogging
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

@average_time
def history(update: Update, context: CallbackContext):
    """Send a message when the command /logs is issued."""
    with open("logs.json", "r") as read_file:
        data = read_file.readlines()
        if len(data) > 5:
            data = data[-1:-6:-1]
        for elems in data:
            log = json.loads(elems)
            response = ""
            for key, value in log.items():
                response = response + f'{key}: {value}\n'
            update.message.reply_text(response)


@average_time
def test(update: Update, context: CallbackContext):
    new_log = {
        "user": update.effective_user.first_name,
        "function": "anonym",
        "message": "test",
        "time": update.message.date.strftime( "%d-%b-%Y (%H:%M:%S.%f)" )
    }
    with open("logs.json", "a") as write_file:
        for _ in range(100000):
            write_file.write(json.dumps(new_log) + "\n")


def fact(update: Update, context: CallbackContext):
    max = 0
    upvoted_text = ''
    r = requests.get('https://cat-fact.herokuapp.com/facts')
    answer = json.loads(r.text)
    for i in answer['all']:
        if i['upvotes'] > max:
            max = i['upvotes']
            upvoted_text = i['text']
    update.message.reply_text(upvoted_text)


def main():
    bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('test', test))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    LOGS = []
    main()