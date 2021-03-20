import os

from googleapiclient.discovery import build
import googleapiclient
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
def get_weekday(curdate = datetime.datetime.now()):
	return "월화수목금토일"[curdate.weekday()]

class HandlingDiaryGDocs():
	def __init__(self,DRIVE,base_folder_id = '0B-r02_3Jzx_tNDNmNWZiYzQtNGFkMi00ZTk5LWEyMzAtYjE2N2EyOTIwNjJi'):
		self.DRIVE = DRIVE
		self.base_folder_id = base_folder_id

	@classmethod
	def get_build_drive(cls,secrete_file,store_file='storage.json'):
		try :
			import argparse
			flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
		except ImportError:
			flags = None

		store = file.Storage(store_file)
		creds = store.get()

		if not creds or creds.invalid:
			SCOPES = 'https://www.googleapis.com/auth/drive.file'
			SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
			# SCOPES ='https://www.googleapis.com/upload/drive/v3/files?uploadType=media'

			print("make new storage data file ")
			flow = client.flow_from_clientsecrets(secrete_file, SCOPES)
			creds = tools.run_flow(flow, store, flags) \
					if flags else tools.run(flow, store)

		DRIVE = build('drive', 'v3', http=creds.authorize(Http()))
		return HandlingDiaryGDocs(DRIVE)

	def create_doc(self,folder_id,title):
		file_metadata = {
			'name': title,
			'mimeType': 'application/vnd.google-apps.document',
			'parents': [folder_id]
		}

		file = self.DRIVE.files().create(body=file_metadata,
									# media_body=media,
									fields='id').execute()
		print('File ID: %s' % file.get('id'))
		return file

	def create_diary(self,folder_id,title):

		curdate = datetime.datetime.now()-datetime.timedelta(hours=3)
		curdate.weekday()
		name = f'{curdate.month:02d}월 {curdate.day:02d}일 {get_weekday(curdate)}요일 - {title}'

		return self.create_doc(folder_id,name)

	def get_subfolders(self):
		page_token = None
		q=f"parents in '1nxWaOdPzGGcS7yM-Tf_9J3FLexF6ptvf'"
		q = "mimeType = 'application/vnd.google-apps.folder'"
		response = self.DRIVE.files().list(
			q=q,
			spaces='drive',
			fields='nextPageToken, files(id, name)',
			pageToken=page_token).execute()
		for file in response.get('files', []):
			# Process change
			print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
		pass


def create_exam():
	dir_file = os.path.dirname(__file__)

	secrete_file = dir_file + '/client_secret_476383775373-192qipsl35ec4g3hf7ue11v4464j8mp0.apps.googleusercontent.com.json'
	folder_id = '1nxWaOdPzGGcS7yM-Tf_9J3FLexF6ptvf'  # test
	inst = HandlingDiaryGDocs.get_build_drive(secrete_file)
	inst.create_doc(folder_id,"테스트 문서")
	#print(inst.get_subfolders())


	pass

if __name__ == '__main__':
	create_exam()


