import base64

import pymysql
from neolib import neoutil
#from Crypto.Hash import SHA256
from Crypto.Cipher import AES

map_db_info = {
			"host": "localhost",
			"port": 3306,
			"user": "neo1seok",
			"passwd": "tofhdna1pi",
			"db": "",
			"charset": "utf8"
		}
conn = pymysql.connect(**map_db_info)
cur = conn.cursor(pymysql.cursors.DictCursor)

cipher = AES.new(b'0'*32, AES.MODE_CBC, b'\x00'*16)
cipher.encrypt(b'saffsafas')
encoded_text = base64.b64encode(b'aadfasffasffdsdfas')

print(encoded_text)


cur.execute("""
	SELECT seq, pwd_uid, phd_uid, site, ptail, id, etc, status, updt_date, reg_date, comment 
FROM neo_pwinfo.passwd;;""")
list_map = cur.fetchall()
neoutil.simple_view_list(list_map)