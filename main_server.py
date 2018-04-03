from flask import Flask, request, render_template, url_for, Markup, json, session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash
import pymysql
from werkzeug.utils import redirect

import class_web_app
import tool_xls_to_json
#WebAppBase, map_general_map, navigation, tag_login
map_general_map = class_web_app.get_lists()

print(map_general_map)
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
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '#root1234'
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


@app.route('/<app_name>/')
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












@app.route('/user/<username>')
def show_user_profile(username):
	# show the user profile for that user
	return 'User %s' % username
	print("show_entries",app_name)
	title = "MB GO TO JAIN"
	conn = mysql.connect()
	cur = conn.cursor(pymysql.cursors.DictCursor)
	cur.execute('''SELECT seq, fnk_uid, title, link, updt_date, reg_date, comment, type 
					FROM neo_pwinfo.fav_link where type = 'MAIN';''')

	list_data = cur.fetchall()
	list_col_name = ["제목","날짜"]
	print(list_data)

	return render_template('test_jinja.html',** dict(title=title,list_col_name=list_col_name, list_data=list_data,navigation=navigation))

	return render_template('test_jinja.html',title=title,list_col_name=list_col_name, list_data=list_data,navigation=navigation)
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
# 	if request.method == 'POST':
#
#
# 		#do_the_login()
# 		print("POST")
# 		return "POST"
# 	else:
# 		print(request.args)
# 		return "GET"
# 		#show_the_login_form()

#
# @app.route('/login', methods=['GET', 'POST'])
# def logout():
# 	session.pop(tag_login,False)
# 	return redirect("/")
	#show_the_login_form()
@app.route('/test/')
@app.route('/test/<name>')
def hello(name=None):
	url_for('static', filename='style.css')
	navigation = []
	for i in range(1, 11):
		i = str(i)

		# dict == {}
		# you just don't have to quote the keys
		an_item = dict(date="2012-02-" + i, id=i, position="here", status="waiting",href="aafdf",caption="asdfadfaf")
		navigation.append(an_item)
	items = []
	for i in range(1, 11):
		i = str(i)

		# dict == {}
		# you just don't have to quote the keys
		an_item = dict(date="2012-02-" + i, id=i, position="here", status="waiting")
		items.append(an_item)
	return render_template('test.html',title='MB GO TO JAIL', name=name,navigation=navigation,items=items)

@app.route('/sample_form/')
@app.route('/sample_form/<title>')
def sample_form(title=None):
	url_for('static', filename='style.css')


	list_data = []
	for i in range(1, 11):
		i = str(i)

		# dict == {}
		# you just don't have to quote the keys
		an_item = dict(date="2012-02-" + i, id=i, position="here", status="waiting")
		list_data.append(an_item)
	return render_template('sample_form.html', title=title,navigation=navigation,list_data=list_data)

@app.route('/tes2t/')
@app.route('/test2/<name>')
def test2(name=None):
	app.logger.debug('A value for debugging')
	app.logger.warning('A warning occurred (%d apples)', 42)
	app.logger.error('An error occurred')
	Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
	Markup.escape('<blink>hacker</blink>')
	Markup('<em>Marked up</em> &raquo; HTML').striptags()


	return ""
@app.route('/signup')
def showSignUp():
	return render_template('signup.html')

@app.route('/test_red')
def test_red():
	return redirect("/signup")

@app.route('/signUp', methods=['POST'])
def signUp():
	# read the posted values from the UI
	_name = request.form['inputName']
	_email = request.form['inputEmail']
	_password = request.form['inputPassword']

	conn = mysql.connect()
	cursor = conn.cursor()
	_hashed_password = generate_password_hash(_password)
	print(_hashed_password)
	cursor.callproc('sp_createUser', (_name, _email, _hashed_password))

	data = cursor.fetchall()

	if len(data) is 0:
		conn.commit()
		return json.dumps({'message': 'User created successfully !'})
	else:
		return json.dumps({'error': str(data[0])})
	#
	# # validate the received values
	# if _name and _email and _password:
	# 	return json.dumps({'html': '<span>All fields good !!</span>'})
	# else:
	# 	return json.dumps({'html': '<span>Enter the required fields</span>'})

if __name__ == '__main__':

	app.run(host='0.0.0.0' ,port=80,threaded=True)