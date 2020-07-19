import datetime

from neo_server.main_class.class_web_app_base import *
from neo_server.parsing_class.enum_option import WEBTOON_PARSE_OPTION
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

		self.date = neoutil.get_safe_mapvalue(request.values, "date", "")
		
		sql = """
				SELECT prt_uid, main_url,name as title 	FROM neo_pwinfo.portal;
				"""
		list_portals = self.select(sql)
		

		
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
		print("self.cur_web_date",self.cur_web_date)
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

	def update_from_site(self):

		return dict()



	def update_custom(self):
		st = time.time()
		dict_time ={}

		date = neoutil.get_safe_mapvalue(request.values, "date", "")
		option = neoutil.get_safe_mapvalue(request.values, "option", "")
		print("update_custom",date)
		print("option", option)

		# get list of ids on not hidden in db

		#우선 db에 가능한 ids와 update date 들을 구한다.
		sql = """SELECT id,updt_date FROM neo_pwinfo.webtoon where  status != 'HIDDEN';"""
		list_ids = self.select(sql)

		#현재 id와 updt_date를 매핑한다.
		dict_updt_date_per_id = {tmp['id']: tmp['updt_date'] for tmp in list_ids}


		#먼저 매인 대쉬 정버를 바탕으로 필터링된 ids를 구한다.
		inst = GetLateestWebtoon(date=date, list_ids=[tmp['id'] for tmp in list_ids])

		inst.get_today()


		filterd_ids = inst.update_get_filter_ids()
		inst.dict_timer
		dict_time.update(**inst.dict_timer)
		dict_time["update_get_filter_ids "] = time.time() -st
		st = time.time()


		#현재 시간을 기준으로 하루가 넘어 가는 경우 detail update를 한다.
		if date =='org' or option == 'detail':
			option = WEBTOON_PARSE_OPTION.detail
		else:
			today = datetime.datetime.today()
			option = WEBTOON_PARSE_OPTION.no_detail

			for id in filterd_ids:

				updt_date = dict_updt_date_per_id[id]
				td = today.date() - updt_date.date()
				print("##update",updt_date, td)


				if td.days >1:
					option = WEBTOON_PARSE_OPTION.detail
					break



		print("option",option)

		#결정된 option을 세팅하고 실행한다..
		inst.set_option(option)
		inst.run()
		dict_time["update_detail_title "] = time.time() - st
		st = time.time()

		self.list_result_webtoon = inst.result()
		self.cur_web_date = inst.cur_web_date
		'''
		[{'id': '723714', 'lastno': '126', 'today_title': '126화',
		'img_src': 'https://shared-comic.pstatic.net/thumb/webtoon/723714/126/thumbnail_202x120_0c4a6d38-b9cd-4106-aced-9c45f2795bf9.jpg',
		'status_icon': '', 'writer': '류기운 / 문정후', 'web_title': '용비불패 완전판', 'reg_date': '2019.11.21'},
		]
		'''
		
		self.title = "{} ({}요일)".format(self.title_org, self.cur_web_date)
		
		#옵션에 따라 db에 업데이트 시킨다.
		if option == WEBTOON_PARSE_OPTION.detail:
			self.dict_result_webtoon = {tmp['id']: tmp for tmp in self.list_result_webtoon}

			for tmp_dic in self.list_result_webtoon:

				comment = pymysql.escape_string(json.dumps(tmp_dic))
				tmp_dic['comment']=comment

				sql_update = """UPDATE neo_pwinfo.webtoon
							SET title='{web_title}', today_title = '{today_title}',  lastno = '{lastno}', updt_date = now(),comment='{comment}'
							WHERE id='{id}';""".format(**tmp_dic)
				self.cur.execute(sql_update)
		dict_time["update_db"] = time.time() - st
		st = time.time()

		ids = ",".join([f"'{tmp['id']}'" for tmp in self.list_result_webtoon])
		if not ids:
			ids = "''"
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
			#webtoon_info = self.dict_result_webtoon.get(id, {})
			#del  webtoon_info['title']
			#del webtoon_info['today_title']

			# map_line.update(**webtoon_info)
			# print("id",webtoon_info)
		kor_date = GetLateestWebtoon.map_date_rev.get(inst.date,"")

		print("inst.date",inst.date,self.date)
		if kor_date:
			str_tail = f"{kor_date}요일"
		elif inst.date =='all':
			str_tail = '연재중 리스트 '
		elif inst.date == 'org':
			str_tail = '전체 리스트 '

		table_html =render_template("webtoon_table.html", id_div_list="id_div_list", title=f"네이년 웹툰 {str_tail}", list_result_webtoon=self.list_data,
		                       modal_id="id_modal_input")

		dict_time["make_table_html"] = time.time() - st
		st = time.time()

		return dict(table_html=table_html,cur_web_date=self.cur_web_date,date=inst.date,
		            option =option.name,dict_time=dict_time)


# print(list_result)
# return dict(result='ok')
