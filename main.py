"""
    Written by Yusuf ÖZKAN

    A web scraper bot with specific e-commerce website in Turkey. 

"""
from numpy import row_stack
import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
from lxml import html
from lxml.html import fromstring
import random
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy

proxy_list = list()
keyword_list = list()
category_list = list()
mydict = dict()
not_found = 0  # if keyword not found

def proxy(): # get random proxies 

    proxies = list()
    req_proxy = RequestProxy() 
    proxiess = req_proxy.get_proxy_list() 

    for proxy in proxiess:
        proxies.append(proxy)

    return proxies

def read_excel(): # returns excel keyword list
    
    global keyword_list

    df = pd.read_excel("data.xlsx")
    temp_list = df.values.tolist()

    for k in temp_list:
        for l in k:
            keyword_list.append(l)

    return keyword_list

def run():
    global proxy_list
    global category_list
    global keyword_list
    global not_found
    global mydict

    proxy_counter = 0  # for update proxy list periodically

    headers = {'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    session = requests.Session()
    session.headers.update(headers)
    proxies = proxy()

    for query in keyword_list:

        try:
            query = urllib.parse.quote(query) # converts string to url encoded
            print(query)

            url = f"https://www.trendyol.com/sr?q={query}&qt={query}&st={query}&os=1"

            if proxy_counter > 350:
                proxies = proxy()
                proxy_counter = 0

            selected = random.choice(proxies)
            proxy_counter += 1
            session.proxies = selected
            response = session.get(url , timeout=1.5)
            
            if response.status_code == 200:
                write_excel(category_list)
                print("status code :"+ str(response.status_code))
                soup =  BeautifulSoup(response.content, "lxml")  # getting websites content

                try:
                    items = soup.find("div" , attrs= {"class":"p-card-chldrn-cntnr"})
                    temp_link = items.find("a").get("href")
                    link = "https://www.trendyol.com"+temp_link
                    print(link)
                
                    url2 = link
                    response2 = session.get(url2 , timeout=1.5)
                    tree = html.fromstring(response2.content)
                    category = tree.xpath('//*[@id="product-detail-app"]/div/div[2]/a[2]/@title')
                    strobj = str(category[0])

                    print(strobj)
                    category_list.append(category)
                    mydict[query] = category # to control data pair

                except:
                    not_found += 1
                    category_list.append("-")  # if keyword is broken
                    mydict[query] = "-"
                    continue
            else:
                not_found += 1
                category_list.append("-")  # if connection is broken
                mydict[query] = "-"
                continue
        except:
            not_found += 1
            category_list.append("-")  # if request is broken
            mydict[query] = "-"
            continue

def write_excel(data): # writes to new excel file as 'result.xlsx'
    
    df =  pd.DataFrame(data)
    df.to_excel('result.xlsx', header=False, index=False)

if __name__ == "__main__":
        
    read_excel()  # updated keyword_list globally
    run() 
    write_excel(category_list) # creates and writes to excel file
    print(str(not_found)+" keyword not found")
    #print(mydict) # shows data pairs

    