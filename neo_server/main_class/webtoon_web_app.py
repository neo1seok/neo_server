from neo_server.main_class.class_web_app_base import *
from neo_server.parsing_class.show_naverweb import GetLateestWebtoon


class WebtoonWebApp(BaseDBWebApp):
	def init(self):
		BaseDBWebApp.init(self)
		self.title_org = self.title
		self.list_result_webtoon =[]
		self.dict_result_webtoon = {}
		self.cur_web_date=""
	
	def init_run(self):
		#self.update_custom()
		
		pass
	
	def get_today_date(self):
		import time
		now = time.localtime()
		
		week = ['월', '화', '수', '목', '금', '토', '일']
		date_name = week[now.tm_wday]
		return date_name
	
	def ready_extra_condition(self):
		pass
	
	def update_from_db(self):
		pass
	
	def post_process(self):
		type = neoutil.get_safe_mapvalue(request.values, "type", "")
		
		sql = """
				SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
				"""
		list_portals = self.select(sql)
		
		# for map_line in self.list_data:
		# 	id = map_line['id']
		# 	map_line['list_url'] = map_line['list_url'].format(id)
		# 	map_line['detail_url'] = map_line['detail_url'].format(id, map_line['lastno'])
		# 	webtoon_info = self.dict_result_webtoon.get(id,{})
		# 	map_line.update(**webtoon_info)
		
		# print("map_url", map_line['list_url'], map_line['detail_url'])
		
		list_input_row = [
			
			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="웹툰이름", name="title", id="input_title", row_type="all", type="input"),
			row_dict(title="웹툰아이디", name="id", id="input_id", row_type="left", type="input"),
			row_dict(title="요일", name="dates", id="input_dates", row_type="right", type="input"),
			row_dict(title="포탈", name="prt_uid", id="input_prt_uid",
			         row_type='all', type="select",
			         list_options=[dict(value=map_portal['prt_uid'], name=map_portal["title"]) for map_portal in
			                       list_portals])
		]
		# self.list_tables
		
		this_table = dict(title="웹툰",
		                  list_input_row=list_input_row,
		                  list_col_info=[
			                  dict(title="제목", type="link", href_key="list_url", title_key="title"),
			                  dict(title="제목", type="link", href_key="detail_url", title_key="today_title"),
			                  dict(title="편집", type="btn", onclick="edit_content"),
			                  dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
		                  ],
		                  list_data=[])
		map_date = {
			'월': 'mon',
			'화': 'tue',
			'수': 'wed',
			'목': 'thu',
			'금': 'fri',
			'토': 'sat',
			'일': 'sun',
			
		}
		week = map_date.get(self.cur_web_date, "all")
		self.url_naver_date_webtoon = f"https://comic.naver.com/webtoon/weekdayList.nhn?week={week}" \
			if week != 'all' else 'https://comic.naver.com/webtoon/weekday.nhn'
		
		self.date_btn_info = []
		for name, eng in map_date.items():
			is_cur_date = (name == self.cur_web_date)
			
			self.date_btn_info.append(dict(name=name, eng=eng, is_cur_date=is_cur_date))
		
		self.list_tables[0].update(this_table)
#		neoutil.simple_view_list(self.list_data)
		pass
	
	def update_custom(self):

		date = neoutil.get_safe_mapvalue(request.values, "date", "")
		
		# get list of ids on not hidden in db
		sql = """SELECT id FROM neo_pwinfo.webtoon where  status != 'HIDDEN';"""
		list_ids = self.select(sql)
		
		print(sql, list_ids)
		inst = GetLateestWebtoon(date=date, list_ids=[tmp['id'] for tmp in list_ids]).run()
		self.list_result_webtoon = inst.result()
		self.cur_web_date = inst.cur_web_date
		'''
		[{'id': '723714', 'lastno': '126', 'today_title': '126화',
		'img_src': 'https://shared-comic.pstatic.net/thumb/webtoon/723714/126/thumbnail_202x120_0c4a6d38-b9cd-4106-aced-9c45f2795bf9.jpg',
		'status_icon': '', 'writer': '류기운 / 문정후', 'web_title': '용비불패 완전판', 'reg_date': '2019.11.21'},
		]
		'''
		
		self.title = "{} ({}요일)".format(self.title_org, self.cur_web_date)
		
		self.dict_result_webtoon = {tmp['id']: tmp for tmp in self.list_result_webtoon}
		
		for tmp_dic in self.list_result_webtoon:
			sql_update = """UPDATE neo_pwinfo.webtoon
						SET title='{web_title}', today_title = '{today_title}',  lastno = '{lastno}', updt_date = now()
						WHERE id='{id}';""".format(**tmp_dic)
			self.cur.execute(sql_update)

		ids = ",".join([f"'{tmp['id']}'" for tmp in self.list_result_webtoon])
		
		BaseDBWebApp.ready_extra_condition(self)
		self.extra_condition += "and id in (%s) " % ids
		
		
		
		sql = self.fmt_list.format(extra_condition=self.extra_condition)
		print("extra_condition", self.extra_condition)
		print("sql", sql)
		self.cur.execute(sql)
		self.list_data = self.cur.fetchall()
		
		for map_line in self.list_data:
			id = map_line['id']
			map_line['list_url'] = map_line['list_url'].format(id)
			map_line['detail_url'] = map_line['detail_url'].format(id, map_line['lastno'])
			webtoon_info = self.dict_result_webtoon.get(id, {})
			map_line.update(**webtoon_info)
			
		
		
		table_html =render_template("webtoon_table.html", id_div_list="id_div_list", title="네이년 웹툰 ", list_result_webtoon=self.list_data,
		                       modal_id="id_modal_input")
		return dict(table_html=table_html)
# print(list_result)
# return dict(result='ok')
