from selenium import webdriver
from time import sleep
#https://raspberrypi.stackexchange.com/questions/4941/can-i-run-selenium-webdriver-using-firefox-as-the-browser

driver_path ='C:/app/python38/chromedriver_110/chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(driver_path, options=options)
#driver = webdriver.Chrome(options=options)
#url = 'https://example.com'
url = 'https://comic.naver.com/webtoon'
driver.get(url)


#sleep(5) # wait for 5 seconds to load the page
page_source = driver.page_source
#element = driver.find_element_by_css_selector('div.example-class')
print(page_source)
driver.quit()