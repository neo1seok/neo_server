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
	def run(self):
		ret = requests.get(self.url)

		#img_src_patt = r'<img\s+src="([^"]+)"\s+alt="([^"]+)"\s*/'

		rmoved = re.sub(self.img_src_patt, "", ret.text)
		def append_map(key,contnets):
			list_obj = self.map_img_src.get(key, [])
			list_obj.append(contnets)
			self.map_img_src[key] = list_obj
			pass


		key_word = ['04_Lineup/04_1_전체현황/', '04_Lineup/04_2_실시간/', '06_ETC/']
		fi = open("out/out.txt","w")
		comp = re.compile(self.patt_realtime)
		comp2 =re.compile(self.patt_summary)
		for img, alt in re.findall(self.img_src_patt, ret.text):
			is_ok = False
			conv_img = unquote(img).replace(self.patt_remove_str, "")
			fi.write(conv_img + "\n")
			match = comp.search(conv_img)
			match2 = comp2.search(conv_img)
			if match == None and match2==None and conv_img != "06_ETC/전화연결.gif":
				continue
			if match:
				day_night = match.group(1)
				name = match.group(2)
				append_map("실시간",dict(day_night=day_night,name=name,url=img))
				# list_real_time = self.map_img_src.get("실시간",[])
				# list_real_time.append(dict(day_night=day_night,name=name,url=img))
				# self.map_img_src["실시간"] = list_real_time
				# print(day_night,name)
			if match2:
				day_night_real = match2.group(1)
				append_map("출근현황", dict(day_night=day_night_real, name='출근현황', url=img))
				# attendance = self.map_img_src.get("출근현황", [])
				# attendance.append(dict(day_night=day_night_real, name='출근현황', url=img))
				# self.map_img_src["실시간"] = attendance
				#
				# print("출근현황", day_night_real)
			if conv_img == "06_ETC/전화연결.gif":
				self.map_img_src['전화'] = [dict( name='전화', url=img)]
				# attendance = self.map_img_src['전화'].get("전화", [])
				# append_map("전화", dict( name='전화', url=img))

			#self.map_img_src

			# for word in key_word:
			# 	if word in conv_img:
			# 		is_ok = True
			# if not is_ok:
			# 	continue
			file = conv_img.split('/')[-1]
			#download(img, "out/" + file)

			#print(conv_img)



		#print(self.mapTopid)
		return self
	pass

if __name__ == '__main__':
	map_list = GetShowDailyInfo().run().get_contents()
	print([ tmp['name'] for tmp in map_list['실시간'] if tmp['day_night']=='야간'])

	for key,val in map_list.items():
		#print(key,val)
		for tmp in val:
			print(tmp)

