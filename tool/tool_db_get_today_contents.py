import pymysql
from neolib import neoutil
map_db_info = {
			"host": "192.168.0.27",
			"port": 3306,
			"user": "neo1seok",
			"passwd": "tofhdna1pi",
			"db": "",
			"charset": "utf8"
		}
conn = pymysql.connect(**map_db_info)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("""
	SELECT seq, tdc_uid, title, issue, solution, status, etc, updt_date, reg_date, comment 
FROM neo_pwinfo.today_contents;
;""")
list_map = cur.fetchall()

body ="""
*TITLE:
{title}

*ISSUE:
{issue}

*SOLUTION:
{solution}
"""
for tmp in list_map:
	with open("out/{}.txt".format(tmp['title']),"w",encoding="utf-8") as of:
		of.write(body.format(**tmp))
		print(body.format(**tmp))
	#wtn_uid = tmp['wtn_uid']
	# cur.execute(sql_dateinfo.format(wtn_uid = wtn_uid))
	# list_dates = cur.fetchall()
	# str_todays = "|".join([date['date'] for date in list_dates])
	# print(wtn_uid,str_todays)
	# cur.execute(sql_update.format(dates=str_todays,wtn_uid=wtn_uid))
