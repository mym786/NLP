# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 15:43:23 2018

@author: Administrator
"""
import jieba, csv,mysql.connector
import jieba.posseg as psg
import pandas as pd
from hanziconv import HanziConv
#textrank
from textrank4zh import TextRank4Keyword

import jieba.analyse 
jieba.analyse.set_idf_path(".\\for_tfidf\\idf.txt") #似乎沒用(改Model)

#count TF
from sklearn.feature_extraction.text import CountVectorizer
#count IDF
from sklearn.feature_extraction.text import TfidfTransformer
from gensim.models import word2vec

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
    """
    doc_list=[]
    doc_list.append(word_list)
    
    
    #call function "ComputeTF"
   
    return doc_list
    """

def Convert(string):
    #type string to list 
    li = list(string.split("/")) 
    return li

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

def String_to_list(data_string):
    #type string to list 
    data_list = list(data_string.split("/")) 
    return data_list

def List_to_string(data_list):
    data_string=" ".join(str(x) for x in data_list)
    return data_string


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
    
    #詞頻統計
    from collections import Counter
    c = Counter()
    
    for n in cont_list: 
        word_list=[]
        for i in range(len(n)):
            word=n[i]
            if word not in stopwords_list:  
                if word != '\t' or word != '\n' : 
                    word=word.lower()
                    outstr += word  
                    outstr += " "
                    word_list.append(word)                    
                    c[word]+=1 #詞頻計算
        word_str=' '.join(word_list)
        cont_filter_list.append(word_str)
    print('工作內容詞頻統計結果')
    df1=term_count(c)
     
    for n in cond_list: 
        word_list=[]
        for i in range(len(n)):
            word=n[i]
            if word not in stopwords_list:  
                if word != '\t' or word != '\n' : 
                    word=word.lower()
                    outstr += word  
                    outstr += " "
                    word_list.append(word)
                    c[word]+=1 #詞頻計算
        word_str=' '.join(word_list)
        cond_filter_list.append(word_str)
    print ('工作條件詞頻統計結果')
    df2=term_count(c)
   
    #========================================================================#

    df=df1.append(df2,ignore_index=True)
    csv_output="{}_TermCount.csv".format(filename)
    df_to_csv(df,csv_output)
    
    # 过滤停用词表中的词，以及长度为<2的词
    """if not word in word_list and len(word) > 1:
        word_list.append(word)
        """
    return cont_filter_list,cond_filter_list

#詞頻計算
def term_count(c): 

 
    list_a=[]
    list_b=[]
    
    for (k,v) in c.most_common(100):
        #print('%s  %d' % (k, v))
        list_a.append(k)
        list_b.append(v)
    data_tuples = list(zip(list_a,list_b))
    df=pd.DataFrame(data_tuples, columns=['term','count'])
    print(df)
    return df
  
     #return [w for w in job_output if w not in stopwords]

#將斷詞結果存入TXT
def list_to_txt(cont_filter_list,cond_filter_list):
    
    file1="{}_cond_after_filter.txt".format(filename)
    with open(file1, 'w', encoding='UTF-8') as f:
        for item in cond_filter_list:
            f.write("%s\n" % item) 
            
    file2="{}_cont_after_filter.txt".format(filename)
    with open(file2, 'w', encoding='UTF-8') as f:
        for item in cont_filter_list:
            f.write("%s\n" % item)
   
    
#新tfidf萃取:
def tfidf_kw(_filter_list):
    # 01、构建词频矩阵，将文本中的词语转换成词频矩阵
    vectorizer = CountVectorizer()

    # a[i][j]:表示j词在第i个文本中的词频
    trans_x = vectorizer.fit_transform(_filter_list)
    print(trans_x)  # 词频矩阵

    # 02、构建TFIDF权值
    transformer = TfidfTransformer()
    # 计算tfidf值
    tfidf = transformer.fit_transform(trans_x)

    # 03、获取词袋模型中的关键词
    word = vectorizer.get_feature_names()

    # tfidf矩阵
    weight = tfidf.toarray()
    
    # 打印权重
    list_a=[]
    list_b=[]
    for i in range(len(weight)):
        for j in range(len(word)):
            if weight[i][j] != 0.0 :
                print("{}: {}".format(word[j],weight[i][j]))
                list_a.append(word[j])
                list_b.append(weight[i][j])
                
    data_tuples = list(zip(list_a,list_b))
    df=pd.DataFrame(data_tuples, columns=['word','vector'])
    print(df)
    return df
    


def df_to_csv(df,csv_output):
    df.to_csv(csv_output, sep='\t', encoding='UTF-8')
    


        
if __name__=='__main__':
    pos=True
    filename="MIS"
    load_file="{}_content_output.csv".format(filename)

    cont_filter_list,cond_filter_list=Start(load_file)
    list_to_txt(cont_filter_list,cond_filter_list)
    
    #tfidf
    cont_vec_df=tfidf_kw(cont_filter_list)
    cond_vec_df=tfidf_kw(cond_filter_list)
    df=cont_vec_df.append(cond_vec_df,ignore_index=True)
    csv_output="{}_WordVector.csv".format(filename)
    df_to_csv(df,csv_output)
       
