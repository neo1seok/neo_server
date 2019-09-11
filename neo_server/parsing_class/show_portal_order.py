import json

import requests
from neolib import neo_class, neoutil
import re
from bs4 import BeautifulSoup, Tag


def comm_parser(contents:str,patt_title:str,start_tag:str,end_tag:str):

	try:
		st = contents.index(start_tag)
		ed = contents.index(end_tag, st)
		narrow_contents = contents[st:ed]
	except:
		narrow_contents = contents


#	print(re.findall(patt_title, narrow_contents))
	return re.findall(patt_title, narrow_contents)

def parse_naver(contents:str):
	patt_title =r'<span class="ah_r">(\d+)</span>s*\n\s*<span class="ah_k">(.+)</span>'
	start_tag = '<div class="ah_roll_area PM_CL_realtimeKeyword_rolling">'
	end_tag = '</div>'
	return comm_parser(contents,patt_title,start_tag,end_tag)

def parse_daum(contents:str):
	patt_title = r'<span class="num_pctop rank\d+"><span class="ir_wa">(\d+)위</span></span>\s*\n\s*<span class="txt_issue"><a href=".+" class="link_issue">(.+)</a></span>'
	start_tag = '<h4 class="tit_hotissue">실시간 이슈 검색어</h4>'
	end_tag = "</ol>"

	return comm_parser(contents, patt_title, start_tag, end_tag)


def parse_zum(contents:str):
	soup = BeautifulSoup(contents, 'html.parser')
	div_issue_keyword = soup.find('div', class_='issue_keyword')
	for tmp in  div_issue_keyword.find_all("li"):
		print(tmp)

		f_nump = tmp.find("span",class_='r_num')
		f_a = tmp.find("a", class_='d_btn_keyword')
		print(f_nump.text,f_a.text)

	return


def parse_nate(contents:str):
	soup = BeautifulSoup(contents, 'html.parser')
	div_issue_keyword = soup.find('div', class_='kwd_list')
	for tmp in  div_issue_keyword.find_all("li"):
		#
		f_nump = tmp.find("span",class_='nHide')
		f_a = tmp.find("a")
		print(f_nump.text,f_a.text)

	return
class CheckNaverDaumOrder(neo_class.NeoRunnableClass):
	url_portal_order = "http://localhost/query/keyword_order/update"

	def __init__(self):
		neo_class.NeoRunnableClass.__init__(self)
		self.list_tuples =[
			("naver.com","https://www.naver.com", 'naver.html',
			 'https://search.naver.com/search.naver?where=nexearch&query={}&ie=utf8&sm=tab_lve',parse_naver),
			("daum.net","https://www.daum.net",
			 'daum.html', 'https://search.daum.net/search?w=tot&DA=1TH&rtmaxcoll=1TH&q={}',parse_daum),
			("zum.com","http://zum.com",
			 'zum.html','http://search.zum.com/search.zum?query={}',parse_zum),
			("nate.com", "http://nate.com",
			 'nate.html', 'https://search.daum.net/nate?w=tot&q={}', parse_nate),

		]
		self.list_result =[]



	def result(self):
		return self.list_result


	def run(self):

		for title, url, outfile, search, parser in self.list_tuples:
			# url = "https://www.naver.com"
			r = requests.get(url)

			neoutil.StrToFile(r.text, outfile)
			parse_name = parser(r.text)

			self.list_result.append(
				(title, [(ord, title) for ord, title in parse_name]))
			#print(search.format(urllib.parse.quote(title)))


		return self
		# r = requests.post(self.url_portal_order, data=dict(json_list_result=json.dumps(self.list_result)))
		# print(r.text)
		# return
		# sql = """
		# SELECT prt_uid, main_url 	FROM neo_pwinfo.portal;
		# """
		# self.cur.execute(sql)
		# fmt_insert="({0},'kwo_{0}','{1}',{2},'{3}','{4}',now(),now())"
		# # 0: seq 1:prt_uid 2:order 3:keyword 4:url
		# list_potal =self.cur.fetchall()
		# map_portal = { tmp['main_url']:neoutil.Struct(**tmp) for tmp in list_potal}
		# for main_url,list_order in self.list_result:
		# 	obj = map_portal[main_url]
		# 	print(obj.prt_uid)
		# 	self.db_format(obj.prt_uid,len(list_order))
		# 	self.db_update(obj.prt_uid,list_order)
		# 	continue
		# 	sql = """SELECT seq, kwo_uid, prt_uid, `order`,keywords, etc, updt_date, reg_date, comment
		# 	FROM neo_pwinfo.keyword_order where prt_uid = '{}';""".format(obj.prt_uid)
		# 	self.cur.execute(sql)
		# 	list_order_db = self.cur.fetchall()
		# 	if len(list_order_db)  > 0:
		# 		self.cur.execute("""delete from neo_pwinfo.keyword_order
		# 		where prt_uid = '{}';""".format(obj.prt_uid))
		#
		#
		# 	for order,keyword,url in list_order:
		# 		print(order,keyword,url)
		# 	str_value = ",".join([fmt_insert.format(obj.prt_uid,order,keyword,url ) for order,keyword,url in list_order])
		# 	self.cur.execute("""
		# 					INSERT INTO neo_pwinfo.keyword_order(
		# 					   seq  ,kwo_uid  ,prt_uid  ,`order`, keyword,url, updt_date  ,reg_date
		# 					) VALUES {}""".format(str_value))
		# #	neoutil.simple_view_list(list_order)
		# pass

if __name__ == "__main__":
	from urllib.parse import unquote

	url = """example.com?title=%D0%BF%D1%80%D0%B0%D0%B2%D0%BE%D0%B2%D0%B0%D1%8F+%D0%B7%D0%B0%D1%89%D0%B8%D1%82%D0%B0"""

	import urllib.parse


	#print('https://search.naver.com/search.naver?where=nexearch&query={}&ie=utf8&sm=tab_lve'.format(urllib.parse.quote("박근헤")))
	# contents = neoutil.StrFromFile('rsc/nate.html')
	# #parse_zum(contents)
	#
	# parse_nate(contents)
	# exit()
	# url = unquote('https://search.naver.com/search.naver?where=nexearch&query={}&ie=utf8&sm=tab_lve'.format("박근헤"))
	# print(url)
	result = CheckNaverDaumOrder().run().result()
	for portal, list_keyword in result:
		print(portal)
		for keyword in list_keyword:
			print(keyword)

	pass