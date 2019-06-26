from neolib import neoutil,neo_class
import re
import requests

import  json
import time
import codecs
import base64




class GetLateestWebtoon(neo_class.NeoRunnableClass):
	webtoonurlfmt = "http://comic.naver.com/webtoon/list.nhn?titleId={0}"
	isAll = True


	def reff(self):
		id = '409629'
		nicklist = requests.get("http://comic.naver.com/webtoon/list.nhn?titleId={0}".format(id))
		print(nicklist.text)

		startstgtr = '<td class="title">'
		index = nicklist.text.index(startstgtr)
		str = nicklist.text[index:]
		regexp = r"/webtoon/detail.nhn\?titleId=" + id + r"&no=(\d{1,4}).*"
		results = re.search(regexp, str)
		print(results.group(1))

		str = '["foo", {"bar":["baz", null, 1.0, 2]}]'

		safdsf = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
		fsdf = json.loads(safdsf)

	def getTopId(self, id):

		r = requests.get(self.webtoonurlfmt.format(id))

		startstgtr = '<td class="title">'
		try:
			index = r.text.index(startstgtr)
		except ValueError:
			return None

		str = r.text[index:]
		# print(str)
		regexp = r"/webtoon/detail.nhn\?titleId=" + id + r"&no=(\d{1,4}).*"
		regexpniewno = r">(.*)</a>"

		results = re.search(regexp, str)
		str = results.group(0)

		results2 = re.search(regexpniewno, str)

		# print(results.group(1))
		# print(results2.group(1))

		return dict(id=id,lastno=results.group(1),today_title= results2.group(1))

	def getList(self, url):

		r = requests.get(url)
		print(r.text.encode());
		contents = r.text.replace(codecs.BOM_UTF8.decode(), "")
		print(contents.encode());
		self.todaylist = json.loads(contents)

		None

	def set_list_ids(self,list_ids):
		self.list_ids =list_ids
		return self

	def run(self):
		self.mapTopid = []
		for id in self.list_ids:
			tmp = self.getTopId(id)
			if tmp == None: continue
			self.mapTopid.append(tmp)

		#print(self.mapTopid)
		return self
	def result(self):
		return self.mapTopid

	# print(imglist)

	def test(self):
		print('test')
		None

if __name__ == '__main__':


	result = GetLateestWebtoon().set_list_ids(['675554', '694191', '21815', '25613', '597478']).run().result()
	print(result)

