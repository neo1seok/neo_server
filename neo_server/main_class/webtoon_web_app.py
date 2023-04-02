import copy
import datetime
import pickle

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

		#self.extra_condition = "and status != 'HIDDEN' and A.updt_date >= DATE_ADD(NOW(), INTERVAL -1 DAY) order by updt_date desc"
		self.extra_condition = f"and status != 'HIDDEN' and dates ='{self.get_today_date()}' order by updt_date desc"


		pass
	
	# def update_from_db(self):
	# 	pass
	
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

		self._build_table_list_table()
		# self.list_tables

		# for map_line in self.list_data:
		# 	id = map_line['id']
		# 	map_line['list_url'] = map_line['list_url'].format(id)
		# 	map_line['detail_url'] = map_line['detail_url'].format(id, map_line['lastno'])

		this_table = dict(title="웹툰",
		                  list_input_row=list_input_row,
		                  list_col_info=[
			                  dict(title="제목", type="link", href_key="list_url", title_key="title"),
			                  dict(title="오늘제목", type="link", href_key="detail_url", title_key="today_title"),

			                  dict(title="편집", type="btn", onclick="edit_content"),
			                  dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
		                  ],
		                  list_data=self.list_data)


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

	def _build_table_list_table(self):
		str_tail=""
		for map_line in self.list_data:
			id = map_line['id']
			comment = map_line['comment']
			detail_data = {}
			try:
				detail_data = json.loads(comment)
			except:
				pass

			map_line['list_url'] = map_line['list_url'].format(id)
			map_line['detail_url'] = map_line['detail_url'].format(id, map_line['lastno'])

			map_line['reg_date'] = f"{map_line['reg_date']:%Y/%m/%d}"
			map_line['img_src'] = detail_data.get('img_src','')
			map_line['main_img_src'] = detail_data.get('main_img_src', '')
			map_line['status_icon'] = detail_data.get('status_icon', '')



		table_html = render_template("webtoon_table.html", id_div_list="id_div_list", title=f"네이년 웹툰 {str_tail}",
		                             list_result_webtoon=self.list_data,
		                             modal_id="id_modal_input")


		#return list_data

	def update_custom(self):
		st = time.time()
		dict_time ={}

		date = neoutil.get_safe_mapvalue(request.values, "date", "")
		option = neoutil.get_safe_mapvalue(request.values, "option", "detail")
		print("update_custom",date)
		print("option", option)

		# get list of ids on not hidden in db

		#우선 db에 가능한 ids와 update date 들을 구한다.
		sql = f"""SELECT * FROM neo_pwinfo.webtoon where  status != 'HIDDEN' and dates='{date}';"""
		list_ids = self.select(sql)

		print(list_ids)

		#현재 id와 updt_date를 매핑한다.
		dict_db_data_per_id = {tmp['id']: tmp for tmp in list_ids}
		from neo_server.main_server import webtoon_info_file
		webtoon_info = pickle.load(open(webtoon_info_file,'rb'))
		print("webtoon_info",webtoon_info)



		#먼저 매인 대쉬 정버를 바탕으로 필터링된 ids를 구한다.
		inst = GetLateestWebtoon(date=date, list_ids=[tmp['id'] for tmp in list_ids],option=WEBTOON_PARSE_OPTION.update_detail_filter_ids_up if option !="detail" else WEBTOON_PARSE_OPTION.update_detail_all_ids
		   )
		inst.run()






		#self.list_result_webtoon = inst.result_detail
		self.cur_web_date = inst.result_detail['today_date']
		self.dict_result_webtoon = inst.result_detail['all_data']

		'''
		result_detail:
		{'today_date': 'sun',
 'all_data': {'758037': {'titleId': '758037',
                         'title': '참교육',
                         'status': '',
                         'week_date': 'mon',
                         'is_detail': False},
                         .
                         .
                         .
		'''
		
		self.title = "{} ({}요일)".format(self.title_org, self.cur_web_date)
		
		#옵션에 따라 db에 업데이트 시킨다.
		#if option == WEBTOON_PARSE_OPTION.detail:
		dict_update_ids = {}
		for id_,tmp_dic in self.dict_result_webtoon.items():
			comment = dict_db_data_per_id[id_].get('comment','{}')
			if comment =="":
				comment = "{}"
			db_hash_value = json.loads(comment).get('hash')
			cur_hash = tmp_dic['hash']
			if option != 'force' and db_hash_value == cur_hash:
				continue


			print("hash vals",db_hash_value,cur_hash)

			comment = pymysql.escape_string(json.dumps(tmp_dic,ensure_ascii=True))

			dict_update_ids[id_] = copy.deepcopy(tmp_dic)
			tmp_dic['comment'] = comment
			sql_update = """UPDATE neo_pwinfo.webtoon
						SET title='{web_title}', today_title = '{today_title}',  lastno = '{lastno}', updt_date = now(),reg_date = '{reg_date}',comment='{comment}'
						WHERE id='{id}';""".format(**tmp_dic)
			print(sql_update)
			self.cur.execute(sql_update)
		return dict(dict_update_ids=dict_update_ids)
