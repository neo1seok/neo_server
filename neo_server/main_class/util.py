import datetime
import pickle
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

from neo_server.main_class.class_web_app import *
from neo_server.main_class.class_web_app_base import *
from neo_server.main_class.keyword_order_web_app import KeywordOrderWebApp
from neo_server.main_class.webtoon_web_app import WebtoonWebApp
from neo_server.neo_telegram_bot.neo_chat_bot import NeoChatBot
from neo_server.parsing_class.show_naverweb import GetLateestWebtoon
from neo_server.parsing_class.show_portal_order import CheckPortalOrder


def get_lists(dir_path):
	WebtoonWebApp,KeywordOrderWebApp

	list_new_content = json.load(open(dir_path+'/rsc/webinfo.json'))
	val_global = globals()
	list_map_from_json =[  val_global[tmp['class_name']](**tmp) for tmp in list_new_content]
	list_general_map =  [
		WebAppBase(name="main",title="신원석 홈페이지",
		           description ='이 홈페이지는 신원석(neo1seok)의 집에 있는 라즈베리파이의 아파치 서버위에서 돌아가고 있습니다..'),


		LogIn(name="login",title="로그인",type='login'),
		LogOut(name="logout",title="로그아웃",type='logout')
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

def get_webtoon_json(dir_path):

	webtoon_info_file = os.path.join(dir_path,"temp", "webtoon_info.json")
	if not os.path.exists(webtoon_info_file):
		temp_dir = os.path.dirname(webtoon_info_file)
		neoutil.MakeDir(temp_dir)
		pickle.dump({},open(webtoon_info_file,"wb"))


	return webtoon_info_file
