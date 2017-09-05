#coding:utf-8

import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

client = pymongo.MongoClient('localhost', 27017)
ceshi = client['qunawang']
item_infoA = ceshi['hotel']

class QunaSpider(object):


    def get_hotel(self,driver, to_city,fromdate,todate):
        '''通过selenium获取目的地框、入住时间、离店时间和搜索按钮的元素，输入内容，并点击搜索按钮'''
        ele_toCity = driver.find_element_by_name('toCity')   #获取目的地框
        ele_fromDate = driver.find_element_by_id('fromDate')  #入住时间
        ele_toDate = driver.find_element_by_id('toDate')   #离店时间
        ele_search = driver.find_element_by_class_name('search-btn')   #搜索按钮
        ele_toCity.clear()
        ele_toCity.send_keys(to_city)    #输入目的地
        ele_toCity.click()
        ele_fromDate.clear()
        ele_fromDate.send_keys(fromdate)  #输入入住时间
        ele_toDate.clear()
        ele_toDate.send_keys(todate)    #输入离店时间
        ele_search.click()
        page_num=0
        while True:

            '''等待加载时间'''
            try:
                WebDriverWait(driver, 10).until(
                    EC.title_contains(unicode(to_city))
                )
            except Exception,e:
                print e
                break
            time.sleep(5)

            '''向滚动条置底，获取完整的页面数据'''
            js = "window.scrollTo(0, document.body.scrollHeight);"
            driver.execute_script(js)
            time.sleep(5)

            '''使用BwautifulSoup解析酒店信息，并将数据进行清洗和存储'''
            try:
                htm_const = driver.page_source
                soup = BeautifulSoup(htm_const,'html.parser', from_encoding='utf-8')
                hotel_titles = soup.select('span.hotel_item a')
                hotel_addrs = soup.select(' p.adress  span.area_contair')
                hotel_scores = soup.select('p.score a b')
                hotel_prices = soup.select('p.item_price.js_hasprice a b')
                for hotel_title,hotel_addr,hotel_score,hotel_price in zip(hotel_titles,hotel_addrs,hotel_scores,hotel_prices):
                    hotel_urls = hotel_title.get('href')
                    if 'http://bnb.qunar.com' not in hotel_urls:
                        data = {
                            '酒店': hotel_title.get_text().strip(),
                            '酒店地址': hotel_addr.get_text().strip(),
                            '酒店评分': hotel_score.get_text().strip(),
                            '酒店价格': hotel_price.get_text().strip(),
                            '酒店链接': 'http://hotel.qunar.com' + hotel_urls
                        }
                        print data
                        item_infoA.insert_one(data)
                    else:
                        data = {
                            '酒店': hotel_title.get_text().strip(),
                            '酒店地址': hotel_addr.get_text().strip(),
                            '酒店评分': hotel_score.get_text().strip(),
                            '酒店价格': hotel_price.get_text().strip(),
                            '酒店链接': hotel_urls
                        }
                        print data
                        item_infoA.insert_one(data)
            except Exception,e:
                print e
                break

            try:
                next_page = WebDriverWait(driver, 10).until(
                EC.visibility_of(driver.find_element_by_css_selector('ul > li.item.next'))
                )
                next_page.click()
                page_num+=1
                time.sleep(10)
            except Exception,e:
                print e
                break

    def crawl(self,root_url,to_city):
         today = datetime.date.today().strftime('%Y-%m-%d')
         tomorrow=datetime.date.today() + datetime.timedelta(days=1)
         tomorrow = tomorrow.strftime('%Y-%m-%d')
         driver = webdriver.Chrome()
         driver.set_page_load_timeout(50)
         driver.get(root_url)
         driver.maximize_window() # 将浏览器最大化显示
         driver.implicitly_wait(10) # 控制间隔时间，等待浏览器反映
         self.get_hotel(driver,to_city,today,tomorrow)


if __name__=='__main__':
    spider = QunaSpider()
    spider.crawl('http://hotel.qunar.com/',u"上海")
