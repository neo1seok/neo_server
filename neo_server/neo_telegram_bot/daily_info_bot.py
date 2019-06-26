
"""Simple Bot to reply to Telegram messages.
This program is dedicated to the public domain under the CC0 license.
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import threading

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# Enable logging
from neo_server.neo_telegram_bot.api_token import neo_bot_token, daily_info_token
from neo_server.parsing_class.show_daily_info import GetShowDailyInfo

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

logger.warning("start")
# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
	"""Send a message when the command /start is issued."""
	logger.info("start")
	update.message.reply_text('Hi!')

def mot(bot, update):
	"""Send a message when the command /start is issued."""
	logger.info("mot")
	list_html  = GetShowDailyInfo().run().get_html()
	logger.info(list_html)

	dict_proc = {
		"html":lambda content:update.message.reply_html(content),
		"text": lambda content: update.message.reply_text(content),
		"img": lambda content: update.message.reply_photo(content),
	}
	for content,type in list_html:
		logger.info(content)
		if content =="":
			continue
		dict_proc[type](content)


# print([tmp['name'] for tmp in map_list['실시간'] if tmp['day_niddght'] == '야간'])
	#
	# for key, val in map_list.items():
	# 	# print(key,val)
	# 	for tmp in val:
	# 		print(tmp)


def help(bot, update):
	"""Send a message when the command /help is issued."""
	logger.info("help")
	update.message.reply_text('Help!')
def check(bot, update):
	"""Send a message when the command /start is issued."""
	logger.info("check")
	logger.info("update %s",update)
	update.message.reply_html("<a href='www.google.com'>test </a>")
	print(dir(update.message))


def echo(bot, update):
	logger.info("echo %s",update.message.text)
	"""Echo the user message."""
	update.message.reply_text(update.message.text)


def error(bot, update, error):
	"""Log Errors caused by Updates."""
	#logger.info("error %s", update.message.text)
	logger.warning('Update "%s" caused error "%s"', update, error)

def start_chat():
	"""Start the bot."""
	# Create the EventHandler and pass it your bot's token.

	# https://api.telegram.org/535111053:AAHIL89_ZsQUjy43-a4JWmsvtGfuxLRKb-o/getMe
	updater = Updater(daily_info_token)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("mot", mot))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("check", check))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler(Filters.text, echo))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	return updater

def main():
	updater  = start_chat()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	print("test")
	main()