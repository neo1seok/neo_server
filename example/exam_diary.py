from neo_server.tool.create_diary_with_class import HandlingDiaryGDocs
basedir ="../neo_server"
secrete_file = basedir + '/rsc/client_secret_476383775373-192qipsl35ec4g3hf7ue11v4464j8mp0.apps.googleusercontent.com.json'
storage_file = basedir +"/rsc/storage.json"

inst = HandlingDiaryGDocs.get_build_drive(secrete_file,storage_file)
inst.get_subfolders()
dict_folder_id ={
			2023:'1xlxONRV9EkgXXSIfgMoUu0Z1iChYNEtN',
			2024: '1n09C7N4e2c1HDXuduRkCK5RUfRAop0GY',
		}
#inst.create_diary(dict_folder_id,"TEST")
