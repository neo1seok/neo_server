import requests

r = requests.post('http://localhost:5555/query/webtoon/update_custom', data=dict(id="tdc_5"))
print(r.text)

r = requests.post('http://localhost:5555/query/keyword_order/update_custom', data=dict(id="tdc_5"))
print(r.text)