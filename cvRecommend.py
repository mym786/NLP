# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 17:58:49 2018

@author: Administrator
"""

import sys

from hanziconv import HanziConv
import pandas as pd
import numpy as np
import mysql.connector, jieba, time, pickle #pickle模块


from sklearn import model_selection, preprocessing, linear_model, naive_bayes, metrics, svm
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn import decomposition, ensemble
from sklearn.metrics.pairwise import cosine_similarity,cosine_distances
from scipy.spatial import distance
from keras.preprocessing import text, sequence
from keras import layers, models, optimizers 

import heapq

#DISC
import disc

conn = mysql.connector.connect(user='jobRecommend', password='xOsIhwgaFIfm8nqf',
                              host='localhost',
                              database='job_recommendation')


#讀取PDF檔案內容
#pip install pdfminer3k  #pdf讀檔
from urllib.request import urlopen
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from io import open

def readPDF(pdfFile):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)

    process_pdf(rsrcmgr, device, pdfFile)
    device.close()

    content = retstr.getvalue()
    retstr.close()
    return content

def readCVContent(file_path):
    """顯示履歷"""
    #cv_file='2018-05-23-15-58-16.pdf'
    #查詢前，必須先獲取游標
    """
    cur =conn.cursor()
    sql="SELECT jobContent, jobCondition, positionClass FROM job_content Order by id DESC"
    #執行的都是原生SQL語句
    cur.execute(sql)
    cv_file=cur.fetchall()
    #cv_file.reverse()
    
    cv_file = ''.join(cv_file)
    print(cv_file)
    """
    #file_path="j156kt2"
    cv_file="C:/xampp/htdocs/eduai_jobot/module/NLP/file/{}.pdf".format(file_path)
    
    pdfFile=open(cv_file,"rb")
    #pdfFile = urlopen("http://www1.pu.edu.tw/~s1040204/autobiography.pdf")
    outputString = readPDF(pdfFile)
    
    pdfFile.close()
 
    return outputString
    

def Jieba_segment(work):
    #为主词典即优先考虑的词典,原词典此时变为非主词典
    jieba.load_userdict(".\\dict_for_jieba\\dict.txt")
    output_list=[]
    
    #jieba.load_userdict(".\\dict_for_jieba\\dict.txt")
    jieba.initialize()
    sim_sent=HanziConv.toSimplified(work)
    str_load=jieba.lcut(sim_sent) #list
    job_output_str=" ".join(str_load) #string
      
    #trad_sent=HanziConv.toTraditional(str_load)
    output_list.append(job_output_str)
    #print(output_list)
    return job_output_str,str_load

def readTainInputData():
     
    import csv
    content_x=[]
    f = open('job_class1_5.csv', 'r',encoding="gb18030")
    for row in csv.DictReader(f):
        content_x.append(row['content'])
    f.close()
    return content_x

#預測履歷為哪一職業類別
def predCV_class(cvContent):   
    job_seg, output_list=Jieba_segment(cvContent)  #call jieba segment
    job_str = ''.join(str(e) for e in job_seg)
    
    y_list=[]
    y_list.append(job_str)
      
  
    #data = pd.read_csv('job_class1_5.csv',usecols=['content'],encoding='gb18030')
    #type(data)

    #list to pd.series
    y_series = pd.Series(y_list)
    #print(y_series)
    
    #讀取原始訓練資料集的透定欄位
    content_x=readTainInputData()
    
    
    
    #创建一个向量计数器对象
    #使用向量计数器(字詞計數)对象转换训练集和验证集
    count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}',max_features=5000)
    count_vect.fit(content_x)
    y_count = count_vect.transform(y_series)
    
    
    
    #ngram 级tf-idf
    #tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2,3), max_features=210)
    #tfidf_vect_ngram.fit(y_list)
    #y_tfidf_ngram = tfidf_vect_ngram.transform(job_str.split('\n'))

    
    
    #词语级tf-idf
    tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', max_features=5000)
    tfidf_vect.fit(content_x)
    ytest_tfidf = tfidf_vect.transform(y_series)
    
    
    cv_weight_list=[]
    word=tfidf_vect.get_feature_names()#獲取詞袋模型中的所有詞語
    weight=ytest_tfidf.toarray() #將tf-idf矩陣抽取出來，元素a[i][j]表示j詞在i類文字中的tf-idf權重
    for i in range(len(weight)):#列印每類文字的tf-idf詞語權重，第一個for遍歷所有文字，第二個for便利某一類文字下的詞語權重
        print(u"-------這裡輸出第",i,u"類文字的詞語tf-idf權重------")
        for j in range(len(word)):
            #print(word[j],weight[i][j])
            cv_weight_list.append(weight[i][j])
            
            
    #print("ytest_tfidf.shape==>",ytest_tfidf.shape)
    
   # print(ytest_tfidf)
    modelName="cv_classifier_20190107_100139.pickle"
    mode_path="saveModel/{}".format(modelName)
    
     #開始預測
    predictions=callModel(mode_path,ytest_tfidf)
    
    
    print(predictions)
    #list result to string
    prediction = ''.join(predictions)
    return prediction,output_list,cv_weight_list
    
def callModel(mode_path,feature_vector_valid,is_neural_net=False):
    #读取Model
    with open(mode_path, 'rb') as f:
        clf2 = pickle.load(f)
        #print(type(clf2))
        #测试读取后的Model
        #print(clf2.predict(feature_vector_valid[0:1]))
    #print(feature_vector_valid.shape)
    
    try:
        # predict the labels on validation dataset
        predictions = clf2.predict(feature_vector_valid)
        if is_neural_net:
            predictions = predictions.argmax(axis=-1)
        return predictions
    except:
        msg="Sorry, the content of resume may be not enough. So, we couldn't match your personel resume to recommend!"
        return msg
    
        
    #print(predictions)
    #print(y_test)
    return predictions 
    

#==========DISC============
def countDISC(output_list):

    
    # Send the Text to CKip
    #res = PDP_socket.socket_connect(cvContent)
    
    # Calculate the Score    
    DISCscore = disc.vocabase_score(output_list)
    
    # Output the Result to File
    #作業系統的路徑os.path.abspath(pwd)
    """
    f = open("C:" + "/Output_for_DISC/" + Identify + "_result.txt", "w")
    f.write("%.2f\n" %DISCscore[0])
    f.write("%.2f\n" %DISCscore[1])
    f.write("%.2f\n" %DISCscore[2])
    f.write("%.2f\n" %DISCscore[3])
    """
    print("Score :", DISCscore[0], DISCscore[1], DISCscore[2], DISCscore[3])
    d=DISCscore[0]
    i=DISCscore[1]
    s=DISCscore[2]
    c=DISCscore[3]
    
    sys.stdout.flush()
    
    return d,i,s,c

def filter_for_stopwords(output_list):
        #加载停用词表
    
    #查詢前，必須先獲取游標
    cur =conn.cursor ()
    
    #執行的都是原生SQL語句
    cur.execute ( "SELECT * FROM nlp_simplechinese_stopwords" )
    
    stop_tuple=()
    for  stop  in  cur.fetchall (): 
        stop_tuple=stop_tuple+(stop)
      
    stop_list=list(stop_tuple)
    """"
    stop_words=[]
    list(stop_words)   
    stop_words[1]
    """       
    
    # jieba.load_userdict('userdict.txt')  
    # 创建停用词list  
    
    stopwords = stop_list # 这里加载停用词的路径  
    outstr ="" 
    word_list=[] 
    for word in output_list:  
        if word not in stopwords:  
            if word != '\t' or word != '\n' :  
                outstr += word  
                outstr += " "
                word_list.append(word)
    
    outstr = " ".join(outstr.split()) #將\n \t 去掉 
    
    return word_list
#==========3Powers============    
def count3Powers(prediction,output_list):
    word_list=filter_for_stopwords(output_list) #斷完詞的結果
    power=['skill','experience','trait']
    
    """執行 skill""" 
    skill_score=countPower(power[0],word_list,prediction)
    
    """執行 education"""
    education_score=countPower(power[1],word_list,prediction)
    
    """執行 trait"""
    trait_score=countPower(power[2],word_list,prediction)
    
    return skill_score, education_score, trait_score
    
def countPower(power,word_list,prediction):
    
      
    #查詢前，必須先獲取游標
    cur =conn.cursor ()
    #執行的都是原生SQL語句
    sql="SELECT words,score FROM job_3powers_keywords WHERE positionClass= '{}' AND powerClass= '{}' ".format(prediction,power)
    
    cur.execute(sql)
    #conn.commit()  #執行sql指令
    
    total_score=0.0                                            
    for (words, score) in cur:
        #print("{}, {}".format(Words, Score)) 
        for i in range(0, len(word_list)):
            if word_list[i]== words:
                total_score+=score
                #print("{},{}".format(word_list[i],total_score))
    
    total_score=round(total_score, 3)
    return total_score
       

def recommendJob(prediction,cv_weight_list):
    #從資料庫select出和履歷同類別的職缺
    prediction=4
    cos_len=[]
           
    class_model_name="saveModel/class_{}_vector.pickle".format(prediction)
    # 讀取職缺向量模型
    job_load_df = pd.read_pickle(class_model_name)
    id_list=job_load_df["id"]
    vector_list=job_load_df["vector"].tolist()
    job_len=len(vector_list)
    for index in range(0,job_len):
        job_weight_list=job_load_df["vector"][index]
        job = np.array(job_weight_list)
        cv = np.array(cv_weight_list)
        cos_len.append(distance.cosine(job,cv))
        

    heapq.nsmallest(5, cos_len)
    min_num_index_list = map(cos_len.index, heapq.nsmallest(5, cos_len))
    matrixR = tuple(min_num_index_list)
    
    companyName_list=[]
    positionTitle_list=[]
        
        
    for l in range(0,len(matrixR)):
        n=matrixR[l]
        index=id_list[n]
        #查詢前，必須先獲取游標
        cur =conn.cursor ()
        
        #執行的都是原生SQL語句
        sql="SELECT companyName, positionTitle FROM `yourator_job` WHERE id= {} " .format(index)
        #print(sql)
        cur.execute(sql) 
        myresult = cur.fetchall()
        companyName_list.append(myresult[0][0])
        positionTitle_list.append(myresult[0][1])
        
        
    result_df=pd.DataFrame({
            'company':companyName_list,
            'job':positionTitle_list
            })  
    
    result_df_js=result_df.to_json(orient='records', force_ascii=False)
    
    return result_df_js
            
            
def saveDB(upload_id,file_path,cvContent,prediction,d,i,s,c,skill_score, education_score, trait_score,result_df_js):
    mycursor = conn.cursor()
 
    sql = "INSERT INTO job_cv (upload_id, cvDocument, cvContent, positionClass,recommend,Dscore,Iscore,Sscore,Cscore,education, skill, trait) VALUES ('{}','{}','{}','{}','{}',{},{},{},{},{},{},{})"\
    .format(upload_id,file_path,cvContent,prediction,result_df_js,d,i,s,c, education_score, skill_score, trait_score)
    #print(sql)
    mycursor.execute(sql)

    conn.commit()
    
    conn.close()
    

if __name__=='__main__':
    #判斷是否有接到外部參數的user_id的值
    try:
        #print(sys.argv[1])
        upload_id=sys.argv[1]
        file_path=sys.argv[2]
    
        cvContent=readCVContent(file_path)
        
        prediction,output_list,cv_weight_list=predCV_class(cvContent)    
        
        d,i,s,c=countDISC(output_list)
        
        skill_score, education_score, trait_score=count3Powers(prediction,output_list)
        
        result_df_js=recommendJob(prediction,cv_weight_list)
        saveDB(upload_id,file_path,cvContent,prediction,d,i,s,c,skill_score, education_score, trait_score,result_df_js)
       
    except IndexError as e:
        # do stuff... optionally displaying the error (e)
        print("123")
    
