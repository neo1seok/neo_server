import sys
sys.path.insert(0,'/var/www/neo_server')
print(sys.path)
import main_server
main_server.init()
from main_server import app as application



