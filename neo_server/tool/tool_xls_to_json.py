from neolib import neoutil,xlrd_util
import json
def main():
	list_lines = xlrd_util.get_lines_from_xls_by_index('../rsc/neoserver_page_info.xlsx',0)
	#neoutil.simple_view_list(list_lines)
	title_name = list_lines[0]
	content = [     { title_name[idx]:col for idx, col in enumerate(line) }for line  in list_lines[1:]]




	neoutil.StrToFile(neoutil.json_pretty(content),'../rsc/webinfo.json')
	#json.dump(content,open('../rsc/webinfo.json','w'))

	new_content = json.load(open('../rsc/webinfo.json',encoding='utf-8'))
	neoutil.simple_view_list(new_content)

if __name__ == '__main__':
	main()