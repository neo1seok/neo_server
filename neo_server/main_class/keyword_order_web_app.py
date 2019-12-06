import urllib
import urllib
import urllib.parse

from neo_server.main_class.class_web_app_base import *
from neo_server.parsing_class.show_portal_order import CheckPortalOrder


class KeywordOrderWebApp(BaseDBWebApp):
	fmt_select_keyword_order ="""SELECT seq, kwo_uid, prt_uid, `order`,keyword,url, etc, updt_date, reg_date, comment
					FROM neo_pwinfo.keyword_order where prt_uid = '{}';"""

	def init_run(self):
		#self.update_custom()
		pass
	def update_from_db(self):
		pass
		# # sql = """
		# # 		SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
		# # 		"""
		# # self.list_portals = self.select(sql)
		# # # self.list_col_name = ['검색어']
		# # for tmp in self.list_portals:
		# # 	prt_uid = tmp['prt_uid']
		# # 	list_order = self.select(self.fmt_select_keyword_order.format(prt_uid))
		# # 	tmp['list_order'] = list_order
		# # 	tmp['list_col_name'] = self.list_col_name
		# # print("self.list_portals ",self.list_portals )
		# # print("self.list_col_name ", self.list_col_name)
		# self.list_portals =[]
		# for main_url,search, list_order_org in self.list_result:
		# 	list_order =[]
		# 	for order,key_word in list_order_org:
		# 		list_order.append(dict(order=order,keyword=key_word,url=search.format(urllib.parse.quote(key_word, safe=''))))
		# 		pass
		#
		# 	self.list_portals.append(dict(title=main_url,list_order=list_order[:10]))
		# 	pass
		# pass
	# def db_format(self, prt_uid, len_order):
	# 	sql = self.fmt_select_keyword_order.format(prt_uid)
	# 	list_order_db = self.select(sql)
	# 	if len(list_order_db) > 0:
	# 		return
	# 	fmt_insert = "({0},'kwo_{0}','{1}',{2},'{3}','{4}',now(),now())"
	# 	# 0: seq 1:prt_uid 2:order 3:keyword 4:url
	# 	list_seq = self.select("select max(seq) as lastseq FROM neo_pwinfo.keyword_order")
	#
	# 	last_seq = list_seq[0]['lastseq']
	# 	last_seq = int(last_seq) if last_seq != None else 0
	# 	print(last_seq)
	# 	str_value = ",".join(
	# 		[fmt_insert.format(last_seq + idx + 1, prt_uid, idx + 1, "", "") for idx in range(len_order)])
	# 	sql = """
	# 	INSERT INTO neo_pwinfo.keyword_order(
	# 	   seq  ,kwo_uid  ,prt_uid  ,`order`, keyword,url, updt_date  ,reg_date
	# 	) VALUES {}""".format(str_value)
	#
	# 	self.cur.execute(sql)
	#
	# 	pass
	#
	# def db_update(self, obj, list_order):
	# 	fmt_update = """
	# 	UPDATE neo_pwinfo.keyword_order
	# 	SET
	# 	  keyword = '{0}' -- text
	# 	  ,url = '{1}' -- text
	# 	  ,updt_date = now() -- datetime
	#
	# 	WHERE `order` = {2} -- int(11)
	# 	  AND prt_uid = '{3}' -- varchar
	# 	"""
	# 	# 0: keyword 1:url 2: order 3:prt_uid
	# 	for order, keyword in list_order:
	# 		url = obj.search_form.format(urllib.parse.quote(keyword))
	# 		sql = fmt_update.format(keyword, url, order, obj.prt_uid)
	# 	#	print(sql)
	# 		self.cur.execute(sql)
	# 		print(order, keyword, url)

	def update_custom(self):
		print("update_custom data",self.data)
		self.list_result = CheckPortalOrder().run().result()
		list_portals = []
		for main_url, search, list_order_org in self.list_result:
			list_order = []
			for order, key_word in list_order_org:
				import urllib
				list_order.append(
					dict(order=order, keyword=key_word, url=search.format(urllib.parse.quote(key_word, safe=''))))
				pass
			
			list_portals.append(dict(title=main_url, list_order=list_order[:10]))
		table_html =render_template("keyword_order_contents.html", list_portals=list_portals)
		return dict(table_html=table_html)
		
		
		#
		# list_portals = self.select("SELECT seq, prt_uid, name, search_form, main_url FROM neo_pwinfo.portal;")
		#
		# map_portal = { tmp['main_url']:neoutil.Struct(**tmp) for tmp in list_portals}
		#
		# for main_url,search,list_order in self.list_result:
		# 	obj = map_portal[main_url]
		# 	print(obj.prt_uid)
		# 	self.db_format(obj.prt_uid,len(list_order))
		# 	self.db_update(obj,list_order)


	pass