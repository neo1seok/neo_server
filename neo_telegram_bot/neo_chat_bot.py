#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)

import logging

# Enable logging
from neo_telegram_bot.api_token import neo_bot_token
from parsing_class.show_portal_order import CheckNaverDaumOrder

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.DEBUG)

logger = logging.getLogger(__name__)

logger.debug("STRAT")
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['패스워드', '포탈검색순위'],
				   ['Done']]
keword_query_url = {
"네이년":	"https://search.naver.com/search.naver?where=nexearch&query={keyword}&ie=utf8&sm=tab_lve",
"다음":"https://search.daum.net/search?w=tot&DA=1TH&rtmaxcoll=1TH&q={keyword}"
}
logger.debug("keword_query_url %s",[list(keword_query_url.keys())])
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_keyword = ReplyKeyboardMarkup([list(keword_query_url.keys()),["DONE"]], one_time_keyboard=True)

def facts_to_str(user_data):
	facts = list()

	for key, value in user_data.items():
		facts.append('{} - {}'.format(key, value))

	return "\n".join(facts).join(['\n', '\n'])


def start(bot, update):
	logger.debug("start")
	update.message.reply_text(
		"네오셕의 개인 앱입니다. "
		"다음을 선택 하시겠습니까??",
		reply_markup=markup)

	return CHOOSING


def password(bot, update, user_data):
	logger.debug("password")
	text = update.message.text
	user_data['choice'] = text
	update.message.reply_text(
		'힌트어는 다음과 같습니다. {} 답변을 적으시오'.format('내생일'))

	return TYPING_REPLY

def check_hint(bot, update, user_data):
	logger.debug("check_hint")
	text = update.message.text
	user_data['choice'] = text
	update.message.reply_text(
		'검색어를 입력하시오 '.format('내생일'))

	return TYPING_REPLY


def password_result(bot, update, user_data):
	logger.debug("password_result")
	text = update.message.text
	user_data['choice'] = text
	update.message.reply_text(
		'검색어를 입력하시오 '.format('내생일'))

	return TYPING_REPLY



def custom_choice(bot, update):
	update.message.reply_text('Alright, please send me the category first, '
							  'for example "Most impressive skill"')

	return TYPING_CHOICE


def received_information(bot, update, user_data):
	logger.debug("received_information")
	text = update.message.text
	category = user_data['choice']
	user_data[category] = text
	del user_data['choice']

	update.message.reply_text("Neat! Just so you know, this is what you already told me:"
							  "{}"
							  "You can tell me more, or change your opinion on something.".format(
								  facts_to_str(user_data)), reply_markup=markup)

	return CHOOSING


def done(bot, update, user_data):
	if 'choice' in user_data:
		del user_data['choice']

	update.message.reply_text("I learned these facts about you:"
							  "{}"
							  "Until next time!".format(facts_to_str(user_data)))

	user_data.clear()
	return ConversationHandler.END

def keyword(bot, update):
	logger.debug("received_information")

	#user_data["list_keyword"] = CheckNaverDaumOrder().run().result()
	# result = CheckNaverDaumOrder().run().result()
	#
	# for portal, list_keyword in result:
	# 	print(portal)
	# 	for keyword in list_keyword:
	# 		update.message.reply_text("{}".format(keyword))

	update.message.reply_text(
		"네오셕의 개인 앱입니다. "
		"다음을 선택 하시겠습니까??",
		reply_markup=markup_keyword)

	return CHOOSING

def keyword_replay(bot, update,user_data):
	logger.debug("received_information")

	#user_data["list_keyword"] = CheckNaverDaumOrder().run().result()
	# result = CheckNaverDaumOrder().run().result()
	#
	# for portal, list_keyword in result:
	# 	print(portal)
	# 	for keyword in list_keyword:
	# 		update.message.reply_text("{}".format(keyword))

	update.message.reply_text(
		"네오셕의 개인 앱입니다. "
		"다음을 선택 하시겠습니까??",
		reply_markup=markup_keyword)

	return CHOOSING
def error(bot, update, error):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, error)



def start_chat():
	# Create the Updater and pass it your bot's token.

	updater = Updater(neo_bot_token)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],

		states={
			CHOOSING: [RegexHandler('^패스워드$',
			                        password,
			                        pass_user_data=True),

					   RegexHandler('^Something else...$',
									custom_choice),
					   ],

			TYPING_CHOICE: [MessageHandler(Filters.text,
			                               check_hint,
			                               pass_user_data=True),
							],

			TYPING_REPLY: [MessageHandler(Filters.text,
			                              check_hint,
										  pass_user_data=True),
						   ],
		},

		fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
	)
	conv_handler_keyword = ConversationHandler(
		entry_points=[CommandHandler('keyword', keyword)],

		states={
			CHOOSING: [MessageHandler(Filters.text,
			                        keyword_replay,
			                        pass_user_data=True),
			           ],

			TYPING_CHOICE: [MessageHandler(Filters.text,
			                               check_hint,
			                               pass_user_data=True),
			                ],

			TYPING_REPLY: [MessageHandler(Filters.text,
			                              check_hint,
			                              pass_user_data=True),
			               ],
		},

		fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
	)

	dp.add_handler(conv_handler)

	dp.add_handler(conv_handler_keyword)

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	return updater

def main():
	updater = start_chat()
	updater.idle()

if __name__ == '__main__':
	main()
