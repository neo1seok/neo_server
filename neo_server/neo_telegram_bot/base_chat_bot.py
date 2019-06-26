import telegram
from neolib import neo_class
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)

import logging

from neo_server.neo_telegram_bot.api_token import temptest_bot


class BaseNeoChatBot(neo_class.NeoRunnableClass):

	def __init__(self,api_token,logger=None):
		neo_class.NeoRunnableClass.__init__(self,api_token=api_token,logger=logger)
		self.api_token = api_token
		if logger == None:
			logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
			                    level=logging.DEBUG)
			logger =logging.getLogger("")

		self.logger = logger
		self.logger.info("create class %s",self.__class__.__name__)
		self._init()

	def _init(self):
		pass
	def _init_run(self):
		self.updater = Updater(self.api_token)
		self.bot = telegram.Bot(token=temptest_bot)
		# Get the dispatcher to register handlers
		self.dp = self.updater.dispatcher
		self._set_handlers()

		pass
	def _set_handlers(self):
		self.dp.add_handler(CommandHandler("start", self._start))
		self.dp.add_error_handler(self._error)

	def _start(self,bot, update):
		self.logger.debug("start")
		update.message.reply_text("HI!!!!!", reply_markup=ReplyKeyboardMarkup([ ["/check"]], one_time_keyboard=True))

	def _error(self,bot, update, error):
		"""Log Errors caused by Updates."""
		self.logger.warning('Update "%s" caused error "%s"', update, error)

	def do_run(self):
		# log all errors


		# Start the Bot
		self.updater.start_polling()

		self.updater.idle()

	def start(self):
		try:
			self.exit = self.map_args['exit']
		except:
			self.exit = True
		self._init_run()
		self.updater.start_polling()
		return self.updater

if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	                    level=logging.DEBUG)
	bot = telegram.Bot(token=temptest_bot)
	print(bot)
	bot.sendMessage(chat_id="61951841", text="체크봇 시작")

	exit()
	updater= BaseNeoChatBot(api_token = temptest_bot).start()
	updater.idle()

	pass
