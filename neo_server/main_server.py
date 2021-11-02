import datetime
import os
import sys

import requests
import yaml
from flask import Flask, request, render_template, url_for, Markup, json, session, send_from_directory
from flaskext.mysql import MySQL
from flask import jsonify
from werkzeug.security import generate_password_hash
import pymysql
from werkzeug.utils import redirect

from neo_server.main_class import class_web_app
from neo_server.main_class.util import get_lists, get_webtoon_json
from neo_server.main_value import dir_path, basedir
from neo_server.neo_telegram_bot.api_token import neo_bot_token, temptest_bot

#dir_path = os.path.dirname(os.path.realpath(__file__))
from neo_server.sample_data import sample_data

map_general_map = get_lists(dir_path)
webtoon_info_file = get_webtoon_json(dir_path)
#print(map_general_map)
app = Flask(__name__)
mysql = MySQL()

jinja_options = app.jinja_options.copy()
jinja_options.update(dict(
	block_start_string='<%',
	block_end_string='%>',
	variable_start_string='%%',
	variable_end_string='%%',
	comment_start_string='<#',
	comment_end_string='#>'
))
#app.jinja_options = jinja_options
#Name

# MySQL configurations



#basedir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(basedir,'config.yaml')
print("config.yaml",config_path)

with open(config_path) as f:
	conf = yaml.safe_load(f)
print(conf)

# app.config['MYSQL_DATABASE_USER'] = 'neo1seok'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'tofhdna1pi'
# app.config['MYSQL_DATABASE_DB'] = 'neo_pwinfo'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'

#app.config.__dict__.update(**conf)

# print(app.config['MYSQL_DATABASE_USER'])
# print(app.config['MYSQL_DATABASE_PASSWORD'])
# print(app.config['MYSQL_DATABASE_DB'])
# print(app.config['MYSQL_DATABASE_HOST'])
print()

app.config.update(**conf)


print(app.config['MYSQL_DATABASE_USER'])
print(app.config['MYSQL_DATABASE_PASSWORD'])
print(app.config['MYSQL_DATABASE_DB'])
print(app.config['MYSQL_DATABASE_HOST'])
print()

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


mysql.init_app(app)

telebot_inst = None

def get_main_inst(app_name):
	return map_general_map[app_name].update_params( mysql=mysql,telebot_inst=telebot_inst)
@app.route('/')
def main():
	url_for('static', filename='style.css')
	print("main")
	return get_main_inst('main') .main_process()


@app.route('/<app_name>.neo',methods=['GET','POST'])
def show_general_app(app_name=None):
	print("show_general_app",app_name)
	#url_for('static', filename='style.css')
	print("values",request.values)
	print("form", request.form)
	print("args", request.args)
	print("data", request.data)

	#print(url_for('static', filename='comm.js'))
	if app_name not in map_general_map:
		return "NO APP PAGE"
	inst = get_main_inst(app_name)
	print('is_login')
	# if not inst.is_login():
	# 	return inst.direct_login()
	return inst.main_process()


@app.route('/query/<app_name>/<cmd>',methods=['GET','POST'])
def query_app(app_name=None,cmd=None):
	print("query_app")

	print("values",request.values)
	print("form", request.form)
	print("args", request.args)
	print("data", request.data)
	# ret = map_general_map[app_name].update_params(navigation,mysql).do_query(request.form)
	# print("ret",ret)
	return get_main_inst(app_name).do_query(cmd,request.form)

@app.route('/health_rd.neo',methods=['GET'])
def health_redirect():
	dict_type = dict(wt='id_new_input_wt',bp='id_new_input_bp')
	return render_template("health_redirect.html")

@app.route('/recog.neo',methods=['GET','POST'])
def recog_attendance():
	print(request.method)
	if request.method == "POST":
		#data = dict()
		data =request.form.to_dict()

		#data= dict(request.form)

		print("values",data)
		print("form", request.form)
		print("args", request.args)
		print("data", request.data)
		curtime = data['curtime']
		curtime = datetime.datetime.fromtimestamp(float(curtime) / 1000)
		print(curtime,type(curtime))
		import time

		url = 'https://wh.jandi.com/connect-api/webhook/20747084/162ea949c087f8478edf2182cafeea7e'
		headers ={ "Accept": "application/vnd.tosslab.jandi-v2+json",
				"ContentType": "application/json",}

		try:
			ret = requests.post(url, json=dict(body=f'신원석(neo1seok) {curtime:%Y/%m/%d %H:%M:%S}'), headers=headers)
			print(ret.text, type(ret.text))

			result = dict(result="OK")

			result.update(**json.loads(ret.text))

		except Exception as ext:
			print(ext)
			result['result'] = "FAIL"
			result['error'] = str(ext)

			pass
		return json.dumps(result)

	dict_type = dict(datetime=datetime.datetime.now(),name='신원석(neo1seok)')
	return render_template("recog_attendance.html",**dict_type)

@app.route('/dia.neo',methods=['GET','POST'])
def dia_check():
	print(request.method)
	if request.method == "POST":
		#data = dict()
		data =request.form.to_dict()

		#data= dict(request.form)

		print("values",data)
		print("form", request.form)
		print("args", request.args)
		print("data", request.data)

		result = dict(result="OK")

		return json.dumps(result)

	dict_type = dict(datetime=datetime.datetime.now(),name='신원석(neo1seok)')
	return render_template("recog_attendance.html",**dict_type)

@app.route('/netflix.neo',methods=['GET'])
def netflix():
	dict_type = dict(wt='id_new_input_wt',bp='id_new_input_bp')
	list_genre = json.load(open(dir_path + '/rsc/netflix_genre.json'))
	return render_template("netflix_genre.html",list_genre=list_genre)


@app.route('/<app_name>/',methods=['GET'])
@app.route('/<app_name>',methods=['GET'])
def no_neo_redirection(app_name=None):
	print('no_neo_redirection')
	return redirect("/"+app_name+".neo")



@app.route('/<path:path>')
def send_static(path):
	return send_from_directory('static', path)

@app.route('/static/<path:path>')
def send_static_2(path):
	return send_from_directory('static', path)

@app.route('/etc/ip')
def get_ip():
	data = dict(ip = request.remote_addr)
	return jsonify(data)


@app.route('/exam')
def exam():
	return send_from_directory('static', "sample.html")
	#//return render_template("test.html",**dict())

@app.route('/page_test_2')
def page_test_2():
	print("page_test_2")
	conn = mysql.connect()
	cur = conn.cursor(pymysql.cursors.DictCursor)
	cur.execute("""SELECT pwd_uid as cur_uid,site, B.title,ptail,B.phd_uid,id,A.etc ,A.updt_date
  FROM passwd A,pheader B where A.phd_uid = B.phd_uid  order by updt_date desc""")
	data = {}
	data['data']= cur.fetchall()
	#data = cur.fetchall()
	print(data)
	return jsonify(data)

@app.route('/page_test_3',methods=['GET'])
def webtoon_table():
	from neo_server.parsing_class.show_naverweb import GetLateestWebtoon
	list_all = ["675554", "665170", "22897", "21815", "25455", "570506", "641253", "670139", "690503", "703307",
				"695321", "696617", "597478", "710766", "703836", "723714", "710751", "712694", "727268", "726842",
				"728750", "730259", "730148", "729255", "733413"]
	inst = GetLateestWebtoon(date=''
								  '', list_ids=list_all).run()
	result = inst.result()
	return render_template("webtoon_table.html",id_div_list="id_div_list",title="TEST",result=result,modal_id="test_modal_id")

@app.route('/page_test_4',methods=['GET'])
def keyword_order_contents():
	from neo_server.parsing_class.show_naverweb import GetLateestWebtoon
	
	from neo_server.parsing_class.show_portal_order import CheckPortalOrder
	result = CheckPortalOrder().run().result()
	list_portals = []
	for main_url, search, list_order_org in result:
		list_order = []
		for order, key_word in list_order_org:
			import urllib
			list_order.append(
				dict(order=order, keyword=key_word, url=search.format(urllib.parse.quote(key_word, safe=''))))
			pass
		
		list_portals.append(dict(title=main_url, list_order=list_order[:10]))
	return render_template("keyword_order_contents.html",list_portals=list_portals)

@app.route('/page_test')
def page_test():
	print("page_test")


	return jsonify(sample_data)


def init():
	global telebot_inst
	from neo_server.neo_telegram_bot import neo_chat_bot
	api_token = neo_bot_token
	if sys.argv.__len__() > 1 and sys.argv[1] == 'debug':
		api_token = temptest_bot
	#telebot_inst = neo_chat_bot.start(api_token)
	#telebot_inst = neo_chat_bot.start(api_token)




if __name__ == '__main__':

	init()
	app.run(host='localhost' ,port=5556,threaded=True)
