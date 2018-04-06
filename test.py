#!/usr/bin/python3

import os
cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))
print(os.path.abspath(__file__))
print(dir_path,cwd,__file__)
open('rsc/webinfo.json')

