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
import enum
import random
from enum import Enum

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

import logging

# Enable logging
from main_class.class_web_app_base import tag_session_no
from neo_telegram_bot.api_token import neo_bot_token, temptest_bot
from neo_telegram_bot.base_chat_bot import BaseNeoChatBot
from parsing_class.show_portal_order import CheckNaverDaumOrder

class BOT_STATUS(Enum):
	CHOOSING = enum.auto()
	TYPING_REPLY = enum.auto()
	TYPING_CHOICE = enum.auto()


class AUTH_STATUS(Enum):
	GIVE_HINT = enum.auto()
	CHECK_PASSWD = enum.auto()
	FINISH = enum.auto()


def conv_keyboard (list_keyboard):
	return ReplyKeyboardMarkup(list_keyboard, one_time_keyboard=True)

def conv_keyboard_inner (list_keyboard):
	return ReplyKeyboardMarkup(list_keyboard, one_time_keyboard=True)
class NeoChatBot(BaseNeoChatBot):
	CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

	reply_keyboard = [['패스워드', '포탈검색순위'],
	                  ['Done']]

	map_hint = {
			"second_sister": "0331",
			"first_sister": "1219",
			"dad": "0124",
			"mom": "1011",
			"me": "0815",
			"sewol_sadday": "0416",
		}

	reply_keyboard_cmd = [['/check', '/keyword','/auth','/test'],
	                  ['Done']]
	reply_ok_cmd = [['ok']]
	keword_query_url = {
		"네이년": "https://search.naver.com/search.naver?where=nexearch&query={keyword}&ie=utf8&sm=tab_lve",
		"다음": "https://search.daum.net/search?w=tot&DA=1TH&rtmaxcoll=1TH&q={keyword}"
	}

	markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
	markup_keyword = ReplyKeyboardMarkup([list(keword_query_url.keys()), ["DONE"]], one_time_keyboard=True)

	# def __init__(self, api_token, logger=None):
	# 	BaseNeoChatBot.__init__(self,api_token, logger)
	# 	#self.session = session
	# 	self.auth_info = dict()
		#self.clear_auth_info()
	def __init__(self, api_token, logger=None):
		super().__init__(api_token, logger=None)


	def _init(self):
		#self.conv_rep_keybaord = lambda list_keyboard:ReplyKeyboardMarkup(list_keyboard, one_time_keyboard=True)

		self.markup =conv_keyboard(self.reply_keyboard)#ReplyKeyboardMarkup(self.reply_keyboard, one_time_keyboard=True)
		self.markup_keyword = conv_keyboard([list(self.keword_query_url.keys()), ["DONE"]])

		self.clear_auth_info()
		#self.auth_info = dict(session_no ="0000000",auth=False)
		#ReplyKeyboardMarkup([list(self.keword_query_url.keys()), ["DONE"]], one_time_keyboard=True)

		pass

	def clear_auth_info(self):
		self.auth_info = dict(session_no="0000000", auth=False)

	def start_auth(self,session_no):
		self.clear_auth_info()

		self.auth_info["session_status"] = "init"
		self.auth_info["session_no"] = session_no
		#session_no

		self.bot.sendMessage(chat_id="61951841", text=f"인증 요청 {session_no}", reply_markup=conv_keyboard(self.reply_keyboard_cmd))
		self.bot.sendMessage(chat_id="61951841", text=f"/auth",)


	def _set_handlers(self):
		BaseNeoChatBot._set_handlers(self)


		auth_handler = ConversationHandler(
			entry_points=[CommandHandler('auth', self._auth,pass_user_data=True)],

			states={

				AUTH_STATUS.GIVE_HINT.value: [RegexHandler('^ok',
				                                             self._give_hint,
				                                             pass_user_data=True),
				                              RegexHandler('^cancel$', self._cancel, pass_user_data=True)

				                              ],
				AUTH_STATUS.CHECK_PASSWD.value: [MessageHandler(Filters.text,
				                                         self._check_password,
				                                         pass_user_data=True),
					                            ],
				AUTH_STATUS.FINISH.value: [MessageHandler(Filters.text,
				                                                self._finish_auth,
				                                                pass_user_data=True),
				                                 ],


			},

			fallbacks=[RegexHandler('^cancel$', self._cancel, pass_user_data=True)]
		)

		conv_handler_keyword = ConversationHandler(
			entry_points=[CommandHandler('keyword', self._keyword)],

			states={
				BOT_STATUS.CHOOSING.value: [MessageHandler(Filters.text,
				                          self._keyword_replay,
				                          pass_user_data=True),
				           ],

				BOT_STATUS.TYPING_CHOICE.value: [MessageHandler(Filters.text,
				                               self._check_hint,
				                               pass_user_data=True),
				                ],

				BOT_STATUS.TYPING_REPLY.value: [MessageHandler(Filters.text,
				                              self._check_hint,
				                              pass_user_data=True),
				               ],
			},

			fallbacks=[RegexHandler('^Done$', self._cancel, pass_user_data=True)]
		)
		self.dp.add_handler(CallbackQueryHandler(self._ok_button))
		self.dp.add_handler(auth_handler)
		self.dp.add_handler(conv_handler_keyword)

#		self.dp.add_error_handler(self._error)

		self.bot.sendMessage(chat_id="61951841", text="시작",reply_markup=conv_keyboard(self.reply_keyboard_cmd))





	def _facts_to_str(self,user_data):
		facts = list()

		for key, value in user_data.items():
			facts.append('{} - {}'.format(key, value))

		return "\n".join(facts).join(['\n', '\n'])

	def _ok_button(self,bot, update):
		query = update.callback_query

		bot.edit_message_text(text="Selected option: {}".format(query.data),
		                      chat_id=query.message.chat_id,
		                      message_id=query.message.message_id)

	def _start(self,bot, update):
		self.logger.debug("start")
		update.message.reply_text(
			"네오셕의 개인 앱입니다. "
			"다음을 선택 하시겠습니까??",
			reply_markup=conv_keyboard(self.reply_keyboard_cmd))

		#return BOT_STATUS.CHOOSING.value

	def _auth(self,bot, update, user_data):

		self.logger.debug(f"_auth {user_data}")

		session_no = self.auth_info[tag_session_no]
		self.auth_info["session_status"] = "start"
		keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
		             InlineKeyboardButton("Option 2", callback_data='2')],

		            [InlineKeyboardButton("Option 3", callback_data='3')]]

		reply_markup = InlineKeyboardMarkup(keyboard)

		update.message.reply_text(
			f"인증을 시작하겠습니다. {session_no}",reply_markup=reply_markup
			)

		return AUTH_STATUS.GIVE_HINT.value

	def _give_hint(self,bot, update, user_data):
		self.logger.debug("_give_hint")

		if self.auth_info['auth']:
			update.message.reply_text(
				'이미 인증 되었습니다.!!!!', reply_markup=conv_keyboard(self.reply_ok_cmd))
			return AUTH_STATUS.FINISH.value
		self.auth_info["session_status"] = "on_auth"
		selected_index = random.randrange(self.map_hint.__len__())
		self.logger.debug(f"selected_index {selected_index} self.map_hint.keys() {self.map_hint.keys()}")

		hint = list(self.map_hint.keys())[selected_index]

		user_data["hint"] = hint
		update.message.reply_text(
			"인증 과정입니다. "
			f"{hint} 에 대한 답변은?")
		return AUTH_STATUS.CHECK_PASSWD.value

	def _check_password(self,bot, update, user_data):
		self.logger.debug("_check_password")
		text = update.message.text
		count = user_data.get("count",0)
		self.logger.debug(f"count {count}")
		hint = user_data["hint"]
		value = self.map_hint[hint]
		if count >=3:
			update.message.reply_text(
				'인증 실패 했습니다!!!!',reply_markup=conv_keyboard(self.reply_ok_cmd))
			self.auth_info['auth'] = False
			self.auth_info["session_status"] = "done"
			return AUTH_STATUS.FINISH.value

		if value == text:
			update.message.reply_text(
				'인증되었습니다.',reply_markup=conv_keyboard(self.reply_ok_cmd))

			self.auth_info['auth'] = True
			self.auth_info["session_status"] = "done"

			user_data['count'] = 0
			return AUTH_STATUS.FINISH.value
		count+=1

		user_data["count"] =count
		update.message.reply_text(
			f'인증 실패 했습니다. 다시 입력 하십시오. {count}/3')
		return AUTH_STATUS.CHECK_PASSWD.value

	def _finish_auth(self, bot, update, user_data):
		update.message.reply_text("인증이 종료 되었습니다.", reply_markup=conv_keyboard(self.reply_keyboard_cmd))
		#self.auth_info.clear()
		user_data.clear()
		return ConversationHandler.END

	def _check_hint(self,bot, update, user_data):
		self.logger.debug("check_hint")
		text = update.message.text
		user_data['choice'] = text
		update.message.reply_text(
			'검색어를 입력하시오 '.format('내생일'))

		return BOT_STATUS.TYPING_REPLY.value

	def _password_result(self,bot, update, user_data):
		self.logger.debug("password_result")
		text = update.message.text
		user_data['choice'] = text
		update.message.reply_text(
			'검색어를 입력하시오 '.format('내생일'))

		return BOT_STATUS.TYPING_REPLY.value

	def _custom_choice(self,bot, update):
		update.message.reply_text('Alright, please send me the category first, '
		                          'for example "Most impressive skill"')

		return BOT_STATUS.TYPING_CHOICE.value

	def _received_information(self,bot, update, user_data):
		self.logger.debug("received_information")
		text = update.message.text
		category = user_data['choice']
		user_data[category] = text
		del user_data['choice']

		update.message.reply_text("Neat! Just so you know, this is what you already told me:"
		                          "{}"
		                          "You can tell me more, or change your opinion on something.".format(
			self._facts_to_str(user_data)), reply_markup=self.markup)

		return BOT_STATUS.CHOOSING.value

	def _cancel(self, bot, update, user_data):

		update.message.reply_text("cancel 되었습니다.",reply_markup=conv_keyboard(self.reply_keyboard_cmd))

		user_data.clear()
		return ConversationHandler.END

	def _keyword(self,bot, update):
		self.logger.debug("received_information")


		update.message.reply_text(
			"네오셕의 개인 앱입니다. "
			"다음을 선택 하시겠습니까??",
			reply_markup=self.markup_keyword)

		return BOT_STATUS.CHOOSING.value

	def _keyword_replay(self,bot, update, user_data):
		self.logger.debug("received_information")
		update.message.reply_text(
			"네오셕의 개인 앱입니다. "
			"다음을 선택 하시겠습니까??",
			reply_markup=self.markup_keyword)

		return BOT_STATUS.CHOOSING.value

	def _error(self,bot, update, error):
		"""Log Errors caused by Updates."""
		self.logger.warning('Update "%s" caused error "%s"', update, error)

def start(api_token):
	inst = NeoChatBot(api_token=api_token )
	updater = inst.start()
	#inst.set_session_no('00000')
	return inst

def main():
	session = dict()
	inst =start(temptest_bot)
	inst.start_auth('00000')
	inst.updater.idle()


	# updater = start_chat()
	# updater.idle()

if __name__ == '__main__':
	main()
