from neolib import neoutil,neo_class
import neolib.neoutil as neolib
import neolib.db as neodb
import time

import   json
import re
import collections

class CreateTableAnd(neodb.MakeCreateTableFor):
	xlsDbFile = "../rsc/DB설계서.xlsx"
	def doRun(self):
		ret = self.makeMapFromExcel(self.xlsDbFile)
		self.strlines = self.makeSqlDropAndCreate(ret,self.createTableForm,self.fieldForm)
		neolib.StrToFile(self.strlines, "table/TABLE.SQL")
		self.strlines = self.makeSqlDropAndCreate(ret, self.dropTableForm, '')
		neolib.StrToFile(self.strlines, "table/DROP.SQL")

		None
class CreateClass(neodb.MakeDataFieldsClass):
	xlsDbFile = "../rsc/DB설계서.xlsx"

	def doRun(self):
		self.convert();





if __name__ != '__main__':
	exit()


CreateTableAnd().Run()
CreateClass().Run()