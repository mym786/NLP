# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 17:58:49 2018

@author: Administrator
"""

import sys

from hanziconv import HanziConv
import pandas as pd
import mysql.connector, jieba, time, pickle #pickle模块


from sklearn import model_selection, preprocessing, linear_model, naive_bayes, metrics, svm
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn import decomposition, ensemble


from keras.preprocessing import text, sequence
from keras import layers, models, optimizers 


    

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
    work_list=[]
    
    
    #jieba.load_userdict(".\\dict_for_jieba\\dict.txt")
    jieba.initialize()
    sim_sent=HanziConv.toSimplified(work)
    str_load=jieba.lcut(sim_sent)
    job_output_str=" ".join(str_load) #string
      
        #trad_sent=HanziConv.toTraditional(str_load)
    work_list.append(job_output_str)
    #print(len(cont_seg_list))
    return job_output_str


#預測履歷為哪一職業類別
def predCV_class(cvContent):   
    job_seg=Jieba_segment(cvContent)  #call jieba segment
    job_str = ''.join(str(e) for e in job_seg)
    print(job_str)
    y_list=[]
    y_list.append(job_str)
    
    
    #讀取原始訓練資料集的透定欄位
  
    data = pd.read_csv('job_class1_5.csv',usecols=['content'],encoding='gb18030')
    type(data)



    #list to pd.series
    y_series = pd.Series(y_list)
    print(y_series)
    
    
    
    import csv
    content_x=[]
    f = open('job_class1_5.csv', 'r',encoding="gb18030")
    for row in csv.DictReader(f):
        content_x.append(row['content'])
    f.close()
    
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

    
    print("ytest_tfidf.shape==>",ytest_tfidf.shape)
    
   # print(ytest_tfidf)
    modelName="cv_classifier_20190102_171610.pickle"
    mode_path="saveModel/{}".format(modelName)
    
     #開始預測
    predictions=callModel(mode_path,ytest_tfidf)
    
    
    print(predictions)
    return predictions
    
def callModel(mode_path,feature_vector_valid,is_neural_net=False):
    #读取Model
    with open(mode_path, 'rb') as f:
        clf2 = pickle.load(f)
        print(type(clf2))
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
    


if __name__=='__main__':
    #判斷是否有接到外部參數的user_id的值
    try:
        #print(sys.argv[1])
        user_id=sys.argv[1]
        file_path=sys.argv[2]
    
        cvContent=readCVContent(file_path)
        
        predictions=predCV_class(cvContent)
        
        
        
        
        
       
    except IndexError as e:
        # do stuff... optionally displaying the error (e)
        print("123")
    
