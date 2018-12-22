
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
#要搜尋的網址:
#MIS  #IOT
name="class3"

com_name_list=[]
job_url_list=[]
search_url_list=[]
job_name_list=[]
for i in range(1,9):
    #針對職缺名稱搜尋的url ↓
    #search_url = "https://www.104.com.tw/area/freshman/search?keyword={}&page={}&area=&jobcategory=2007000000&industry=".format(name,i)
    #針對職缺類別搜尋的url ↓
    search_url="https://www.104.com.tw/area/freshman/search?keyword=&page={}&area=&jobcategory=2013000000%2C2014000000%2C2016000000&industry=".format(i)
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
        job_name_list.append(job_name)

#將職務的連結存入CSV
job_url_filename="{}output.csv".format(name)
df = pd.DataFrame(job_url_list,columns = ['JOB URL'])
df.to_csv(job_url_filename, encoding='utf_8_sig')
  


content_list=[]
condition_list=[]      
job_url_row=len(job_url_list)
       
for com_row in range(0,job_url_row):
    res = requests.get(job_url_list[com_row], headers = head)
    res.encoding = 'utf8'
    soup = bs(res.text, "lxml")        
    #工作內容
    content1=soup.select(".content")[0].select('p')[0].text.replace('\r','')
    
    #工作條件
    content2=soup.select(".content")[1].text.replace('\r','').replace('\n','')
    content_list.append(content1)
    condition_list.append(content2)

v=" "
content_list.append("~你是孩子們的大朋友~ 這是一份充滿學習與挑戰的工作！ 你的身分隨時都在轉變，可能是他們心中最佩服的孩子王 更可能是家長心中可靠的橋樑； 歡迎你前進孩子Fun課後的小天地！ 1.學童接送 2.國小孩童課後輔導、複習 3.班級經營及親師溝通 4.教室環境佈置維護 5.寒暑假學藝課程規劃及教學職務類別：安親班老師、國小學校教師、幼教班老師 工作待遇：月薪 2萬7仟元 至 2萬9仟元工作性質：全職上班地點：台北市文山區(依照公司規定分派) 管理責任：不需負擔管理責任出差外派：無需出差外派上班時段：日班，08:00~17:00休假制度：週休二日可上班日：一個月內需求人數：1至2 人")
condition_list.append("接受身份：上班族、應屆畢業生工作經歷：不拘學歷要求：大學以上科系要求：不拘語文條件：英文 -- 聽 /略懂、說 /略懂、讀 /略懂、寫 /略懂擅長工具：不拘工作技能：不拘其他條件：1.高中職以上幼教相關科系畢業，或具助理教保員資格， 2.對幼兒教育有熱忱 3.喜愛孩子，個性細心、耐心")

output_filename="{}_content_output.csv".format(name)
df = pd.DataFrame(
    {'公司名稱': com_name_list,
     '職缺名稱': job_name_list,
     '工作內容': content_list,
     '工作條件': condition_list
    })
df.to_csv(output_filename, encoding='utf_8_sig')




