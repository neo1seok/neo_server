from neolib import neoutil

from neo_server.main_class.class_web_app_base import BaseDBWebApp, row_dict


class JcsgNovelWebApp(BaseDBWebApp):
	def post_process(self):
		list_input_row = [

			row_dict(name="cur_uid", id="input_cur_uid", type='hidden'),
			row_dict(title="제목", name="title", id="input_title", row_type="all", type="input"),
			row_dict(title="이슈", name="issue", id="input_issue", row_type="all", type="text"),
			row_dict(title="솔루션", name="solution", id="input_solution", row_type="all", type="text"),

		]

		list_attr = [dict(key="data-toggle", val="modal"),
		             dict(key="data-target", val="#id_modal_input"),
		             ]
		list_attr_ext = [
			dict(key="onclick", proc=lambda item: "edit_content('{cur_uid}')".format(cur_uid=item['cur_uid']))]
		text_ext = lambda item: item['title']

		this_table = dict(title="전체리스트",
		                  form_title="title",

		                  list_input_row=list_input_row,
		                  list_col_info=[
			                  dict(title="제목", type="btn_ext", onclick="edit_content", href_key="link",
			                       title_key="title",
			                       list_attr=list_attr,
			                       list_attr_ext=list_attr_ext,
			                       text_ext=lambda
				                       item: item['title'],

			                       ),
			                  dict(title="날짜", type="title", title_key="updt_date"),
			                  dict(title="삭제", type="btn_no_modal", onclick="delete_content"),
		                  ],
		                  list_data=self.list_data)

		self.list_tables[0].update(this_table)
		neoutil.simple_view_list(self.list_data)
		pass

	def get_content(self):
		#print('get_content',self.data.option)
		list_header = self.select("""SELECT no, title, contents, status FROM neo_pwinfo.jcsg_contents where jc_uid='{cur_uid}';""".format(cur_uid=self.data.cur_uid ))

		response = {}
		response['result'] = "ok"
		return response
