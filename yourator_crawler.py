# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 17:12:58 2018

@author: Administrator
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import mysql.connector


com_name_list=[]
com_url_list=[]

search_url_list=[]


#針對職缺類別搜尋的url ↓
search_url="https://www.yourator.co/events/2019YouratorSpringJobFair"
  

head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4'} 


res = requests.get(search_url, headers = head)
res.encoding = 'utf8'
soup = bs(res.text, "lxml")

#進入公司的頁面
com_box = soup.select(".adjust-rwd-col")
com_box_num=len(com_box)
for item in range(0,com_box_num):
    print(item)
    com_box = soup.select(".adjust-rwd-col")[item]
    print(com_box)
    com_url="https://www.yourator.co" +com_box.select(".y-card-content-title")[0].select('a')[0]['href'] #com url
    print(com_url)
    
    com_name=com_box.select(".y-card-content-title")[0].select('a')[0].text.replace('\t','').replace('\r\n','').replace('\n','')    #company name
    print(com_name)
    
    com_name_list.append(com_name)
    com_url_list.append(com_url)
 



#進入公司職缺的頁面
job_url_list=[]
job_name_list=[]
com_title_list=[]
com_num=len(com_name_list)
for index in range(0,com_num):
    
    res = requests.get(com_url_list[index], headers = head)
    res.encoding = 'utf8'
    soup = bs(res.text, "lxml")

    job_box = soup.select(".y-card-content")
    job_box_num=len(job_box)
    
    for item in range(0,job_box_num):
        job_box = soup.select(".y-card-content")[item]

        
        job_url="https://www.yourator.co" +job_box.select(".y-card-content-title")[0].select('a')[0]['href'] #job url

        job_name=job_box.select(".y-card-content-title")[0].select('a')[0].text.replace('\t','').replace('\r\n','').replace('\n','')    #job name
        
        com_title=com_name_list[index]
        
        com_title_list.append(com_title)
        job_name_list.append(job_name)
        job_url_list.append(job_url)
        
        
#進入公司職確的工作內容頁面 
job_content_list=[]      
job_num=len(job_name_list)     
for index in range(0,job_num):
    res = requests.get(job_url_list[index], headers = head)
    res.encoding = 'utf8'
    soup = bs(res.text, "lxml")
    content_box=soup.select(".job-description")[0]
    cont=content_box.select('article')[0].text.replace('\t','').replace('\r\n','').replace('\n','')    #job content
    cond=content_box.select('article')[1].text.replace('\t','').replace('\r\n','').replace('\n','')    #condition ask
    
    job_content=cont+cond
    job_content_list.append(job_content)
        


#寫入csv
output_filename="Yourator_jobContentOutput.csv"
df = pd.DataFrame(
    {'公司名稱': com_title_list,
     '職缺url': job_url_list,
     '職缺名稱': job_name_list,
     '職缺內容': job_content_list
    })
df.to_csv(output_filename, encoding='utf_8_sig')


#寫入mtsql db

conn = mysql.connector.connect(user='jobRecommend', password='xOsIhwgaFIfm8nqf',
                              host='35.160.71.183',
                              database='job_recommendation')

data_row=len(com_title_list)#讀取資料幾筆
for i in range(0,data_row):
    
    mycursor = conn.cursor()
    companyName=str(com_title_list[i])
    positionURL=str(job_url_list[i])
    positionTitle=str(job_name_list[i])
    positionContent=str(job_content_list[i])
    sql = "INSERT INTO yourator_job (companyName, positionURL, positionTitle, positionContent) VALUES ('{}','{}','{}','{}')".format(companyName, positionURL, positionTitle, positionContent)
    print(sql)
    try:
        mycursor.execute(sql)
        conn.commit()
    except:
        print(i)
conn.close()
