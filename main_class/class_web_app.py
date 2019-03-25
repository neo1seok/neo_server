import random
import urllib

import pymysql
import time
from flask import render_template, json, session, request
import collections,os
from neolib import neoutil,crypto_util_bin
from neolib.hexstr_util import *

from main_class.class_web_app_base import *
from neo_telegram_bot.neo_chat_bot import NeoChatBot
from parsing_class.show_naverweb import GetLateestWebtoon
from parsing_class.show_portal_order import CheckNaverDaumOrder


class SampleWebApp(BaseDBWebApp):
	pass


class WebtoonWebApp(BaseDBWebApp):
	def init(self):
		BaseDBWebApp.init(self)
		self.title_org = self.title

	def init_run(self):
		self.update_custom()


		pass
	def get_today_date(self):
		import time
		now = time.localtime()

		week = ['월', '화', '수', '목', '금', '토', '일']
		date_name = week[now.tm_wday]
		return date_name

	def ready_extra_condition(self):
		# import time
		# now = time.localtime()
		#
		# week = ['월', '화', '수', '목', '금', '토', '일']
		# date_name = week[now.tm_wday]
		# print('오늘 요일: %s요일' % date_name)
		BaseDBWebApp.ready_extra_condition(self)
		type = neoutil.get_safe_mapvalue(request.values, "type", "")
		self.title = "{} ({}요일)".format(self.title_org,self.get_today_date())

		self.extra_condition += "and dates regexp '%s'" % self.get_today_date()

		if type == "all":
			self.extra_condition = ""

		pass
	def post_process(self):
		sql = """
				SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
				"""
		list_portals = self.select(sql)

		for map_line in self.list_data:

			map_line['list_url'] =map_line['list_url'].format(map_line['id'])
			map_line['detail_url'] = map_line['detail_url'].format(map_line['id'],map_line['lastno'])
			#print("map_url", map_line['list_url'], map_line['detail_url'])




		list_input_row = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="웹툰이름",name="title",id="input_title",row_type="all",type="input"),
			row_dict(title="웹툰아이디", name="id", id="input_id", row_type="left", type="input"),
			row_dict(title="요일",name="dates",id="input_dates",row_type="right",type="input"),
			row_dict(title="포탈", name="prt_uid", id="input_prt_uid",
			row_type='all',type="select",
			list_options=[ dict(value=map_portal['prt_uid'],name=map_portal["title"]) for map_portal in list_portals])
		                  ]
		#self.list_tables

		this_table =	dict(title="웹툰",
			     list_input_row=list_input_row,
			     list_col_info=[
				dict(title="제목",type="link",href_key="list_url",title_key="title"),
				dict(title="제목", type="link",href_key="detail_url",title_key= "today_title"),
				dict(title="편집", type="btn",onclick="edit_content"),
				dict(title="삭제", type="btn_no_modal",onclick="delete_content"),
			],
			     list_data = self.list_data)

		self.list_tables[0].update(this_table)
		neoutil.simple_view_list(self.list_data)
		pass
	# def post_process_old(self):
	# 	for map_line in self.list_data:
	#
	# 		map_line['list_url'] =map_line['list_url'].format(map_line['id'])
	# 		map_line['detail_url'] = map_line['detail_url'].format(map_line['id'],map_line['lastno'])
	# 		print("map_url", map_line['list_url'], map_line['detail_url'])
	#
	# 	sql = """
	# 	SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
	# 	"""
	# 	self. list_portals = self.select(sql)
	# 	print(self.list_portals)
	# 	pass
	def update_custom(self):
		sql = """SELECT id FROM neo_pwinfo.webtoon where dates regexp '{}' ;""".format(self.get_today_date())
		print(sql)
		list_ids = self.select(sql)
		print(sql,list_ids)
		list_result = GetLateestWebtoon().set_list_ids([tmp['id'] for tmp in list_ids]).run().result()
		for tmp_dic in list_result:
			sql_update ="""UPDATE neo_pwinfo.webtoon 
						SET  today_title = '{today_title}',  lastno = '{lastno}', updt_date = now()
						WHERE id='{id}';""".format(**tmp_dic)
			self.cur.execute(sql_update)
		print(list_result)
		return dict(result='ok')


class FavLinkDBWebApp(BaseDBWebApp):
	def ready_extra_condition(self):
		type= neoutil.get_safe_mapvalue(request.values,"type","main")

		print("FavLinkDBWebApp ready_extra_condition",type)

		self.extra_condition = "and type = '{type}'".format(type=type.upper())
		print("extra_condition",self.extra_condition)

		pass
	def post_process(self):


		list_input_row = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="제목", name="title", id="input_title", row_type="all", type="input"),
			row_dict(title="링크", name="link", id="input_link", row_type="all", type="input"),

		]

		this_table = 			dict(title="전체리스트",
			   form_title="개인링크",
			   list_input_row=list_input_row,
			   list_col_info=[
				     dict(title="링크", type="link", href_key="link", title_key="title"),
				     dict(title="편집", type="btn", onclick="edit_content"),
				     dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
			     ],
			     list_data=self.list_data)

		self.list_tables[0].update(this_table)
		neoutil.simple_view_list(self.list_data)
		pass
	# def is_login(self):
	# 	if self.name == "fav_link_prv":
	# 		print("is_login")
	# 		return neoutil.get_safe_mapvalue(session, tag_login, False)
	# 	return True
	pass


class TodayContentsWebApp(BaseDBWebApp):
	def post_process(self):


		list_input_row = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="제목", name="title", id="input_title", row_type="all", type="input"),
			row_dict(title="이슈", name="issue", id="input_issue", row_type="all", type="text"),
			row_dict(title="솔루션", name="solution", id="input_solution", row_type="all", type="text"),

		]

		list_attr = [dict(key="data-toggle",val="modal"),
		             dict(key="data-target", val="#id_modal_input"),
		             ]
		list_attr_ext = [dict(key="onclick", proc=lambda item:"edit_content('{cur_uid}')".format(cur_uid=item['cur_uid']))]
		text_ext = lambda item: item['title']

		this_table = dict(title="전체리스트",
				form_title="title",

			     list_input_row=list_input_row,
			     list_col_info=[
				     dict(title="제목", type="btn_ext", onclick="edit_content",href_key="link", title_key="title",
				          list_attr=list_attr,
				          list_attr_ext=list_attr_ext,
				          text_ext=lambda
					          item: item['title'],

				          ),
				     dict(title="날짜", type="title",  title_key="updt_date"),
				     dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
			     ],
			     list_data=self.list_data)

		self.list_tables[0].update(this_table)
		neoutil.simple_view_list(self.list_data)
		pass


class KeywordOrderWebApp(BaseDBWebApp):
	fmt_select_keyword_order ="""SELECT seq, kwo_uid, prt_uid, `order`,keyword,url, etc, updt_date, reg_date, comment 
					FROM neo_pwinfo.keyword_order where prt_uid = '{}';"""

	def init_run(self):
		self.update_custom()
		pass
	def update_from_db(self):
		sql = """
				SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
				"""
		self.list_portals = self.select(sql)
		# self.list_col_name = ['검색어']
		for tmp in self.list_portals:
			prt_uid = tmp['prt_uid']
			list_order = self.select(self.fmt_select_keyword_order.format(prt_uid))
			tmp['list_order'] = list_order
			tmp['list_col_name'] = self.list_col_name
		print("self.list_portals ",self.list_portals )
		print("self.list_col_name ", self.list_col_name)

		pass
	def db_format(self, prt_uid, len_order):
		sql = self.fmt_select_keyword_order.format(prt_uid)
		list_order_db = self.select(sql)
		if len(list_order_db) > 0:
			return
		fmt_insert = "({0},'kwo_{0}','{1}',{2},'{3}','{4}',now(),now())"
		# 0: seq 1:prt_uid 2:order 3:keyword 4:url
		list_seq = self.select("select max(seq) as lastseq FROM neo_pwinfo.keyword_order")

		last_seq = list_seq[0]['lastseq']
		last_seq = int(last_seq) if last_seq != None else 0
		print(last_seq)
		str_value = ",".join(
			[fmt_insert.format(last_seq + idx + 1, prt_uid, idx + 1, "", "") for idx in range(len_order)])
		sql = """
		INSERT INTO neo_pwinfo.keyword_order(
		   seq  ,kwo_uid  ,prt_uid  ,`order`, keyword,url, updt_date  ,reg_date 
		) VALUES {}""".format(str_value)

		self.cur.execute(sql)

		pass

	def db_update(self, obj, list_order):
		fmt_update = """
		UPDATE neo_pwinfo.keyword_order
		SET
		  keyword = '{0}' -- text
		  ,url = '{1}' -- text
		  ,updt_date = now() -- datetime

		WHERE `order` = {2} -- int(11)
		  AND prt_uid = '{3}' -- varchar
		"""
		# 0: keyword 1:url 2: order 3:prt_uid
		for order, keyword in list_order:
			url = obj.search_form.format(urllib.parse.quote(keyword))
			sql = fmt_update.format(keyword, url, order, obj.prt_uid)
		#	print(sql)
			self.cur.execute(sql)
			print(order, keyword, url)

	def update_custom(self):
		print("update_custom data",self.data)
		self.list_result = CheckNaverDaumOrder().run().result()
		list_portals = self.select("SELECT seq, prt_uid, name, search_form, main_url FROM neo_pwinfo.portal;")

		map_portal = { tmp['main_url']:neoutil.Struct(**tmp) for tmp in list_portals}

		for main_url,list_order in self.list_result:
			obj = map_portal[main_url]
			print(obj.prt_uid)
			self.db_format(obj.prt_uid,len(list_order))
			self.db_update(obj,list_order)


	pass


class PasswdWebApp(BaseDBWebApp):
	# def is_login(self):
	# 	print("is_login")
	# 	return neoutil.get_safe_mapvalue(session, tag_login, False)
	def ready_extra_condition(self):
		fmt_repl = "and site regexp '{keyword}'"

		type= neoutil.get_safe_mapvalue(request.values,"type","")
		keyword = neoutil.get_safe_mapvalue(request.values, "keyword", "")
		print("PasswdWebApp ready_extra_condition",type, keyword)
		if type == "":
			self.extra_condition =  fmt_repl.format(keyword="FFFFFFFFFFFFFFFFFFFFFFFFF")
		elif type == "search":
			self.extra_condition = fmt_repl.format(keyword=keyword)
		elif type == "all":
			self.extra_condition = ""
		print("extra_condition",self.extra_condition)

		pass
	pass
	def post_process(self):
		self.list_header = self.select("SELECT phd_uid, title, hint, special_letter FROM pheader;")


		list_input_site = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="site", name="site", id="input_site", row_type="left", type="input"),
			row_dict(title="header", name="phd_uid", id="input_header", row_type="right",
			     type="select",
			     list_options = [ dict(value=map_portal['phd_uid'], name=map_portal["title"]) for map_portal in self.list_header]),
			row_dict(title="ptail", name="ptail", id="input_ptail", row_type="left", type="input"),
			row_dict(title="id", name="id", id="input_id", row_type="right", type="input"),
			row_dict(title="etc", name="etc", id="input_etc", row_type="all", type="text"),

		]
		list_input_header = [

			row_dict(name="phd_uid", id="input_phd_uid", type='hidden'),
			row_dict(title="헤더이름", name="title", id="input_title_header", row_type="left", type="input"),
			row_dict(title="특수문자", name="special_letter", id="input_special_letter", row_type="right", type="input"),
			row_dict(title="힌트", name="hint", id="input_hint", row_type="all", type="input"),



		]

		list_attr = [dict(key="data-toggle", val="modal"),
		             dict(key="data-target", val="#id_modal_input"),
		             ]
		list_attr_header = [dict(key="data-toggle", val="modal"),
		             dict(key="data-target", val="#id_modal_input_header"),
		             ]
		list_attr_ext = [
			dict(key="onclick", proc=lambda item: "edit_content('{cur_uid}')".format(cur_uid=item['cur_uid']))]
		list_attr_header_ext = [
			dict(key="onclick", proc=lambda item: "edit_content_header('{phd_uid}')".format(phd_uid=item['phd_uid']))]
		text_ext = lambda item: item['site']
		text_header_ext = lambda item: item['title']

		this_table = dict(title="사이트리스트",
			 form_title="title",
			query_option="site",
		     list_input_row=list_input_site,

		     list_data=self.list_data,
		     list_col_info=[
			     dict(title="사이트", type="btn_ext", text_ext=text_ext, list_attr=list_attr, list_attr_ext=list_attr_ext),
			     dict(title="헤더", type="btn_ext", text_ext=text_header_ext, list_attr=list_attr_header,
			          list_attr_ext=list_attr_header_ext),
			     dict(title="테일", type="title", title_key="ptail"),
			     dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
		     ])
		this_table_header =dict(title="헤더리스트",
		     modal_id="id_modal_input_header",
		    id_div_list="div_list_header",
		     form_id="form_input_header", form_title="헤더입력",
		     button_id="",
		     query_option="header",
		     new_input_button="헤더 새로 입력",

		     enable_function="enable_input_header",
		     input_class="neo_form_header",

		     check_box_id="id_check_box_header",
		     edit_function="edit_content_header",
		     delete_function="delete_content_header",
		     new_input_function="new_input_function_header",

		     list_input_row=list_input_header,
		     list_data=self.list_header,
		     list_col_info=[
			     # dict(title="사이트", type="btn_ext",text_ext=text_ext,list_attr=list_attr,list_attr_ext=list_attr_ext),
			     dict(title="헤더", type="btn_ext", text_ext=text_header_ext, list_attr=list_attr_header,
			          list_attr_ext=list_attr_header_ext),


		     ])
		self.list_tables[0].update(this_table)
		if len(self.list_tables) ==1:
			self.list_tables.append(this_table_header)
		else:
			self.list_tables[1].update(this_table_header)
		neoutil.simple_view_list(self.list_data)
		pass

	def get_content(self):
		print('get_content',self.data.option)
		if self.data.option == 'site':
			return BaseDBWebApp.get_content(self)
		elif self.data.option == 'header':
			list_header = self.select("""SELECT phd_uid, title, hint, special_letter 
			FROM pheader where phd_uid = '{cur_uid}';""".format(cur_uid=self.data.cur_uid ))

			response = list_header[0]
			response['result'] = "ok"
			return response
			pass
		else:
			raise Exception("not allowd option")

		pass


class HealthWebApp(BaseDBWebApp):
	def post_process(self):

		def_sys_bp = ""
		def_dia_bp = ""
		def_pulse = ""
		def_weight = ""

		last_seq, last_uid = self.get_last_uid()

		list_dict_col = self.select("select * from {table_name} where hlt_uid = '{last_uid}'".format(table_name = self.table_name,last_uid=last_uid))
		print(list_dict_col)
		if len(list_dict_col)>0:
			rows = list_dict_col[0]
			#rows = self.list_data[len(self.list_data) - 1]
			def_sys_bp = rows['sys_bp']
			def_dia_bp = rows['dia_bp']
			def_pulse = rows['pulse']
			def_weight = rows['weight']




		list_input_row = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="수축혈압", name="sys_bp", id="input_sys_bp", row_type="left", type="input",def_value = def_sys_bp),
			row_dict(title="이완혈압", name="dia_bp", id="input_dia_bp", row_type="right", type="input",def_value = def_dia_bp),
			row_dict(title="맥박", name="pulse", id="input_pulse", row_type="left", type="input",def_value = def_pulse),
			row_dict(title="체중", name="weight", id="input_weight", row_type="right", type="input",def_value = def_weight),
			row_dict(title="status", name="status", id="input_status", row_type="right", type="hidden"),
			row_dict(title="type", name="type", id="input_type", row_type="right", type="hidden",def_value = "BP"),
			row_dict(title="param", name="param", id="input_param", row_type="right", type="hidden"),

		]
		#return

		list_attr = [dict(key="data-toggle",val="modal"),
		             dict(key="data-target", val="#id_modal_input"),
		             ]
		list_attr_ext = [dict(key="onclick", proc=lambda item:"edit_content('{cur_uid}')".format(cur_uid=item['cur_uid']))]
		text_ext = lambda item: item['title']

		this_table = dict(title="전체리스트",
				form_title="title",

			     list_input_row=list_input_row,
			     list_col_info=[
				     dict(title="제목", type="btn_ext", onclick="edit_content",href_key="link", title_key="title",
				          list_attr=list_attr,
				          list_attr_ext=list_attr_ext,
				          text_ext=lambda
					          item: item['title'],

				          ),
				     dict(title="날짜", type="title",  title_key="updt_date"),
				     dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
			     ],
			     list_data=self.list_data)

		self.list_tables[0].update(this_table)
		neoutil.simple_view_list(self.list_data)
		pass
	def excute_templete(self,fmt):
		sql = ''
		print("excute_templete")

		sql = fmt.format(**self.data.get_dict())
		print("excute_templete",sql)
		self.cur.execute(sql)

	def update_from_db(self):
		self.list_data =[]
		if not neoutil.get_safe_mapvalue(session, tag_login, False):
			return

		type = neoutil.get_safe_mapvalue(request.values, "type", "")
		sql = self.fmt_list.format(extra_condition="")
		if type == "":
			sql += " limit 10"
			self.extra_condition = "and status != 'HIDDEN' "
		elif type == "all":
			self.extra_condition = ""

		print("sql", sql)
		self.cur.execute(sql)
		self.list_data = self.cur.fetchall()
		#print(self.list_data)

	def ready_extra_condition(self):


		pass
class TestWebApp(WebtoonWebApp):
	pass


class LogOut(WebAppBase):
	def main_process(self):
		self.end_session()

		print("LogOut main_process",session)
		return redirect("/main.neo")


class LogIn(BaseDBWebApp):
	def init(self):
		WebAppBase.init(self)


		self.map_hint = {
			"second_sister": "0331",
			"first_sister": "1219",
			"dad": "0124",
			"mom": "1011",
			"me": "0815",
			"sewol_sadday": "0416",
		}


	def update_from_db(self):
		pass
	def comm_confirm(self,user_info,calc_hash,hash_passwd):

		print('calc_hash', tohexstr(calc_hash))
		print('hash_passwd', hash_passwd)
		if calc_hash != tobytes(hash_passwd):
			raise Exception("password is not match")
		redirect = neoutil.get_safe_mapvalue(session, tag_redirect, "/main.neo")
		session[tag_login] = True
		session[tag_user] = user_info.name
		session[tag_time] = time.time()
		# redirect = session[tag_redirect]

		#session[tag_redirect] = "/main.neo"
		return dict(result="ok", redirect=redirect)

	def log_in(self):
		print("log_in data", self.data.id,self.data.hash_passwd)
		list_user_info = self.select("""SELECT seq, usr_uid, id, fb_userid, name, pwd, rn, rn_srv, etc_info 
					FROM neo_pwinfo.user where id='{id}';""".format(id=self.data.id))




		print(tag_redirect, redirect)
		if len(list_user_info) ==0:
			raise Exception("user is not in db")
		user_info = neoutil.Struct(**list_user_info[0])
		print("hash", tohexstr(crypto_util_bin.sha256('tofhdna1pwd'.encode())))
		print("hash pwd", user_info.pwd)

		pwd = user_info.pwd
		print("input_hash",tohexstr(self.server_random+ tobytes(pwd)))
		calc_hash = crypto_util_bin.sha256(self.server_random+ tobytes(pwd))
		return self.comm_confirm(user_info,calc_hash,self.data.hash_passwd)
		# print('calc_hash',tohexstr(calc_hash))
		# print('hash_passwd', self.data.hash_passwd)
		# if calc_hash != tobytes(self.data.hash_hint_passwd):
		# 	raise Exception("password hit is not match")
		#
		#
		#
		#
		# session[tag_login] = True
		# session[tag_user] = user_info.name
		# session[tag_time] = time.time()
		# #redirect = session[tag_redirect]
		#
		#
		# #session[tag_redirect] = "/main.neo"
		# return dict(result="ok",redirect=redirect)
	def log_in_facebook(self):
		print("log_in_facebook data", self.data.fb_userid,self.data.hash_hint_passwd)
		list_user_info = self.select("""SELECT seq, usr_uid, id, fb_userid, name, pwd, rn, rn_srv, etc_info 
					FROM neo_pwinfo.user where fb_userid='{fb_userid}';""".format(fb_userid=self.data.fb_userid))
		redirect = neoutil.get_safe_mapvalue(session, tag_redirect, "/main.neo")
		print(tag_redirect, redirect)
		if len(list_user_info) ==0:
			raise Exception("user is not in db")
		value = self.map_hint[self.pre_key]
		user_info = neoutil.Struct(**list_user_info[0])

		calc_hash = crypto_util_bin.sha256(self.server_random+ value.encode())
		print('calc_hash',tohexstr(calc_hash))
		print('hash_hint_passwd', self.data.hash_hint_passwd)
		return self.comm_confirm(user_info, calc_hash, self.data.hash_hint_passwd)

	def start_log_in_telegram(self):
		telebot_inst: NeoChatBot
		telebot_inst = self.global_args.get("telebot_inst",None)
		if telebot_inst == None:
			raise Exception("telebot_inst is None")

		session_no = tohexstr(crypto_util_bin.getrandom(16))
		session[tag_session_no]  = session_no


		telebot_inst.start_auth(session_no)

		return dict(result="ok")

	def check_log_in_telegram(self):
		telebot_inst: NeoChatBot
		telebot_inst = self.global_args.get("telebot_inst", None)

		if telebot_inst == None:
			raise Exception("telebot_inst is None")

		session_no = session.get(tag_session_no,"")
		auth_info = telebot_inst.auth_info

		if auth_info == None:
			raise Exception(f"auth is not excute")

		session_status = auth_info["session_status"]
		auth = auth_info["auth"]
		tele_session_no = auth_info["session_no"]

		if tele_session_no != session_no:
			raise Exception(f"session_no:{session_no} is diffrent from  {tele_session_no}")

		if session_status != "done" or not auth_info["auth"]:
			raise Exception(f"session_no:{session_no} session_status:{session_status} and auth:{auth}")

		auth_info["session_status"] = "init"
		session[tag_session_no] = ""
		calc_hash = crypto_util_bin.sha256(b'111')
		print('calc_hash',tohexstr(calc_hash))
		user_info = neoutil.Struct()
		user_info.name = "신원석"
		return self.comm_confirm(user_info, calc_hash, calc_hash)


	def do_run(self):
		print("do_run")
		idx_a = random.randint(0,len(self.map_hint)-1)
		self.pre_key = list(self.map_hint.keys())[idx_a]
		self.server_random = crypto_util_bin.getrandom(32)
		self.hexstr_server_random = tohexstr(self.server_random)
		pass
	# def main_process(self):
	# 	session[tag_login] = False
	# 	print("LogOut main_process",session)
	# 	return redirect("/")


def get_lists(dir_path):

	list_new_content = json.load(open(dir_path+'/rsc/webinfo.json'))
	val_global = globals()
	list_map_from_json =[  val_global[tmp['class_name']](**tmp) for tmp in list_new_content]
	list_general_map =  [
		WebAppBase(name="main",title="신원석 홈페이지",
		           description ='이 홈페이지는 신원석(neo1seok)의 집에 있는 라즈베리파이의 아파치 서버위에서 돌아가고 있습니다..'),


		LogIn(name="login",title="로그인"),
		LogOut(name="logout",title="로그아웃")
	]
	for idx,val in enumerate( list_map_from_json):
		list_general_map.insert(1+idx,val)
	map_general_map = collections.OrderedDict( [(tmp.name,tmp) for tmp in list_general_map])
# map_general_map = dict(
# 	main=MainWebApp(name="main",description ='이 홈페이지는 신원석(neo1seok)의 집에 있는 라즈베리파이의 아파치 서버위에서 돌아가고 있습니다..'),
# 	test_jinja=MainWebApp( name="test_jinja",description ="테스트 진자" )
#
# )
	navigation = [  dict(id=val.id, title=val.title, href=val.href,type=val.type) for val in list_general_map if val.name != "main"]
	for inst in map_general_map.values():
		inst.navigation_org = navigation
	return map_general_map
#navigation.append(dict(id="nav_signup", title="signup", href="/signup"),)

#
# for tmp in list_general_map:
# 	if not hasattr(tmp,"uid_prefix"):
# 		continue
# 	list_aaa = [tmp.name,tmp.title,tmp.uid_prefix,tmp.table_name,tmp.href,tmp.description]
# 	print("\t".join(list_aaa))
'''
table_name = ""
	uid_prefix = ""
'''
#inst = globals()['WebtoonWebApp']
# inst(name="webtoon")