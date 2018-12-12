
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
#要搜尋的網址:
#MIS  #IOT
name="MIS"

com_name_list=[]
job_url_list=[]
search_url_list=[]
for i in range(1,9):
    search_url = "https://www.104.com.tw/area/freshman/search?keyword={}&page={}&area=&jobcategory=2007000000&industry=".format(name,i)
    search_url_list.append(search_url)
    

head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4'} 
search_url_row=len(search_url_list)




for url_row in range(search_url_row):
    res = requests.get(search_url_list[url_row], headers = head)
    res.encoding = 'utf8'
    soup = bs(res.text, "lxml")
    for item in range(0,20):
        
        job_box = soup.select(".job_box")[0]
        joblist=job_box.select('.joblist_cont')[item]
        #job_name = joblist.select('a')[0]['title']    #job name
        job_name = joblist.select(".jobname")[0].select('a')[0]['title'] #job name
        com_name = joblist.select('a')[1]['title']    #company name
        #com_name01 = joblist.select(".compname")[0].text.replace('\t','').replace('\r\n','').replace('\n','')    #company name
        
        #edu = joblist.select(".edu")[0].text.replace('\t','').replace('\r\n','')   #學歷
        #area = joblist.select(".area")[0].text.replace('\t','').replace('\r\n','') #工作地點在哪個市區
        job_url = "https://www.104.com.tw" + joblist.select(".jobname")[0].select('a')[0]['href']       #職缺網頁
        #com_url = "https://www.104.com.tw" + joblist.select('a')[1]['href']        #公司簡介網頁
        job_url_list.append(job_url)
        com_name_list.append(com_name)
       

#將職務的連結存入CSV
job_url_filename="{}output.csv".format(name)
df = pd.DataFrame(job_url_list,columns = ['JOB URL'])
df.to_csv(job_url_filename, encoding='utf_8_sig')
  


content_list=[]
condition_list=[]      
job_url_row=len(job_url_list)
       
for com_row in range(117,job_url_row):
    res = requests.get(job_url_list[com_row], headers = head)
    res.encoding = 'utf8'
    soup = bs(res.text, "lxml")        
    #工作內容
    content1=soup.select(".content")[0].select('p')[0].text.replace('\r','')
    
    #工作條件
    content2=soup.select(".content")[1].text.replace('\r','').replace('\n','')
    content_list.append(content1)
    condition_list.append(content2)


output_filename="{}_content_output.csv".format(name)
df = pd.DataFrame(
    {'工作內容': content_list,
     '工作條件': condition_list
    })
df.to_csv(output_filename, encoding='utf_8_sig')



