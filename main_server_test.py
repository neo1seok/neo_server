import os
import main_server
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

	def setUp(self):
		self.db_fd, main_server.app.config['DATABASE'] = tempfile.mkstemp()
		main_server.app.config['TESTING'] = True
		self.app = main_server.app.test_client()
		#main_server.init_db()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(main_server.app.config['DATABASE'])

	def test_empty_db(self):
		rv = self.app.get('/')
		print(rv.data)
		#assert 'No entries here so far' in rv.data.decode()

	def test_keyword_order_update_custom(self):
		rv = self.app.post('/query/keyword_order/update_custom')
		print(rv.data)
	def test_webtoon_update_custom(self):
		rv = self.app.post('/query/webtoon/update_custom')
		print(rv.data)
		#assert 'No entries here so far' in rv.data.decode()
if __name__ == '__main__':
	unittest.main()
