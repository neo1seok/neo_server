
from flask import render_template, json, session, request
from werkzeug.utils import redirect

import random

import pymysql
import time
from flask import render_template, json, session, request
import collections,os
from neolib import neoutil,crypto_util_bin
from neolib.hexstr_util import *




tag_login = "login"
tag_user = "user"
tag_time ="log_in_time"
tag_redirect = "redirect"
tag_session_no = "session_no"


def row_dict(**kwargs):
	# if "dev_value" in kwargs:
	# 	kwargs["dev_value"] = ""
	return dict(**kwargs)


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
		self.href = "/" + self.name+".neo"
		self.id = self.name
		self.temp_file = self.name + ".html"
		self.column_names =""
		self.type =""
		self.navigation_org =[]
		print(kwargs)
		not_empty_map ={ key:val for key,val in kwargs.items() if val !=""}
		self.__dict__.update(not_empty_map)

		self.global_args = dict()

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
		for value in request.values:
			print("value",value)

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

		type = neoutil.get_safe_mapvalue(request.values, "type", "")
		print("type",type)
		if not self.is_login() and (self.type =="private" or type =="private") :
			return self.direct_login()

		session[tag_time] = time.time()
		user = neoutil.get_safe_mapvalue(session, tag_user,"")
		self.user_description = "{}님 반갑습니다.".format(user) if user !="" else ""
		self.init_run()
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


	def update_params(self,**kwargs):
		# self.navigation =navigation
		# print("navigation",self.navigation)
		self.global_args = kwargs
		mysql = kwargs.get("mysql")
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


		print(self.__class__.__name__,"do_query", dict(data))
		for key,value in data.items():
			print(key,value)

		self.data.from_dict(self.__dict__)

		self.post_data = neoutil.Struct(**data)
		self.data.from_dict({ key:value for key,value in data.items()})
		self.cmd = cmd
		print("do_query", self.cmd,self.post_data.get_dict())
		ret = "NOT ASSIGN"
		self.map_ret = dict(result="ok")
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


	def init_run(self):
		pass


class BaseDBWebApp(WebAppBase):
	sql = '''SELECT id, name,updt_date FROM neo_pwinfo.user;
'''
	fmt_last_seq = "SELECT max(seq) as last_seq FROM neo_pwinfo.{table_name};"
	fmt_delete = """delete from neo_pwinfo.{table_name} WHERE  {uid_prefix}_uid  = '{cur_uid}'"""
	fmt_hide = """UPDATE neo_pwinfo.{table_name}
				SET status = 'HIDDEN'  
                WHERE  {uid_prefix}_uid  = '{cur_uid}'"""
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
	def get_last_uid(self):
		ret = self.select("SELECT max(seq) as last_seq FROM neo_pwinfo.{table_name};".format(**self.data.get_dict()))
		if ret[0]['last_seq'] == None:
			last_seq =0
		else:
			print(ret[0]['last_seq'])
			last_seq = int(ret[0]['last_seq'])
		return last_seq,"{}_{}".format(self.uid_prefix,last_seq)

	def get_next_uid(self):
		last_seq,last_uid = self.get_last_uid()
		return last_seq+1,"{}_{}".format(self.uid_prefix,last_seq+1)

	def select(self, sql):
		try:
			self.cur.execute(sql)
		except Exception as ext:
			print(sql)
			raise ext
		return self.cur.fetchall()

	def ready_extra_condition(self):
		fmt_repl = "and site regexp '{keyword}'"

		type = neoutil.get_safe_mapvalue(request.values, "type", "")


		if type == "":
			self.extra_condition = "and status != 'HIDDEN' "
		elif type == "all":
			self.extra_condition = ""

		pass

	def update_from_db(self):

		sql = self.fmt_list.format(extra_condition=self.extra_condition)
		print("extra_condition",self.extra_condition)
		print("sql", sql)
		self.cur.execute(sql)
		self.list_data = self.cur.fetchall()
		#print(self.list_data)

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
			response['result'] = "ok"
			return response
		except Exception as ex:
			return dict(error=str(ex))

	def excute_templete(self,fmt):
		sql = ''
		print("excute_templete")
		if not neoutil.get_safe_mapvalue(session, tag_login, False):
			raise Exception("not login ")
			return dict(result="fail", error="not login ")
		sql = fmt.format(**self.data.get_dict())
		print("excute_templete",sql)
		self.cur.execute(sql)

	def update(self):
		# sql = ''
		# if not neoutil.get_safe_mapvalue(session, tag_login, False):
		# 	return dict(result="fail",error="not login ")
		input_uid = self.data.cur_uid
		if input_uid == '':
			last_seq, last_uid = self.get_next_uid()
			self.data.last_seq = last_seq
			self.data.last_uid = last_uid
			fmt = self.fmt_insert
		else :
			fmt = self.fmt_udpate
		self.excute_templete(fmt)
		# sql = fmt.format(**self.data.get_dict())
		#
		# print(sql)
		# self.cur.execute(sql)

	def delete(self):
		print("delete cur_uid", self.data.cur_uid)
		self.excute_templete(self.fmt_delete)
		# print("delete cur_uid", self.data.cur_uid)
		# if not neoutil.get_safe_mapvalue(session, tag_login, False):
		# 	return dict(result="fail",error="not login ")
		#
		# sql = self.fmt_delete.format(**self.data.get_dict())
		# print(sql)
		# self.cur.execute(sql)
		pass

	def hide(self):
		print("hide cur_uid", self.data.cur_uid)
		self.excute_templete(self.fmt_hide)
		# print("hide cur_uid", self.data.cur_uid)
		# if not neoutil.get_safe_mapvalue(session, tag_login, False):
		# 	return dict(result="fail", error="not login ")
		#
		# fmt_hide
		# pass