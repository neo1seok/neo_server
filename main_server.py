import os
import sys

from flask import Flask, request, render_template, url_for, Markup, json, session, send_from_directory
from flaskext.mysql import MySQL
from flask import jsonify
from werkzeug.security import generate_password_hash
import pymysql
from werkzeug.utils import redirect

from main_class import class_web_app
from neo_telegram_bot.api_token import neo_bot_token, temptest_bot

dir_path = os.path.dirname(os.path.realpath(__file__))
map_general_map = class_web_app.get_lists(dir_path)

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
app.config['MYSQL_DATABASE_USER'] = 'neo1seok'
app.config['MYSQL_DATABASE_PASSWORD'] = 'tofhdna1pi'
app.config['MYSQL_DATABASE_DB'] = 'neo_pwinfo'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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

@app.route('/<app_name>/',methods=['GET'])
@app.route('/<app_name>',methods=['GET'])
def no_neo_redirection(app_name=None):
	print('no_neo_redirection')
	return redirect("/"+app_name+".neo")


@app.route('/<path:path>')
def send_static(path):
	return send_from_directory('static', path)

@app.route('/test')
def test():
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

@app.route('/page_test')
def page_test():
	print("page_test")
	data = {
  "data": [
	[
	  "Tiger Nixon",
	  "System Architect",
	  "Edinburgh",
	  "5421",
	  "2011/04/25",
	  "$320,800"
	],
	[
	  "Garrett Winters",
	  "Accountant",
	  "Tokyo",
	  "8422",
	  "2011/07/25",
	  "$170,750"
	],
	[
	  "Ashton Cox",
	  "Junior Technical Author",
	  "San Francisco",
	  "1562",
	  "2009/01/12",
	  "$86,000"
	],
	[
	  "Cedric Kelly",
	  "Senior Javascript Developer",
	  "Edinburgh",
	  "6224",
	  "2012/03/29",
	  "$433,060"
	],
	[
	  "Airi Satou",
	  "Accountant",
	  "Tokyo",
	  "5407",
	  "2008/11/28",
	  "$162,700"
	],
	[
	  "Brielle Williamson",
	  "Integration Specialist",
	  "New York",
	  "4804",
	  "2012/12/02",
	  "$372,000"
	],
	[
	  "Herrod Chandler",
	  "Sales Assistant",
	  "San Francisco",
	  "9608",
	  "2012/08/06",
	  "$137,500"
	],
	[
	  "Rhona Davidson",
	  "Integration Specialist",
	  "Tokyo",
	  "6200",
	  "2010/10/14",
	  "$327,900"
	],
	[
	  "Colleen Hurst",
	  "Javascript Developer",
	  "San Francisco",
	  "2360",
	  "2009/09/15",
	  "$205,500"
	],
	[
	  "Sonya Frost",
	  "Software Engineer",
	  "Edinburgh",
	  "1667",
	  "2008/12/13",
	  "$103,600"
	],
	[
	  "Jena Gaines",
	  "Office Manager",
	  "London",
	  "3814",
	  "2008/12/19",
	  "$90,560"
	],
	[
	  "Quinn Flynn",
	  "Support Lead",
	  "Edinburgh",
	  "9497",
	  "2013/03/03",
	  "$342,000"
	],
	[
	  "Charde Marshall",
	  "Regional Director",
	  "San Francisco",
	  "6741",
	  "2008/10/16",
	  "$470,600"
	],
	[
	  "Haley Kennedy",
	  "Senior Marketing Designer",
	  "London",
	  "3597",
	  "2012/12/18",
	  "$313,500"
	],
	[
	  "Tatyana Fitzpatrick",
	  "Regional Director",
	  "London",
	  "1965",
	  "2010/03/17",
	  "$385,750"
	],
	[
	  "Michael Silva",
	  "Marketing Designer",
	  "London",
	  "1581",
	  "2012/11/27",
	  "$198,500"
	],
	[
	  "Paul Byrd",
	  "Chief Financial Officer (CFO)",
	  "New York",
	  "3059",
	  "2010/06/09",
	  "$725,000"
	],
	[
	  "Gloria Little",
	  "Systems Administrator",
	  "New York",
	  "1721",
	  "2009/04/10",
	  "$237,500"
	],
	[
	  "Bradley Greer",
	  "Software Engineer",
	  "London",
	  "2558",
	  "2012/10/13",
	  "$132,000"
	],
	[
	  "Dai Rios",
	  "Personnel Lead",
	  "Edinburgh",
	  "2290",
	  "2012/09/26",
	  "$217,500"
	],
	[
	  "Jenette Caldwell",
	  "Development Lead",
	  "New York",
	  "1937",
	  "2011/09/03",
	  "$345,000"
	],
	[
	  "Yuri Berry",
	  "Chief Marketing Officer (CMO)",
	  "New York",
	  "6154",
	  "2009/06/25",
	  "$675,000"
	],
	[
	  "Caesar Vance",
	  "Pre-Sales Support",
	  "New York",
	  "8330",
	  "2011/12/12",
	  "$106,450"
	],
	[
	  "Doris Wilder",
	  "Sales Assistant",
	  "Sidney",
	  "3023",
	  "2010/09/20",
	  "$85,600"
	],
	[
	  "Angelica Ramos",
	  "Chief Executive Officer (CEO)",
	  "London",
	  "5797",
	  "2009/10/09",
	  "$1,200,000"
	],
	[
	  "Gavin Joyce",
	  "Developer",
	  "Edinburgh",
	  "8822",
	  "2010/12/22",
	  "$92,575"
	],
	[
	  "Jennifer Chang",
	  "Regional Director",
	  "Singapore",
	  "9239",
	  "2010/11/14",
	  "$357,650"
	],
	[
	  "Brenden Wagner",
	  "Software Engineer",
	  "San Francisco",
	  "1314",
	  "2011/06/07",
	  "$206,850"
	],
	[
	  "Fiona Green",
	  "Chief Operating Officer (COO)",
	  "San Francisco",
	  "2947",
	  "2010/03/11",
	  "$850,000"
	],
	[
	  "Shou Itou",
	  "Regional Marketing",
	  "Tokyo",
	  "8899",
	  "2011/08/14",
	  "$163,000"
	],
	[
	  "Michelle House",
	  "Integration Specialist",
	  "Sidney",
	  "2769",
	  "2011/06/02",
	  "$95,400"
	],
	[
	  "Suki Burks",
	  "Developer",
	  "London",
	  "6832",
	  "2009/10/22",
	  "$114,500"
	],
	[
	  "Prescott Bartlett",
	  "Technical Author",
	  "London",
	  "3606",
	  "2011/05/07",
	  "$145,000"
	],
	[
	  "Gavin Cortez",
	  "Team Leader",
	  "San Francisco",
	  "2860",
	  "2008/10/26",
	  "$235,500"
	],
	[
	  "Martena Mccray",
	  "Post-Sales support",
	  "Edinburgh",
	  "8240",
	  "2011/03/09",
	  "$324,050"
	],
	[
	  "Unity Butler",
	  "Marketing Designer",
	  "San Francisco",
	  "5384",
	  "2009/12/09",
	  "$85,675"
	],
	[
	  "Howard Hatfield",
	  "Office Manager",
	  "San Francisco",
	  "7031",
	  "2008/12/16",
	  "$164,500"
	],
	[
	  "Hope Fuentes",
	  "Secretary",
	  "San Francisco",
	  "6318",
	  "2010/02/12",
	  "$109,850"
	],
	[
	  "Vivian Harrell",
	  "Financial Controller",
	  "San Francisco",
	  "9422",
	  "2009/02/14",
	  "$452,500"
	],
	[
	  "Timothy Mooney",
	  "Office Manager",
	  "London",
	  "7580",
	  "2008/12/11",
	  "$136,200"
	],
	[
	  "Jackson Bradshaw",
	  "Director",
	  "New York",
	  "1042",
	  "2008/09/26",
	  "$645,750"
	],
	[
	  "Olivia Liang",
	  "Support Engineer",
	  "Singapore",
	  "2120",
	  "2011/02/03",
	  "$234,500"
	],
	[
	  "Bruno Nash",
	  "Software Engineer",
	  "London",
	  "6222",
	  "2011/05/03",
	  "$163,500"
	],
	[
	  "Sakura Yamamoto",
	  "Support Engineer",
	  "Tokyo",
	  "9383",
	  "2009/08/19",
	  "$139,575"
	],
	[
	  "Thor Walton",
	  "Developer",
	  "New York",
	  "8327",
	  "2013/08/11",
	  "$98,540"
	],
	[
	  "Finn Camacho",
	  "Support Engineer",
	  "San Francisco",
	  "2927",
	  "2009/07/07",
	  "$87,500"
	],
	[
	  "Serge Baldwin",
	  "Data Coordinator",
	  "Singapore",
	  "8352",
	  "2012/04/09",
	  "$138,575"
	],
	[
	  "Zenaida Frank",
	  "Software Engineer",
	  "New York",
	  "7439",
	  "2010/01/04",
	  "$125,250"
	],
	[
	  "Zorita Serrano",
	  "Software Engineer",
	  "San Francisco",
	  "4389",
	  "2012/06/01",
	  "$115,000"
	],
	[
	  "Jennifer Acosta",
	  "Junior Javascript Developer",
	  "Edinburgh",
	  "3431",
	  "2013/02/01",
	  "$75,650"
	],
	[
	  "Cara Stevens",
	  "Sales Assistant",
	  "New York",
	  "3990",
	  "2011/12/06",
	  "$145,600"
	],
	[
	  "Hermione Butler",
	  "Regional Director",
	  "London",
	  "1016",
	  "2011/03/21",
	  "$356,250"
	],
	[
	  "Lael Greer",
	  "Systems Administrator",
	  "London",
	  "6733",
	  "2009/02/27",
	  "$103,500"
	],
	[
	  "Jonas Alexander",
	  "Developer",
	  "San Francisco",
	  "8196",
	  "2010/07/14",
	  "$86,500"
	],
	[
	  "Shad Decker",
	  "Regional Director",
	  "Edinburgh",
	  "6373",
	  "2008/11/13",
	  "$183,000"
	],
	[
	  "Michael Bruce",
	  "Javascript Developer",
	  "Singapore",
	  "5384",
	  "2011/06/27",
	  "$183,000"
	],
	[
	  "Donna Snider",
	  "Customer Support",
	  "New York",
	  "4226",
	  "2011/01/25",
	  "$112,000"
	]
  ]
}

	return jsonify(data)


def init():
	global telebot_inst
	from neo_telegram_bot import neo_chat_bot
	api_token = neo_bot_token
	if sys.argv.__len__() > 1 and sys.argv[1] == 'debug':
		api_token = temptest_bot
	#telebot_inst = neo_chat_bot.start(api_token)
	#telebot_inst = neo_chat_bot.start(api_token)




if __name__ == '__main__':

	init()
	app.run(host='localhost' ,port=5555,threaded=True)
