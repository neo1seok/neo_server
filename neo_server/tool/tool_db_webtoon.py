import pymysql
from neolib import neoutil
map_db_info = {
			"host": "192.168.0.17",
			"port": 3306,
			"user": "neo1seok",
			"passwd": "tofhdna1pi",
			"db": "",
			"charset": "utf8"
		}
conn = pymysql.connect(**map_db_info)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
	SELECT * 
	FROM neo_pwinfo.webtoon;""")
list_map = cur.fetchall()
sql_dateinfo = '''
SELECT seq, dte_uid, wtn_uid, `date`, updt_date, reg_date, comment 
FROM neo_pwinfo.date_webtoon where wtn_uid = '{wtn_uid}';

'''

sql_update = '''
UPDATE neo_pwinfo.webtoon
SET
  dates = '{dates}' -- varchar(32)
WHERE wtn_uid = '{wtn_uid}' -- varchar(20)
'''

for tmp in list_map:
	wtn_uid = tmp['wtn_uid']
	cur.execute(sql_dateinfo.format(wtn_uid = wtn_uid))
	list_dates = cur.fetchall()
	str_todays = "|".join([date['date'] for date in list_dates])
	print(wtn_uid,str_todays)
	cur.execute(sql_update.format(dates=str_todays,wtn_uid=wtn_uid))
