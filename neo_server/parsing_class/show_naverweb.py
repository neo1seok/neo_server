import copy
import datetime
from pprint import pprint
from urllib.parse import urlparse

from neolib import neoutil,neo_class,crypto_util_bin
import re
import requests

import  json
import time
import codecs
import base64
from bs4 import BeautifulSoup, Tag, ResultSet
from neolib.hexstr_util import tohexstr

from neo_server.parsing_class.enum_option import WEBTOON_PARSE_OPTION


class GetLateestWebtoon(neo_class.NeoRunnableClass):
	option : WEBTOON_PARSE_OPTION
	webtoonurlfmt = "http://comic.naver.com/webtoon/list.nhn?titleId={0}&weekday={1}"
	isAll = True
	map_date ={
		'월': 'mon',
		'화': 'tue',
		'수': 'wed',
		'목': 'thu',
		'금': 'fri',
		'토': 'sat',
		'일': 'sun',
		
	}
	map_date_rev = {  val:key for key,val in map_date.items() }
	default_obj =dict(id="", lastno="", today_title="", img_src="",
		            status_icon="",writer="",web_title="",reg_date="" ,is_detail=False,hash="")
	
	def __init__(self, date=None, list_ids=[], option = WEBTOON_PARSE_OPTION.update_detail_filter_ids_up):
		neo_class.NeoRunnableClass.__init__(self)
		self.date = date
		self.list_ids=list_ids
		
		self.time_check = dict(requst_time=0,parse_time=0)
		self.option = option
		#self.set_option(option)



		#self.get_dict_from_id = self.getTopId if self.option != WEBTOON_PARSE_OPTION.no_detail else self.getJustId
		self.filterd_ids = None
		self.dict_timer={}
		self.dict_timer_time = {}
		self.main_data = None
		self.main_data_dash_data = None
		#self.st_time = time.time()
		pass



	def _write_time_check(self,key,is_start=False):
		if is_start:
			self.dict_timer_time[key] = time.time()
		else:
			self.dict_timer [key ] = time.time() - self.dict_timer_time[key]

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

	def update_detail_by_Id(self, id, date=''):
		
		url = self.webtoonurlfmt.format(id,date)
		#print(url)
		st = time.time()
		#print(url)
		r = requests.get(url)
		self.time_check['requst_time'] +=time.time()-st
		#print(r.text)
		st = time.time()
		
		soup = BeautifulSoup(r.text, 'html.parser')



		soup_tbody = soup.find("table",class_='viewList')
		
		if not soup_tbody:
			return None
		soup_tbody:Tag
		title_tag = None
		tr_tag = None
		
		for tr_tag in soup_tbody.find_all("tr"):
			tr_tag:Tag
			title_tag = tr_tag.find("td",class_="title")
			if not title_tag: continue
			
			break
			
			#get title name
		if not title_tag:
			return None
		def conv_title(text):
			return text.replace("\n", "").replace("\r", "").replace("\t\t", "").strip()
		
		today_title = title_tag.text.replace("\n","").replace("\r","")
		
		#get img src
		tag_img: Tag
		tag_img = tr_tag.find("a").find("img")
		img_src = tag_img.attrs["src"]
		
		#get last no
		url_tag = tr_tag.find("a")
		lasturl = url_tag.attrs['href']
		regexp = r"/webtoon/detail\?titleId=" + id + r"&no=(\d{1,4}).*"
		print(regexp)
		print(lasturl)
		results = re.search(regexp, lasturl)
		lastno = results.group(1)


		# get status icon
		status_icon_tag = title_tag.find("img")
		status_icon = 	status_icon_tag.attrs["src"]	if status_icon_tag else ""

		# get main title

		img = soup.find("div", class_='thumb').find("a").find("img")
		main_img_src = img.attrs["src"]


		detail_tag = soup.find("div",class_="detail")
		detail_tag:Tag
		



		
		
		web_title_tag =soup.find("div",class_='comicinfo').find("div",class_='thumb').find("a").find('img')
		#print(web_title_tag)
		web_title = web_title_tag.attrs['title']
		#web_title = detail_tag.find_all("h2")[0]
		#web_title	=	web_title.text.replace("\n","").replace("\r","")
		#
		
		# get break title
		break_title_tag = detail_tag.find("span",class_="ico_break")
		break_title = break_title_tag.text.replace("\n","").replace("\r","") if break_title_tag else ""
		
		# get writer
		writer_title_tag = detail_tag.find("span", class_="wrt_nm")
		writer =writer_title_tag.text.replace("\n","").replace("\r","").strip()
		main_desc = detail_tag.find("p").text
		
		# get reg_date
		reg_date = tr_tag.find("td", class_="num").text
		
		self.time_check['parse_time'] += time.time() - st
		return dict(id=id, lastno=lastno, today_title=conv_title(today_title), img_src=img_src,
		            status_icon=status_icon,writer=conv_title(writer),web_title=conv_title(web_title),reg_date=reg_date ,main_img_src=main_img_src,main_desc=conv_title(main_desc),is_detail=True)


	# def getJustId(self, id, date=''):
	# 	return dict(id=id,web_title=self.map_title_per_id[id])
	#
	# def getTopId_old(self, id):
	# 	#soup = BeautifulSoup(contents, 'html.parser')
	# 	r = requests.get(self.webtoonurlfmt.format(id))
	#
	# 	startstgtr = '<td class="title">'
	# 	try:
	# 		index = r.text.index(startstgtr)
	# 	except ValueError:
	# 		return None
	#
	# 	str = r.text[index:]
	# 	# print(str)
	# 	regexp = r"/webtoon/detail.nhn\?titleId=" + id + r"&no=(\d{1,4}).*"
	# 	regexpniewno = r">(.*)</a>"
	#
	# 	results = re.search(regexp, str)
	# 	str = results.group(0)
	#
	# 	results2 = re.search(regexpniewno, str)
	#
	# 	# print(results.group(1))
	# 	# print(results2.group(1))
	#
	# 	return dict(id=id,lastno=results.group(1),today_title= results2.group(1))

	def getList(self, url):

		r = requests.get(url)
		#print(r.text.encode());
		contents = r.text.replace(codecs.BOM_UTF8.decode(), "")
		#print(contents.encode());
		self.todaylist = json.loads(contents)

		None

	def set_list_ids(self,list_ids):
		self.list_ids =list_ids
		return self


	def update_get_filter_ids(self):
		st = time.time()

		assert self.main_data_dash_data != None

		all_data = self.main_data_dash_data['all_data']
		all_data:dict

		udpated_data = [id for id,con in all_data.items() if con['status'] == 'ico_updt']


		if self.option == WEBTOON_PARSE_OPTION.update_detail_all_ids:
			self.filterd_ids =  set(self.list_ids)

		elif self.option == WEBTOON_PARSE_OPTION.update_detail_all_up:
			self.filterd_ids = set(udpated_data)
		elif self.option == WEBTOON_PARSE_OPTION.update_detail_filter_ids_up:
			self.filterd_ids = set(udpated_data) & set(self.list_ids)

		return self.filterd_ids



	def run(self):
		self._write_time_check('GetLateestWebtoon.update_just_dash', True)
		self.parse_main_with_dash()
		self._write_time_check('GetLateestWebtoon.update_just_dash')

		self.update_get_filter_ids()
		print("self.filterd_ids",self.filterd_ids)
		if self.option == WEBTOON_PARSE_OPTION.update_just_dash:
			return self
		self.update_detail_info()


		return self

	@property
	def result_just_dash(self):
		return self.main_data_dash_data

	@property
	def hash_dash(self):
		return tohexstr(crypto_util_bin.sha256(json.dumps(self.main_data_dash_data).encode()))


	@property
	def result(self):
		return self.main_data

	@property
	def result_detail(self):
		all_data = self.main_data['all_data']

		self.main_data['all_data'] = { id:con for id,con in all_data.items() if con['is_detail']}

		return self.main_data

	def _col_list_from_dash(self):
		url = 'https://comic.naver.com/webtoon/weekday.nhn'

		self._write_time_check('GetLateestWebtoon._col_list_from_dash.requests', True)
		r = requests.get(url)
		self._write_time_check('GetLateestWebtoon._col_list_from_dash.requests')
		# print(r.text)
		self._write_time_check('GetLateestWebtoon._col_list_from_dash.get.col_list', True)
		self._write_time_check('GetLateestWebtoon._col_list_from_dash.get.BeautifulSoup', True)
		soup = BeautifulSoup(r.text, 'html.parser')
		self._write_time_check('GetLateestWebtoon._col_list_from_dash.get.BeautifulSoup', False)
		soup: Tag
		self._write_time_check('GetLateestWebtoon._col_list_from_dash.get.col_list', True)
		col_list_tag = soup.find("div", class_='list_area daily_all').find_all("div", class_='col')
		self._write_time_check('GetLateestWebtoon._col_list_from_dash.get.col_list')
		result = {}
		id_per_date = {}
		today_date = ""
		return soup,col_list_tag

	def get_today(self):
		self._write_time_check('GetLateestWebtoon.get_today', True)
		soup, col_list_tag = self._col_list_from_dash()
		for col in col_list_tag:
			col: Tag
			col_inner_tag = col.find("div", class_='col_inner')
			week_date = col_inner_tag.find("h4").attrs['class'][0]
			# print("week_date",week_date)

			if "col_selected" in col.attrs['class']:
				# print("col_selected",week_date)
				today_date = week_date
		self._write_time_check('GetLateestWebtoon.get_today')
		return 	today_date

	def parse_main_with_dash(self):
		url = 'https://comic.naver.com/webtoon/weekday.nhn'
		soup,col_list_tag = self._col_list_from_dash()

		id_per_date ={}
		all_data = {}
		today_date =""
		self._write_time_check('GetLateestWebtoon.parse_main_with_dash.parse',True)
		for col in col_list_tag:
			col:Tag
			col_inner_tag = col.find("div", class_='col_inner')
			week_date = col_inner_tag.find("h4").attrs['class'][0]
			#print("week_date",week_date)
			
			if "col_selected" in col.attrs['class']:
				#print("col_selected",week_date)
				today_date =week_date
			
			img_list_tag = soup.find("ul", class_='img_list')
			img_list_tag: Tag
			#print("week_date:", week_date)
			list_ids = []
			
			for tmp_tag_list in col_inner_tag.find_all("li"):
				thumb_tag = tmp_tag_list.find("div", class_='thumb')
				alink = thumb_tag.find('a')
				atitle = tmp_tag_list.find('a',class_='title')
				link = alink.attrs['href']
				title = atitle.attrs['title']
				parts = urlparse(link)
				em = alink.find("em")
				status = ""
				if em:
					status = em.attrs["class"][0]

				dict_args = dict([tmp.split("=") for tmp in parts.query.split("&")])
				#print(dict_args['titleId'])
				titleId = dict_args['titleId']
				
				list_ids.append(titleId)
				all_data[titleId] = dict(titleId=titleId, title=title, status=status,week_date=week_date,is_detail=False)
				
				#yield dict_args['titleId']
				# list_ids.append((dict_args['titleId'],title))
				pass
			id_per_date[week_date] = list_ids
			#print(id_per_date.keys())
#			self._write_time_check('GetLateestWebtoon.parse_main_with_dash.parse')
			#print(col.attrs['class'])
		#return 	dict(today_date=today_date,all_data=all_data)
		self.main_data_dash_data =dict(today_date=today_date, all_data=all_data)

		return self.main_data_dash_data
		#print("img_list_tag",img_list_tag)

	def update_detail_info(self):

		assert self.main_data_dash_data != None
		assert self.filterd_ids != None

		self.main_data = copy.deepcopy(self.main_data_dash_data)

		all_data = self.main_data['all_data']

		for id in self.filterd_ids:
			contents = all_data.get(id)
			if not contents:continue

			contents:dict
			#status = contents['status']

			#if status != 'ico_updt':continue

			tmp = self.update_detail_by_Id(id)

			#tmp = self.get_dict_from_id(id)

			if tmp == None: continue

			new_obj = copy.deepcopy(self.default_obj)


			new_obj.update(**tmp)

			new_obj['hash'] = tohexstr(crypto_util_bin.sha256(json.dumps(tmp).encode()))
			print(new_obj)
			contents.update(**new_obj)
			#self.mapTopid.append(new_obj)
		pass
	
	# def parse_main(self):
	# 	url ='https://comic.naver.com/webtoon/weekdayList.nhn'
	# 	date = self.date
	#
	# 	if date:
	# 		#eng_date = self.map_date[date]
	# 		eng_date = self.date
	# 		url +=f'?week={eng_date}'
	# 	r = requests.get(url)
	# 	#print(r.text)
	# 	soup = BeautifulSoup(r.text, 'html.parser')
	# 	soup:Tag
	# 	img_list_tag = soup.find("ul",class_='img_list')
	# 	img_list_tag:Tag
	# 	#list_ids =[]
	# 	for tmp_tag_list in img_list_tag.find_all("li"):
	# 		thumb_tag = tmp_tag_list.find("div",class_='thumb')
	# 		alink = thumb_tag.find('a')
	# 		link = alink.attrs['href']
	# 		title = alink.attrs['title']
	# 		parts = urlparse(link)
	# 		dict_args = dict([ tmp.split("=")for tmp in parts.query.split("&")])
	# 		#print(dict_args)
	# 		yield 	dict_args['titleId']
	# 		#list_ids.append((dict_args['titleId'],title))
	# 		pass
	#
	# 	sub_title_tag = soup.find('div',class_='view_type').find("h3", class_='sub_tit')
	# 	#print(sub_title_tag.text)
	# 	self.cur_web_date = re.match(r'(월|화|수|목|금|토|일)요 전체 웹툰',sub_title_tag.text).group(1)
	# 	#print(date)
	#
	#
	# 	#return list_ids

	def test(self):
		print('test')
		None

if __name__ == '__main__':
	list_all = ["783053"]
	#list_all = ["21815", ]
	today = datetime.datetime.today()
	tday = datetime.datetime(2019,12,26)
	print(type(today.date()-tday.date()))

	#result = GetLateestWebtoon().set_list_ids(['675554', '694191', '21815', '25613', '597478']).run().result()
	#print(result)
	#dict_res = inst = GetLateestWebtoon(date='mon', list_ids=list_all).parse_main_with_dash()
	#print(dict_res)
	#exit()
	# res = GetLateestWebtoon().parse_main_with_dash()
	#
	# print(res)
	# exit()



	inst = GetLateestWebtoon(date='all'
	                              '',list_ids=list_all,option=WEBTOON_PARSE_OPTION.update_detail_all_ids)
	#res = inst.parse_main_with_dash()
	print("inst.get_today()",inst.get_today())
	result_main =inst.run()

	pprint(inst.result, sort_dicts=False)
	pprint(inst.result_detail, sort_dicts=False)
	print("inst.hash_dash", inst.hash_dash)

	#pprint(result_main, sort_dicts=False)
	#
	exit()

	inst.update_get_filter_ids()

	inst.run()
	result = 	inst.result()
	for tmp in result:
		print(tmp['id'],tmp['web_title'],tmp['today_title'],tmp['reg_date'])
	pprint(result)
	print(inst.time_check)
	print(inst.today_date)
	#parse_main
	



