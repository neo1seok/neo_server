import os
from flask import Flask, request, render_template, url_for, Markup, json
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash
import pymysql
from werkzeug.utils import redirect

from main_class import class_web_app
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


def get_main_inst(app_name):

	return map_general_map[app_name].update_params( mysql)
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



@app.route('/<app_name>/',methods=['GET'])
@app.route('/<app_name>',methods=['GET'])
def no_neo_redirection(app_name=None):
	print('no_neo_redirection')
	return redirect("/"+app_name+".neo")

if __name__ == '__main__':
	#import tool_xls_to_json
	#tool_xls_to_json.main()

	app.run(host='0.0.0.0' ,port=5555,threaded=True)
