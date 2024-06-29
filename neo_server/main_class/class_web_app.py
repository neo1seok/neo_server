import datetime
import random
import urllib
import urllib.parse
from copy import deepcopy

import pymysql
import time
from flask import render_template, json, session, request
import collections,os
from neolib import neoutil,crypto_util_bin
from neolib.hexstr_util import *

from neo_server.main_class.class_web_app_base import *
#from neo_server.neo_telegram_bot.neo_chat_bot import NeoChatBot
from neo_server.parsing_class.show_naverweb import GetLateestWebtoon
from neo_server.parsing_class.show_portal_order import CheckPortalOrder


class SampleWebApp(BaseDBWebApp):
	pass



class FavLinkDBWebApp(BaseDBWebApp):
	def ready_extra_condition(self):
		type= neoutil.get_safe_mapvalue(request.values,"type","main")
		self.fav_type = type
		print("FavLinkDBWebApp ready_extra_condition",type)

		self.extra_condition = "and type = '{type}'".format(type=type.upper())
		print("extra_condition",self.extra_condition)

		pass
	def post_process(self):


		list_input_row = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(name="type", id="input_type", type='hidden' ,val= self.fav_type),
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
		                        id_new_input_button="id_new_input_button_hd",

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
	def init(self):
		BaseDBWebApp.init(self)

		self.list_tables.append(deepcopy(self.list_tables[0]))
	def __get_last_value(self, type):
		extra_condition = "and type = '{}'".format(type)
		sql = self.fmt_last_contents.format(table_name=self.table_name,extra_condition=extra_condition)

		list_dict_col = self.select(sql)
		if list_dict_col == None:
			return []

		return list_dict_col
	def __get_list(self,type,app_type,is_login=True):


		extra_condition = "and type = '{}'".format(type)

		if not is_login:
			onehourbefore = datetime.datetime.now() - datetime.timedelta(hours=1)
			extra_condition += f" and reg_date > '{onehourbefore:%Y-%m-%d %H:%M:%S}'"
		sql = self.fmt_list.format(extra_condition=extra_condition)
		if app_type == "":
			sql += " limit 10"

		return self.select(sql)
	def post_process(self):

		def_sys_bp = ""
		def_dia_bp = ""
		def_pulse = ""
		def_weight = ""
		def_comment = ""
		last_seq, last_uid = self.get_last_uid()

		list_dict_col = self.__get_last_value("BP")
		list_dict_col_wt = self.__get_last_value("WT")
		print(list_dict_col)
		if len(list_dict_col)>0:
			rows = list_dict_col[0]
			#rows = self.list_data[len(self.list_data) - 1]
			def_sys_bp = rows['sys_bp']
			def_dia_bp = rows['dia_bp']
			def_pulse = rows['pulse']
			def_comment = rows['comment']


		if len(list_dict_col_wt)>0:
			rows = list_dict_col_wt[0]
			def_weight = rows['weight']
			def_comment = rows['comment']

		def row_input_function(table,row):
			return f"<td> 날짜 </td><td> <p id='{row['id']}' >  </p></td>"

		def row_input_set_value_function(table,row,option):
			text = "''" if option =="init" else "response.dt+' '+response.week"


			return f"$('#{row['id']}').text({text});"

		def edit_function_btn(table,item,  col):
			table = neoutil.Struct(**table)
			item = neoutil.Struct(**item)
			col = neoutil.Struct(**col)
			value = getattr(item,col.title_key)



			return f"<button class='w3-btn w3-ripple '  data-toggle='modal' data-target='#{table.modal_id}' onclick=\"{col.onclick}('{item.cur_uid}')\">&#9998;{value}</button>"

		def date_function(table,item, col):
			return f"<p> {item['reg_date']:%m/%d}({item['week']}) {item['reg_date']:%H:%M}</p>"

		dict_select =dict(key="onfocus",val="this.select();")


		list_input_row = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="수축혈압", name="sys_bp", id="input_sys_bp", row_type="left", type="input",
			 list_attr = [dict_select],input_type="number",def_value = def_sys_bp),
			row_dict(title="이완혈압", name="dia_bp", id="input_dia_bp", row_type="right", type="input",
			list_attr = [dict_select],input_type="number",def_value = def_dia_bp),
			row_dict(title="맥박", name="pulse", id="input_pulse", row_type="left", type="input",
			         list_attr=[dict_select],input_type="number",def_value = def_pulse),
			row_dict(title="체중", name="weight", id="input_weight", row_type="right", type="hidden",def_value = "0"),
			row_dict(title="커맨트", name="comment", id="input_comment", row_type="all", type="text",rows=2),
			row_dict(title="status", name="status", id="input_status", row_type="right", type="hidden"),
			row_dict(title="type", name="type", id="input_type", row_type="right", type="hidden",def_value = "BP"),
			row_dict(title="param", name="param", id="input_param", row_type="right", type="hidden"),
			row_dict(name="등록날짜", id="input_dynamic", type='dynamic',ext_set_value_function = row_input_set_value_function ,ext_function = row_input_function),

		]
		list_input_row_weight = [
			row_dict(title="수축혈압", name="sys_bp", id="input_sys_bp_wt", row_type="left", type="hidden",def_value = "0"	),
			row_dict(title="이완혈압", name="dia_bp", id="input_dia_bp_wt", row_type="right", type="hidden",def_value = "0"),
			row_dict(title="맥박", name="pulse", id="input_pulse_wt", row_type="left", type="hidden",def_value = "0"),
			row_dict(name="cur_uid", id="input_cur_uid_wt", type='hidden'),
			row_dict(title="체중", name="weight", id="input_weight_wt", row_type="right", type="input",
			         input_type="number",list_attr=[dict(key="step",val="0.01" ),dict_select],
			         def_value=def_weight),
			row_dict(title="커맨트", name="comment", id="input_comment_wt", row_type="all", type="text" ,rows=2),
			row_dict(title="status", name="status", id="input_status_wt", row_type="right", type="hidden"),
			row_dict(title="type", name="type", id="input_type_wt", row_type="right", type="hidden", def_value="WT"),
			row_dict(title="param", name="param", id="input_param_wt", row_type="right", type="hidden"),
			row_dict(name="등록날짜", id="input_dynamic_wt", type='dynamic', ext_set_value_function = row_input_set_value_function ,ext_function = row_input_function),

		]
		#return

		list_attr = [dict(key="data-toggle",val="modal"),
		             dict(key="data-target", val="#id_modal_input"),
		             ]
		list_attr_ext = [dict(key="onclick", proc=lambda item:"edit_content('{cur_uid}')".format(cur_uid=item['cur_uid']))]
		text_ext = lambda item: item['title']



		this_table = dict(title="혈압리스트",

		          new_input_button="혈압입력",
		                  form_title="혈압입력",
		                  id_new_input_button="id_new_input_bp",
			     list_input_row=list_input_row,
			     list_col_info=[
				     #dict(title="편집", type="btn", onclick="edit_content"),
				     dict(title="혈압", type="dynamic",title_key="bp", onclick="edit_content",ext_function=edit_function_btn),

				    # dict(title="혈압", type="title", title_key="bp"),
				     #dict(title="날짜", type="title",  title_key="dt"),

				     dict(title="날짜", type="dynamic", ext_function=date_function),

			     ],
			     list_data=self.list_data)
		this_table_weight = 		dict(title="체중",
			     modal_id="id_modal_input_wt",
			     form_id="form_input_wt",
			     form_title="채중입력",
			     id_div_list="div_list_wt",
			     new_input_button="채중입력",
			     id_new_input_button="id_new_input_wt",
			     button_id="",
			     enable_function="enable_input_wt",
			     input_class="neo_form_wt",
			     edit_function="edit_content_wt",
			     delete_function="delete_content_wt",
			     new_input_function="new_input_function_wt",

			     query_option="",

			     list_input_row=list_input_row_weight,
			     list_data=self.list_data_wt,
			                            list_col_info=[
				                            #dict(title="편집", type="btn", onclick="edit_content_wt"),
				                            dict(title="체중",title_key="weight", type="dynamic", onclick="edit_content_wt",
				                                 ext_function=edit_function_btn),
				                            #dict(title="체중", type="title", title_key="weight"),
				                            #dict(title="날짜", type="title", title_key="dt"),
				                            dict(title="날짜", type="dynamic", ext_function= date_function),
				                            #  dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
			                            ],
		                                )



		self.list_tables[0].update(this_table)


		self.list_tables[1] = this_table_weight
		print()
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
		self.list_data_wt =[]

		self.type = neoutil.get_safe_mapvalue(request.values, "type", "")
		self.open_type = neoutil.get_safe_mapvalue(request.values, "open", "")
		is_login = neoutil.get_safe_mapvalue(session, tag_login, False)
		# if not neoutil.get_safe_mapvalue(session, tag_login, False):
		# 	return





		print("self.open_type",self.open_type,is_login)
		self.list_data = self.__get_list("BP",self.type,is_login)
		self.list_data_wt =self.__get_list("WT",self.type,is_login)

		#print(self.list_data)

	def ready_extra_condition(self):


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

	def set_redirect_for_login(self):
		pass

	def update_from_db(self):
		pass
	def comm_confirm(self,user_info,calc_hash,hash_passwd):

		print('calc_hash', tohexstr(calc_hash))
		print('hash_passwd', hash_passwd)
		if calc_hash != tobytes(hash_passwd):
			raise Exception("password is not match")
		#session:dict

		redirect = neoutil.get_safe_mapvalue(session, tag_redirect, "/main.neo")
		session[tag_login] = True
		session[tag_user] = user_info.name
		session[tag_time] = time.time()
		# redirect = session[tag_redirect]
		#session[tag_redirect] = "/main.neo"
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

		print("server random", tohexstr(self.server_random))

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

	# def start_log_in_telegram(self):
	# 	telebot_inst: NeoChatBot
	# 	telebot_inst = self.global_args.get("telebot_inst",None)
	# 	if telebot_inst == None:
	# 		raise Exception("telebot_inst is None")
	#
	# 	session_no = tohexstr(crypto_util_bin.getrandom(16))
	# 	session[tag_session_no]  = session_no
	#
	#
	# 	telebot_inst.start_auth(session_no)
	#
	# 	return dict(result="ok")
	#
	# def check_log_in_telegram(self):
	# 	telebot_inst: NeoChatBot
	# 	telebot_inst = self.global_args.get("telebot_inst", None)
	#
	# 	if telebot_inst == None:
	# 		raise Exception("telebot_inst is None")
	#
	# 	session_no = session.get(tag_session_no,"")
	# 	auth_info = telebot_inst.auth_info
	#
	# 	if auth_info == None:
	# 		raise Exception(f"auth is not excute")
	#
	# 	session_status = auth_info["session_status"]
	# 	auth = auth_info["auth"]
	# 	tele_session_no = auth_info["session_no"]
	#
	# 	if tele_session_no != session_no:
	# 		raise Exception(f"session_no:{session_no} is diffrent from  {tele_session_no}")
	#
	# 	if session_status != "done" or not auth_info["auth"]:
	# 		raise Exception(f"session_no:{session_no} session_status:{session_status} and auth:{auth}")
	#
	# 	auth_info["session_status"] = "init"
	# 	session[tag_session_no] = ""
	# 	calc_hash = crypto_util_bin.sha256(b'111')
	# 	print('calc_hash',tohexstr(calc_hash))
	# 	user_info = neoutil.Struct()
	# 	user_info.name = "신원석"
	# 	return self.comm_confirm(user_info, calc_hash, calc_hash)


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