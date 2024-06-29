import sys
sys.path.insert(0,'/var/www/neo_server')
print(sys.path)
from neo_server import main_server
main_server.init()
from neo_server.main_server import app as application



