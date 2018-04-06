import requests

r = requests.post('http://localhost/query/todaycontents/get_content', data=dict(id="tdc_5"))
print(r.text)

r = requests.post('http://localhost/query/portal_order/update', data=dict(id="tdc_5"))
print(r.text)