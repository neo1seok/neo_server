from urllib.parse import urlparse

from neolib import neoutil,neo_class
import re
import requests

import  json
import time
import codecs
import base64
from bs4 import BeautifulSoup, Tag, ResultSet


class GetLateestWebtoon(neo_class.NeoRunnableClass):
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
	
	def __init__(self,date=None,list_ids=[]):
		neo_class.NeoRunnableClass.__init__(self)
		self.date = date
		self.list_ids=list_ids
		
		self.time_check = dict(requst_time=0,parse_time=0)
		
		pass
	
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

	def getTopId(self, id,date=''):
		
		url = self.webtoonurlfmt.format(id,date)
		#print(url)
		st = time.time()
		print(url)
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
		regexp = r"/webtoon/detail.nhn\?titleId=" + id + r"&no=(\d{1,4}).*"
		results = re.search(regexp, lasturl)
		lastno = results.group(1)
		
		# get status icon
		status_icon_tag = title_tag.find("img")
		status_icon = 	status_icon_tag.attrs["src"]	if status_icon_tag else ""
		
		
		detail_tag = soup.find("div",class_="detail")
		detail_tag:Tag
		
		#get main title
		
		
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
		
		# get reg_date
		reg_date = tr_tag.find("td", class_="num").text
		
		self.time_check['parse_time'] += time.time() - st
		return dict(id=id, lastno=lastno, today_title=conv_title(today_title), img_src=img_src,
		            status_icon=status_icon,writer=conv_title(writer),web_title=conv_title(web_title),reg_date=reg_date )
		
		
	def getTopId_old(self, id):
		#soup = BeautifulSoup(contents, 'html.parser')
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
		#print(r.text.encode());
		contents = r.text.replace(codecs.BOM_UTF8.decode(), "")
		#print(contents.encode());
		self.todaylist = json.loads(contents)

		None

	def set_list_ids(self,list_ids):
		self.list_ids =list_ids
		return self

	def run(self):
		self.cur_web_date = ""
		self.filterd_ids = self.list_ids
		st = time.time()
		if self.date != 'org':

			main_info = self.parse_main_with_dash()
			today_date = main_info['today_date']
			self.cur_web_date = today_date
			self.today_date =today_date

			id_per_date = main_info['id_per_date']
			if not self.date:
				self.date = today_date
				
			
			list_tuple_ids = id_per_date[self.date]
			today_list_ids = [id for id,title in list_tuple_ids]
			if self.date == 'all':
				today_list_ids=[]
				for tmpdate,list_tuple_ids in id_per_date.items():
					today_list_ids += [id for id,title in list_tuple_ids]
				#[[id for id,title in list_tuple_ids] for list_tuple_ids in id_per_date.items()]
			
			
			self.filterd_ids = set(today_list_ids) & set(self.list_ids)
		
			
		# if not self.date =='all':
		# 	today_list_ids = list(self.parse_main())
		# 	self.filterd_ids = set( today_list_ids) & set(self.list_ids)
		# 	print('today_list_ids',today_list_ids)
		# 	print('list_ids',self.list_ids)
		# 	print('filterd_ids',self.filterd_ids)
		print("total list part",time.time()-st)
		st = time.time()
		self.mapTopid = []
		for id in self.filterd_ids:
			tmp = self.getTopId(id)
			if tmp == None: continue
			self.mapTopid.append(tmp)
		print("latest part", time.time() - st)
		#print(self.mapTopid)
		return self
	
	def run_old(self):
		self.cur_web_date = ""
		self.filterd_ids = self.list_ids
		st = time.time()
		if not self.date =='all':
			today_list_ids = list(self.parse_main())
			self.filterd_ids = set( today_list_ids) & set(self.list_ids)
			print('today_list_ids',today_list_ids)
			print('list_ids',self.list_ids)
			print('filterd_ids',self.filterd_ids)
		print("total list part",time.time()-st)
		st = time.time()
		self.mapTopid = []
		for id in self.filterd_ids:
			tmp = self.getTopId(id)
			if tmp == None: continue
			self.mapTopid.append(tmp)
		print("latest part", time.time() - st)
		#print(self.mapTopid)
		return self
	
	def result(self):
		return self.mapTopid
	
	def parse_main_with_dash(self):
		url = 'https://comic.naver.com/webtoon/weekday.nhn'
		date = self.date
		r = requests.get(url)
		# print(r.text)
		soup = BeautifulSoup(r.text, 'html.parser')
		soup: Tag
		col_list_tag = soup.find("div", class_='list_area daily_all').find_all("div", class_='col')
		result = {}
		id_per_date ={}
		today_date =""
		for col in col_list_tag:
			col:Tag
			col_inner_tag = col.find("div", class_='col_inner')
			week_date = col_inner_tag.find("h4").attrs['class'][0]
			print("week_date",week_date)
			
			if "col_selected" in col.attrs['class']:
				print("col_selected",week_date)
				today_date =week_date
			
			img_list_tag = soup.find("ul", class_='img_list')
			img_list_tag: Tag
			
			list_ids =[]
			
			for tmp_tag_list in col_inner_tag.find_all("li"):
				thumb_tag = tmp_tag_list.find("div", class_='thumb')
				alink = thumb_tag.find('a')
				atitle = tmp_tag_list.find('a',class_='title')
				link = alink.attrs['href']
				title = atitle.attrs['title']
				parts = urlparse(link)
				dict_args = dict([tmp.split("=") for tmp in parts.query.split("&")])
				print(dict_args['titleId'])
				titleId = dict_args['titleId']
				
				list_ids.append((titleId,title))
				
				#yield dict_args['titleId']
				# list_ids.append((dict_args['titleId'],title))
				pass
			id_per_date[week_date] = list_ids
			print(col.attrs['class'])
		return 	dict(id_per_date=id_per_date,today_date=today_date)
		#print("img_list_tag",img_list_tag)
	
	def parse_main(self):
		url ='https://comic.naver.com/webtoon/weekdayList.nhn'
		date = self.date
		
		if date:
			#eng_date = self.map_date[date]
			eng_date = self.date
			url +=f'?week={eng_date}'
		r = requests.get(url)
		#print(r.text)
		soup = BeautifulSoup(r.text, 'html.parser')
		soup:Tag
		img_list_tag = soup.find("ul",class_='img_list')
		img_list_tag:Tag
		#list_ids =[]
		for tmp_tag_list in img_list_tag.find_all("li"):
			thumb_tag = tmp_tag_list.find("div",class_='thumb')
			alink = thumb_tag.find('a')
			link = alink.attrs['href']
			title = alink.attrs['title']
			parts = urlparse(link)
			dict_args = dict([ tmp.split("=")for tmp in parts.query.split("&")])
			#print(dict_args)
			yield 	dict_args['titleId']
			#list_ids.append((dict_args['titleId'],title))
			pass
		
		sub_title_tag = soup.find('div',class_='view_type').find("h3", class_='sub_tit')
		#print(sub_title_tag.text)
		self.cur_web_date = re.match(r'(월|화|수|목|금|토|일)요 전체 웹툰',sub_title_tag.text).group(1)
		#print(date)
		
		
		#return list_ids

	def test(self):
		print('test')
		None

if __name__ == '__main__':
	list_all = ["675554","665170","22897","21815","25455","570506","641253","670139","690503","703307","695321","696617","597478","710766","703836","723714","710751","712694","727268","726842","728750","730259","730148","729255","733413"]
	#list_all = ["21815", ]

	#result = GetLateestWebtoon().set_list_ids(['675554', '694191', '21815', '25613', '597478']).run().result()
	#print(result)
	#dict_res = inst = GetLateestWebtoon(date='mon', list_ids=list_all).parse_main_with_dash()
	#print(dict_res)
	#exit()
	inst = GetLateestWebtoon(date='mon'
	                              '',list_ids=list_all).run()
	result = 	inst.result()
	for tmp in result:
		print(tmp['id'],tmp['web_title'],tmp['today_title'],tmp['reg_date'])
	print(result)
	print(inst.time_check)
	#parse_main
	



