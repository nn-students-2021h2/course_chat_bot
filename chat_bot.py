#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import logging

import requests
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

from data_parser import DataParser
from dynamics import DiseaseDynamics
from setup import PROXY, TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOG_ACTIONS = []
URL = 'https://cat-fact.herokuapp.com/facts'
CoronaStatsData = DataParser()
CoronaStatsDynamics = DiseaseDynamics()


def log_action(function):
    def inner(*args, **kwargs):
        update = args[0]
        if update and hasattr(update, 'message') and hasattr(update, 'effective_user'):
            LOG_ACTIONS.append({
                'user': update.effective_user.first_name,
                'function': function.__name__,
                'message': update.message.text,
            })
        return function(*args, **kwargs)

    return inner


def write_history(update: Update, filename='user_history.txt', count=5):
    index = 0
    reply_text = ''
    with open(filename, 'w', encoding='utf-8') as file_handler:
        for action in LOG_ACTIONS[::-1]:
            if index >= count:
                break
            if update.effective_user.first_name == action['user']:
                index += 1
                msg = (f'{index} User: {action["user"]} '
                       f'Message: {action["message"]}\n')
                reply_text += msg
                file_handler.write(msg)
    return filename, reply_text


def get_data_from_site(url: str) -> dict:
    try:
        req = requests.get(url)
        if req.ok:
            return req.json()
    except Exception as err:
        print(f'Error occurred: {err}')


def get_most_upvoted_fact(url=URL) -> str:
    data = get_data_from_site(url)
    if data is None:
        return '[ERR] Could not retrieve most upvoted fact'
    most_upvoted = None
    max_upvotes = 0
    for item in data['all']:
        if item['upvotes'] > max_upvotes:
            max_upvotes = item['upvotes']
            most_upvoted = item

    if most_upvoted is None:
        return '[ERR] Could not retrieve most upvoted fact'
    return most_upvoted['text']


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


@log_action
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')


@log_action
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Supported commands: \n /start \n /help \n /history \n /fact \n /corona_stats \n /corona_stats_progress')


@log_action
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


@log_action
def history(update: Update, context: CallbackContext):
    """Log the last 5 user's actions to the file."""
    count = 5
    filename, reply_msg = write_history(update, count=count)
    update.message.reply_text(reply_msg)


@log_action
def cat_fact(update: Update, context: CallbackContext):
    """Get fact about cats"""
    fact = get_most_upvoted_fact()
    update.message.reply_text(f'The most upvoted fact about cats: {fact}')


@log_action
def corona_stats(update: Update, context: CallbackContext):
    """Get coronovirus statistics"""
    reply_text = CoronaStatsData.get_most_diseased()
    update.message.reply_text(f'Top 5 provinces by sick people:\n{reply_text}')


@log_action
def corona_stats_dynamics(update: Update, context: CallbackContext):
    """Get coronovirus statistics"""
    reply_text = CoronaStatsDynamics.get_top_five()
    update.message.reply_text(f'Top 5 provinces by sick people:\n{reply_text}')


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    # Connect via https proxy
    # bot = Bot(
    #     token=TOKEN,
    #     base_url=PROXY,  # delete it if connection via VPN
    # )
    # updater = Updater(bot=bot, use_context=True)

    # Connect via socks proxy
    REQUEST_KWARGS = {
        'proxy_url': PROXY,
        # Optional, if you need authentication:
        # 'urllib3_proxy_kwargs': {
        #     'username': 'name',
        #     'password': 'passwd',
        # }
    }

    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('fact', cat_fact))
    updater.dispatcher.add_handler(CommandHandler('corona_stats', corona_stats))
    updater.dispatcher.add_handler(CommandHandler('corona_stats_progress', corona_stats_dynamics))

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
    main()
