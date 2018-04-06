
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