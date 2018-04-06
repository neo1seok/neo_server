import random

import pymysql
import time
from flask import render_template, json, session, request
import collections
from neolib import neoutil,crypto_util_bin
from neolib.hexstr_util import *
from werkzeug.utils import redirect

import tool_xls_to_json

tag_login = "login"
tag_user = "user"
tag_time ="log_in_time"
tag_redirect = "redirect"
class WebAppBase():
	name:str
	class_name:str
	title:str
	href:str
	uid_prefix:str
	table_name:str
	description:str
	column_names:str
	fmt_list:str
	fmt_udpate:str
	fmt_insert:str
	fmt_delete:str

	def __init__(self,**kwargs):


		#self.temp_file = kwargs['temp_file']
		self.name = kwargs["name"]
		if "name" not in kwargs:
			raise Exception("")
		self.title =self.name
		self.table_name = self.name
		self.description =  self.name
		self.href = "/" + self.name
		self.id = self.name
		self.temp_file = self.name + ".html"
		self.column_names =""
		self.type =""
		self.navigation_org =[]
		print(kwargs)
		not_empty_map ={ key:val for key,val in kwargs.items() if val !=""}
		self.__dict__.update(not_empty_map)



		self.data = neoutil.Struct(**self.__dict__)
		#print(self.data.get_dict())

		# self.href = "/" + self.name
		# self.id = "navid_" + self.name
		# self.temp_file = self.name +".html"
		#print(self.__dict__)
		#self.navigation = []
		#self.param_dict  = kwargs
		self.init()
	def init(self):

		pass
	def end_session(self):
		session[tag_login] = False
		session[tag_user] = ""
		session[tag_time] = 0
		pass
	def start_session(self,user_mame):

		session[tag_login] = True
		session[tag_user] = user_mame
		session[tag_time] = time.time()
	def main_process(self):
		print("main_process session", session)
		print("main_process", self.__class__.__name__, self.name)
		log_time = neoutil.get_safe_mapvalue(session, tag_time, time.time())
		if log_time == None:
			log_time =0

		tk_time = time.time() -log_time
		print(tk_time)
		if tk_time > 60*60:
			self.end_session()
		self.navigation = self.navigation_org
		if not self.is_login():
			self.navigation = [tmp for tmp in self.navigation_org if tmp['type'] != "private"]

		# neoutil.get_safe_mapvalue(session, tag_login, False)

		if not self.is_login() and self.type =="private":
			return self.direct_login()
		session[tag_time] = time.time()
		user = neoutil.get_safe_mapvalue(session, tag_user,"")
		self.user_description = "{}님 반갑습니다.".format(user) if user !="" else ""
		self.do_run()


		print("user_description",self.user_description)
		return self.render()
	def do_run(self):
		pass
	def get_template(self):
		return self.temp_file

	def get_dict_params(self):
		return self.param_dict

	def render(self):
		print("render",self.temp_file)
		ret_render = render_template(self.temp_file, **self.__dict__)
		#print("ret_render",ret_render)
		return ret_render


	def update_params(self,mysql):
		# self.navigation =navigation
		# print("navigation",self.navigation)
		conn = mysql.connect()
		self.cur = conn.cursor(pymysql.cursors.DictCursor)
		return self




	def direct_login(self):

		session[tag_redirect]=self.href
		ret = redirect("/login")
		print(tag_redirect,ret)

		return ret

	def is_login(self):
		return neoutil.get_safe_mapvalue(session, tag_login, False)
		return True

	def do_query(self,cmd,data):


		print("do_query", dict(data))
		for key,value in data.items():
			print(key,value)
		#print({ key:value for key,value in data.items()})
		#self.__dict__.update(**{ key:value for key,value in data.items()})
		self.data.from_dict(self.__dict__)
		# uid_prefix = neoutil.get_safe_mapvalue(self.__dict__,"uid_prefix","")
		# self.data = neoutil.Struct(uid_prefix = uid_prefix)
		self.post_data = neoutil.Struct(**data)
		self.data.from_dict({ key:value for key,value in data.items()})
		self.cmd = cmd
		print("do_query", self.cmd,self.post_data.get_dict())
		ret = "NOT ASSIGN"
		self.map_ret = dict(result="OK")
		try:
			print("self.cmd",self.cmd)
			print(self.__dict__)

			process_query = getattr(self,self.cmd)
			ret =process_query()
			#self.map_cmd[self.cmd]()
			if ret != None:
				self.map_ret.update(**ret)
		except Exception as ext:
			print(ext)
			self.map_ret = dict(result = "FAIL",error = str(ext))
			pass
		print(ret)

		return json.dumps(self.map_ret)
	def get_content(self):
		print("id",self.data.id)
		return dict(state='adasffsadf')

	def update(self):
		print("update id", self.id)
		#//return json.dumps(dict(state='update'))
	def delete(self):
		print("delete id", self.id)
		pass


class BaseDBWebApp(WebAppBase):
	sql = '''SELECT id, name,updt_date FROM neo_pwinfo.user;
'''
	fmt_last_seq = "SELECT max(seq) as last_seq FROM neo_pwinfo.{table_name};"
	fmt_delete = """delete from neo_pwinfo.{table_name} WHERE  {uid_prefix}_uid  = '{cur_uid}'"""
	fmt_cond_get_contents = "and {uid_prefix}_uid = '{cur_uid}'"
	list_col_name = ["제목", "날짜"]

	uid_prefix = ""


	def init(self):

		self.list_col_name = self.column_names.split("|")
		self.list_tables = [
			dict(title="title",
			     modal_id="id_modal_input",
			     form_id="form_input",
			     form_title="title",
			     id_div_list ="div_list",
				new_input_button ="새 글쓰기",
			     button_id="",
			     enable_function="enable_input",
				 input_class ="neo_form",
			     edit_function="edit_content",
			     delete_function="delete_content",
			     new_input_function="new_input_function",
			     query_option="",

			     list_input_row=[],
			     list_data=[],
			     list_col_info=[  ])
		 ]
		#print("list_col_name",self.list_col_name)

		pass

	def do_run(self):
		self.ready_extra_condition()
		self.update_from_db()
		self.post_process()

	def get_next_uid(self):
		ret = self.select("SELECT max(seq) as last_seq FROM neo_pwinfo.{table_name};".format(**self.data.get_dict()))
		last_seq = int(ret[0]['last_seq'])+1
		return last_seq,"{}_{}".format(self.uid_prefix,last_seq)

	def select(self, sql):
		self.cur.execute(sql)
		return self.cur.fetchall()

	def ready_extra_condition(self):
		self.extra_condition = ""
		pass

	def update_from_db(self):

		sql = self.fmt_list.format(extra_condition=self.extra_condition)
		print(self.extra_condition)
		self.cur.execute(sql)
		self.list_data = self.cur.fetchall()
		print(self.list_data)

		pass

	def post_process(self):
		pass

	def get_content(self):
		print("get_content id", self.data.cur_uid)
		try:
			extra_condition = self.fmt_cond_get_contents.format(**self.data.get_dict())
			sql = self.fmt_list.format(extra_condition=extra_condition)
			#sql = sql.format( wtn_uid = self.data.wtn_uid)
			print(sql)
			self.cur.execute(sql)
			list_map =self.cur.fetchall()
			response = list_map[0]
			response['result'] = "OK"
			return response
		except Exception as ex:
			return dict(error=str(ex))

	def update(self):
		sql = ''
		if not neoutil.get_safe_mapvalue(session, tag_login, False):
			return dict(result="fail",error="not login ")
		input_uid = self.data.cur_uid
		if input_uid == '':
			last_seq, last_uid = self.get_next_uid()
			self.data.last_seq = last_seq
			self.data.last_uid = last_uid
			fmt = self.fmt_insert
		else :
			fmt = self.fmt_udpate

		sql = fmt.format(**self.data.get_dict())

		print(sql)
		self.cur.execute(sql)

	def delete(self):
		print("delete cur_uid", self.data.cur_uid)
		if not neoutil.get_safe_mapvalue(session, tag_login, False):
			return dict(result="fail",error="not login ")

		sql = self.fmt_delete.format(**self.data.get_dict())
		print(sql)
		self.cur.execute(sql)
		pass

class SampleWebApp(BaseDBWebApp):
	pass



class WebtoonWebApp(BaseDBWebApp):

	def ready_extra_condition(self):
		import time
		now = time.localtime()

		week = ['월', '화', '수', '목', '금', '토', '일']
		date_name = week[now.tm_wday]
		print('오늘 요일: %s요일' % date_name)
		self.extra_condition = "and dates regexp '%s'" % date_name

		pass
	def post_process(self):
		sql = """
				SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
				"""
		list_portals = self.select(sql)

		for map_line in self.list_data:

			map_line['list_url'] =map_line['list_url'].format(map_line['id'])
			map_line['detail_url'] = map_line['detail_url'].format(map_line['id'],map_line['lastno'])
			print("map_url", map_line['list_url'], map_line['detail_url'])




		list_input_row = [

			dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			dict(title="웹툰이름",name="title",id="input_title",row_type="all",type="input"),
			dict(title="웹툰아이디", name="id", id="input_id", row_type="left", type="input"),
			dict(title="요일",name="dates",id="input_dates",row_type="right",type="input"),
			dict(title="포탈", name="prt_uid", id="input_prt_uid",
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
	def post_process_old(self):
		for map_line in self.list_data:

			map_line['list_url'] =map_line['list_url'].format(map_line['id'])
			map_line['detail_url'] = map_line['detail_url'].format(map_line['id'],map_line['lastno'])
			print("map_url", map_line['list_url'], map_line['detail_url'])

		sql = """
		SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
		"""
		self. list_portals = self.select(sql)
		print(self.list_portals)
		pass

class FavLinkDBWebApp(BaseDBWebApp):
	def post_process(self):


		list_input_row = [

			dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			dict(title="제목", name="title", id="input_title", row_type="all", type="input"),
			dict(title="링크", name="link", id="input_link", row_type="all", type="input"),

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

			dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			dict(title="제목", name="title", id="input_title", row_type="all", type="input"),
			dict(title="이슈", name="issue", id="input_issue", row_type="all", type="text"),
			dict(title="솔루션", name="solution", id="input_solution", row_type="all", type="text"),

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

	def db_update(self, prt_uid, list_order):
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
		for order, keyword, url in list_order:
			sql = fmt_update.format(keyword, url, order, prt_uid)
			print(sql)
			self.cur.execute(sql)
			print(order, keyword, url)

	def update(self):
		print("update data",self.data)
		self.list_result = json.loads(self.data.json_list_result)


		sql = """
		SELECT prt_uid, main_url 	FROM neo_pwinfo.portal;
		"""
		# self.cur.execute(sql)
		# fmt_insert="({0},'kwo_{0}','{1}',{2},'{3}','{4}',now(),now())"
		# # 0: seq 1:prt_uid 2:order 3:keyword 4:url
		# list_potal =self.cur.fetchall()

		list_potal = 	self.select(sql)
		map_portal = { tmp['main_url']:neoutil.Struct(**tmp) for tmp in list_potal}

		for main_url,list_order in self.list_result:
			obj = map_portal[main_url]
			print(obj.prt_uid)
			self.db_format(obj.prt_uid,len(list_order))
			self.db_update(obj.prt_uid,list_order)


	pass

class PasswdWebApp(BaseDBWebApp):
	# def is_login(self):
	# 	print("is_login")
	# 	return neoutil.get_safe_mapvalue(session, tag_login, False)
	def ready_extra_condition(self):
		fmt_repl = "and site regexp '{keyword}';"
		print("PasswdWebApp",request.args)
		type= neoutil.get_safe_mapvalue(request.args,"type","")
		keyword = neoutil.get_safe_mapvalue(request.args, "keyword", "")
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

			dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			dict(title="site", name="site", id="input_site", row_type="left", type="input"),
			dict(title="header", name="phd_uid", id="input_header", row_type="right",
			     type="select",
			     list_options = [ dict(value=map_portal['phd_uid'], name=map_portal["title"]) for map_portal in self.list_header]),
			dict(title="ptail", name="ptail", id="input_ptail", row_type="left", type="input"),
			dict(title="id", name="ptail", id="input_id", row_type="right", type="input"),
			dict(title="etc", name="etc", id="input_etc", row_type="all", type="text"),

		]
		list_input_header = [

			dict(name="phd_uid", id="input_phd_uid", type='hidden'),
			dict(title="헤더이름", name="title", id="input_title_header", row_type="left", type="input"),
			dict(title="특수문자", name="special_letter", id="input_special_letter", row_type="right", type="input"),
			dict(title="힌트", name="hint", id="input_hint", row_type="all", type="input"),



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
			response['result'] = "OK"
			return response
			pass
		else:
			raise Exception("not allowd option")

		pass
class TestWebApp(BaseDBWebApp):
	def ready_extra_condition(self):
		import time
		now = time.localtime()

		week = ['월', '화', '수', '목', '금', '토', '일']
		date_name = week[now.tm_wday]
		print('오늘 요일: %s요일' % date_name)
		self.extra_condition = "and dates regexp '%s'" % date_name

		pass

	'''
	 <option  value="{{option.value}}">"{{option.name}}"</option>
	
	'''
	def post_process(self):
		sql = """
				SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
				"""
		list_portals = self.select(sql)

		for map_line in self.list_data:

			map_line['list_url'] =map_line['list_url'].format(map_line['id'])
			map_line['detail_url'] = map_line['detail_url'].format(map_line['id'],map_line['lastno'])
			print("map_url", map_line['list_url'], map_line['detail_url'])




		list_input_row = [

			dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			dict(title="웹툰이름",name="title",id="input_title",row_type="all",type="input"),
			dict(title="웹툰아이디", name="id", id="input_id", row_type="left", type="input"),
			dict(title="요일",name="dates",id="input_dates",row_type="right",type="input"),
			dict(title="포탈", name="prt_uid", id="input_prt_uid",
			row_type='all',type="select",
			list_options=[ dict(value=map_portal['prt_uid'],name=map_portal["title"]) for map_portal in list_portals])
		                  ]

		self.list_tables =[
			dict(title="talbe",
			     modal_id = "id_modal_input",
			     form_id="form_input", form_title="title",
			     button_id="",
			     check_box_id="id_check_box",
			     edit_function="edit_content",
			     new_input_function="new_input_function",

			     list_input_row=list_input_row,
			     list_col_info=[
				dict(title="제목",type="link",href_key="list_url",title_key="title"),
				dict(title="제목", type="link",href_key="detail_url",title_key= "today_title"),
				dict(title="편집", type="btn",onclick="edit_content"),
				dict(title="삭제", type="btn_no_modal",onclick="delete_content"),
			],
			     list_data = self.list_data)
		]
		neoutil.simple_view_list(self.list_data)
		pass
class LogOut(WebAppBase):
	def main_process(self):
		self.end_session()

		print("LogOut main_process",session)
		return redirect("/")
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
	def log_in_facebook(self):
		print("log_in_facebook data", self.data.fb_userid,self.data.hash_hint_passwd)
		list_user_info = self.select("""SELECT seq, usr_uid, id, fb_userid, name, pwd, rn, rn_srv, etc_info 
					FROM neo_pwinfo.user where fb_userid='{fb_userid}';""".format(fb_userid=self.data.fb_userid))
		redirect = neoutil.get_safe_mapvalue(session, tag_redirect, "/")
		print(tag_redirect, redirect)
		if len(list_user_info) ==0:
			raise Exception("user is not in db")
		value = self.map_hint[self.pre_key]

		calc_hash = crypto_util_bin.sha256(self.server_random+ self.map_hint[self.pre_key].encode())
		print('calc_hash',tohexstr(calc_hash))
		print('hash_hint_passwd', self.data.hash_hint_passwd)
		if calc_hash != tobytes(self.data.hash_hint_passwd):
			raise Exception("password hit is not match")


		user_info = neoutil.Struct(**list_user_info[0])

		session[tag_login] = True
		session[tag_user] = user_info.name
		session[tag_time] = time.time()
		#redirect = session[tag_redirect]


		session[tag_redirect] = "/"
		return dict(result="ok",redirect=redirect)

	def do_run(self):
		idx_a = random.randint(0,len(self.map_hint)-1)
		self.pre_key = list(self.map_hint.keys())[idx_a]
		self.server_random = crypto_util_bin.getrandom(32)
		self.hexstr_server_random = tohexstr(self.server_random)
		pass
	# def main_process(self):
	# 	session[tag_login] = False
	# 	print("LogOut main_process",session)
	# 	return redirect("/")


def get_lists():
	tool_xls_to_json.main()
	list_new_content = json.load(open('rsc/webinfo.json'))
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