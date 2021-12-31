import urllib
import urllib
import urllib.parse

from neo_server.main_class.class_web_app_base import *
#from neo_server.main_server import basedir
from neo_server.main_value import basedir
from neo_server.parsing_class.show_portal_order import CheckPortalOrder
from neo_server.tool.create_diary_with_class import HandlingDiaryGDocs


class CreateDiaryWebApp(BaseDBWebApp):
	fmt_select_keyword_order ="""SELECT seq, kwo_uid, prt_uid, `order`,keyword,url, etc, updt_date, reg_date, comment
					FROM neo_pwinfo.keyword_order where prt_uid = '{}';"""

	def init_run(self):
		#self.update_custom()
		pass
	def update_from_db(self):
		pass


	def create_diary(self):
		print("create_diary title",self.data.title)


		secrete_file = basedir + '/rsc/client_secret_476383775373-192qipsl35ec4g3hf7ue11v4464j8mp0.apps.googleusercontent.com.json'
		storage_file = basedir +"/rsc/storage.json"
		folder_id = '171NMajZTbIJB_tcXiO9PAxOXgxZoce0T'  # 2019
		folder_id = '1EuKyGnIt7l4n3pjyf9xJbcKCqTlHCWK3'  # 2020
		folder_id = '14vcMN6bSAfeIIEx8Zm3JuRLTOzSbpPrX'  # 2021
		folder_id = '15emoEeiwCCSCh_FvywT8ZwDPS7-OPC-z' # 2022
		#folder_id = '1nxWaOdPzGGcS7yM-Tf_9J3FLexF6ptvf'  # test

		# messagebox.showinfo("secrete_file", f"{secrete_file} ")
		inst = HandlingDiaryGDocs.get_build_drive(secrete_file,storage_file)
		file = inst.create_diary(folder_id, self.data.title)
		url = f'https://docs.google.com/document/d/{file["id"]}/edit'


		return dict(url=url)
		


	pass