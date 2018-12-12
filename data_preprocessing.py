# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 15:43:23 2018

@author: Administrator
"""
import jieba, csv,mysql.connector

import pandas as pd
from hanziconv import HanziConv


def Start(load_file):
    dfrme = {}
    with open(load_file, 'r',encoding = 'utf8') as f:
        reader = csv.DictReader(f)
        list_1 = [e for e in reader]  # 每行資料作為一個dict存入連結串列中
        f.close()
        dfrme = pd.DataFrame.from_records(list_1)
        
    #dataframe to list    
    job_content=dfrme['工作內容'].tolist()
    
    work_cont=dfrme['工作內容']
    job_condition=dfrme['工作條件'].tolist()
    work_cond=dfrme['工作條件']
    
    cont_seg_list,cond_seg_list=Jieba_segment(work_cont,work_cond)
   
    
    """
    #two lists to one list
    job_lists=[]
    job_lists=job_content+job_condition
    
    #list to string
    job_str = ' '.join(job_lists) 
    
    #call function "Segment"
    seg_list=Segment(job_str,pos)
    #print(seg_list)
    """
    #call function "Remove_stopwords"
    cont_list,cond_list=simple_to_traditional(cont_seg_list,cond_seg_list)
    
    #return cont_list,cond_list
    cont_filter_list,cond_filter_list=Remove_stopwords(cont_list,cond_list)
    return cont_filter_list,cond_filter_list


def Jieba_segment(work_cont,work_cond):
    #为主词典即优先考虑的词典,原词典此时变为非主词典
    jieba.load_userdict(".\\dict_for_jieba\\dict.txt")
    cont_seg_list=[]
    cond_seg_list=[]
    
    #jieba.load_userdict(".\\dict_for_jieba\\dict.txt")
    jieba.initialize()
    

    
    for i in range(len(work_cont)):
        sim_sent=HanziConv.toSimplified(work_cont[i])
        str_load=jieba.lcut(sim_sent)
        #job_output_str="/".join(str_load) #string
      
        #trad_sent=HanziConv.toTraditional(str_load)
        cont_seg_list.append(str_load)
    #print(len(cont_seg_list))


    for i in range(len(work_cond)):
        sim_sent=HanziConv.toSimplified(work_cond[i])
        str_load=jieba.lcut(sim_sent)
        #job_output_str="/".join(str_load) #string
        #trad_sent=HanziConv.toTraditional(str_load[i])
        cond_seg_list.append(str_load)
    
    return cont_seg_list,cond_seg_list



def get_stopword_list():
     #加载停用词表
    conn = mysql.connector.connect(user='ilovejobot', password='ot2BcE3v6IYB9de5',
                                  host='localhost',
                                  database='jobot')
    cur =conn.cursor()
    cur.execute ( "SELECT * FROM nlp_stopwords" )
    
    stop_tuple=()
    for stop in cur.fetchall (): 
        stop_tuple=stop_tuple+(stop)
      
    stop_list=list(stop_tuple)
    
    
    # jieba.load_userdict('userdict.txt')  
    # 创建停用词list      
    # 这里加载停用词的路径  
    return stop_list


#將簡體的斷詞結果變繁體
def simple_to_traditional(cont_seg_list,cond_seg_list):   
    
    cont_list=[]
    cond_list=[]
    
    for n in cont_seg_list:   
        word_list=[]
        for i in range(len(n)):
            word=HanziConv.toTraditional(n[i])
            word_list.append(word)
        cont_list.append(word_list) 
    print(len(cont_list))     
        
    for n in cond_seg_list:   
        word_list=[]
        for i in range(len(n)):           
            word=HanziConv.toTraditional(n[i])
            word_list.append(word)
        cond_list.append(word_list)
    print(len(cond_list))     
        
    return cont_list,cond_list
    
    
    
#停用詞過濾
def Remove_stopwords(cont_list,cond_list):
    stopwords_list=get_stopword_list()
   
    #停用詞過濾
    outstr ="" 
    cont_filter_list=[]
    cond_filter_list=[]
    
    
    for n in cont_list: 
        word_list=[]
        for i in range(len(n)):
            word=n[i]
            if word not in stopwords_list:  
                if word != '\t' or word != '\n' :  
                    outstr += word  
                    outstr += " "
                    word_list.append(word)
        cont_filter_list.append(word_list)
    
    
    for n in cond_list: 
        word_list=[]
        for i in range(len(n)):
            word=n[i]
            if word not in stopwords_list:  
                if word != '\t' or word != '\n' :  
                    outstr += word  
                    outstr += " "
                    word_list.append(word)
        cond_filter_list.append(word_list)
        
        
    
    #outstr = " ".join(outstr.split()) #將\n \t 去掉
       
    
    

    #print(cond_filter_list)     
    #outstr = " ".join(outstr.split()) #將\n \t 去掉  
    # 过滤停用词表中的词，以及长度为<2的词
    """if not word in word_list and len(word) > 1:
        word_list.append(word)
        """
    return cont_filter_list,cond_filter_list

    
    #return [w for w in job_output if w not in stopwords]






        
if __name__=='__main__':
    pos=True
    filename="MIS"
    load_file="{}_content_output.csv".format(filename)
    #call function "Start"
    #doc_list=Start(load_file)
    cont_filter_list,cond_filter_list=Start(load_file)
    #print(cont_seg_list[1][2])
    
