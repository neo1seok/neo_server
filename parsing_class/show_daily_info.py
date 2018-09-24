from io import StringIO

from neolib import neo_class
import requests

from neolib import neoutil
import re
from urllib.parse import unquote
import os
def download(url, file_name):
	# open in binary mode
	with open(file_name, "wb") as file:
		# get request
		response = requests.get(url)
		# write to file
		file.write(response.content)

class GetShowDailyInfo(neo_class.NeoRunnableClass):
	url = 'https://www.koreaspot.com/profile/21130/'
	img_src_patt = r'<img\s+src="([^"]+)"\s+alt="([^"]+)"\s*/'
	patt_summary=r'04_Lineup/04_1_전체현황/출근현황-([가-힣]+).png'
	patt_realtime = r'04_Lineup/04_2_실시간/([가-힣]+)/([\w가-힣 \-]+)-mini\.gif'
	patt_remove_str ='http://369am.diskn.com/맛동산/'
	cmp_str = "06_ETC/전화연결.gif"

	def __init__(self):
		neo_class.NeoRunnableClass.__init__(self)
		self.map_img_src = {}
	def get_contents(self):
		return self.map_img_src
	def parsing(self,text):
		#rmoved = re.sub(self.img_src_patt, "", ret.text)

		def append_map(key, contnets):
			list_obj = self.map_img_src.get(key, [])
			list_obj.append(contnets)
			self.map_img_src[key] = list_obj
			pass

		key_word = ['04_Lineup/04_1_전체현황/', '04_Lineup/04_2_실시간/', '06_ETC/']

		comp = re.compile(self.patt_realtime)
		comp2 = re.compile(self.patt_summary)
		for img, alt in re.findall(self.img_src_patt, text):
			is_ok = False
			conv_img = unquote(img).replace(self.patt_remove_str, "")
			#fi.write(conv_img + "\n")
			match = comp.search(conv_img)
			match2 = comp2.search(conv_img)
			if match == None and match2 == None and conv_img != "06_ETC/전화연결.gif":
				continue
			if match:
				day_night = match.group(1)
				name = match.group(2)
				if name == "팅커벨":
					append_map("팅커벨", dict(day_night=day_night, name=name, url=img))
					#continue
				append_map("실시간", dict(day_night=day_night, name=name, url=img))
			# list_real_time = self.map_img_src.get("실시간",[])
			# list_real_time.append(dict(day_night=day_night,name=name,url=img))
			# self.map_img_src["실시간"] = list_real_time
			# print(day_night,name)
			if match2:
				day_night_real = match2.group(1)
				append_map("출근현황", dict(day_night=day_night_real, name=day_night_real +' 출근현황', url=img))
			# attendance = self.map_img_src.get("출근현황", [])
			# attendance.append(dict(day_night=day_night_real, name='출근현황', url=img))
			# self.map_img_src["실시간"] = attendance
			#
			# print("출근현황", day_night_real)
			if conv_img == "06_ETC/전화연결.gif":
				self.map_img_src['전화'] = [dict(name='전화', url=img)]
			# attendance = self.map_img_src['전화'].get("전화", [])
			# append_map("전화", dict( name='전화', url=img))

			# self.map_img_src

			# for word in key_word:
			# 	if word in conv_img:
			# 		is_ok = True
			# if not is_ok:
			# 	continue
			file = conv_img.split('/')[-1]

	# download(img, "out/" + file)

	# print(conv_img)

	def simul(self):
		text = neoutil.StrFromFile( "out/contents.out")
		self.parsing(text)
		return self
	def run(self):
		ret = requests.get(self.url)

		self.parsing(ret.text)
		neoutil.StrToFile(ret.text,"out/contents.out")

		#img_src_patt = r'<img\s+src="([^"]+)"\s+alt="([^"]+)"\s*/'





		#print(self.mapTopid)
		return self

	def get_html(self):
		map_list = self.get_contents()
		real_time = map_list['실시간']
		tinca = map_list.get('팅커벨',"")
		phone = map_list['전화'][0]
		status = map_list['출근현황']
		print(phone)
		print(real_time)
		fmt_real_time = "<a href='{url}'>{name}</a>"
		#{'day_night': '주간', 'name': '봉봉', 'url': 'http://369am.diskn.com/%EB%A7%9B%EB%8F%99%EC%82%B0/04_Lineup/04_2_%EC%8B%A4%EC%8B%9C%EA%B0%84/%EC%A3%BC%EA%B0%84/%EB%B4%89%EB%B4%89-mini.gif'}
		sio = StringIO()
		sio.write(fmt_real_time.format(**phone))
		sio.write("<br/>" )

		ret =[fmt_real_time.format(url=self.url,name="원본"),fmt_real_time.format(**phone)]

		#ret['전화'] = [fmt_real_time.format(**phone)]

		def append_ret(list_dict,key_word,fmt = "<a href='{url}'>{name}</a>"):
			list_ret = []
			for tmp in list_dict:
				day_night = tmp['day_night']
				if day_night != key_word:
					continue
				# if not filter(tmp):
				# 	continue
				list_ret.append(fmt.format(**tmp))
			return list_ret
		#make_html = lambda list_ret : "".join([   "{} ".format(tmp ) + ("<br/>" if idx%4==0 else ",")for idx , tmp in enumerate(list_ret) ])
		make_html = lambda list_ret: "".join(
			["{} ".format(tmp)  for idx, tmp in enumerate(list_ret)])
		ret.extend(append_ret(status,'주간'))
		# sio.write(append_ret(status,'주간')[0])
		# sio.write("<br/>")
		ret.append(make_html(append_ret( real_time, '주간',fmt="{name}")))
		ret.append(make_html(append_ret(tinca, '야간')))



		# sio.write(make_html(append_ret( real_time, '주간')))
		# sio.write("<br/>")

		ret.extend(append_ret(status, '야간'))
		ret.append(make_html(append_ret(real_time, '야간',fmt="{name}")))
		#ret.extend(append_ret(real_time, '야간'))

		# sio.write(append_ret(status, '야간')[0])
		# sio.write("<br/>")
		#
		# sio.write(make_html(append_ret(real_time, '야간')))
		# sio.write("<br/>")
		#
		#
		# # append_ret( status, '야간')
		# # append_ret( real_time, '야간')
		#
		# neoutil.simple_view_list(ret)
		return ret
		# for tmp in status:
		# 	day_night = tmp['day_night']
		# 	subdict = ret.get(day_night, [])
		# 	subdict.append(fmt_real_time.format(**tmp))
		# 	ret[day_night] = subdict
		#
		# for tmp in real_time:
		# 	day_night = tmp['day_night']
		# 	subdict = ret.get(day_night,[])
		# 	subdict.append(fmt_real_time.format(**tmp))
		# 	ret[day_night] = subdict
		# print(ret['주간'])
		# print(ret['야간'])
		#



if __name__ == '__main__':

	result = GetShowDailyInfo().simul().get_html()
	neoutil.StrToFile(result,"out/out.html")
	exit()
	map_list = GetShowDailyInfo().run().get_contents()
	print([ tmp['name'] for tmp in map_list['실시간'] if tmp['day_night']=='야간'])
	print(map_list)
	real_time = map_list['실시간']
	phone = map_list['전화']
	status = map_list['출근현황']

	for key,val in map_list.items():
		print(key)
		for tmp in val:
			print(tmp)

