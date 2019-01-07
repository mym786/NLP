# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 11:48:17 2019

@author: Administrator
"""

from hanziconv import HanziConv
import pandas as pd
import mysql.connector, jieba, pickle #pickle模块
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

conn = mysql.connector.connect(user='jobRecommend', password='xOsIhwgaFIfm8nqf',
                              host='35.160.71.183',
                              database='job_recommendation')

#讀入資料庫中的id和職缺內容
def readPositionContent():
    # 使用cursor()方法获取操作游标 
    cursor = conn.cursor()

    # 使用execute方法执行SQL语句
    cursor.execute(" SELECT id, positionContent FROM yourator_job ")
    myresult = cursor.fetchall()
    
    position_list=[]
    for row in myresult :
        print(row)
        position_list.append(row)
    
    
    return position_list
    
    
def Jieba_segment(position_list):
    #为主词典即优先考虑的词典,原词典此时变为非主词典
    jieba.load_userdict(".\\dict_for_jieba\\dict.txt")
    output_list=[] 
    
    
    #jieba.load_userdict(".\\dict_for_jieba\\dict.txt")
    jieba.initialize()
    n=len(position_list)
    for n in range(0,n):
        
        sim_sent=HanziConv.toSimplified(position_list[n][1]).lower()
        str_load=jieba.lcut(sim_sent) #list
        job_output_str=" ".join(str_load) #string
      
        #trad_sent=HanziConv.toTraditional(str_load)
        output_list.append(job_output_str)
    #print(output_list)
    return output_list


#預測工作內容為哪一職業類別
def predJob_class(position_list):     
    output_list=Jieba_segment(position_list)  #call jieba segment
    """
    job_str = ''.join(str(e) for e in job_seg)
    print(job_str)
    y_list=[]
    y_list.append(job_str)
    print(y_list)
    """
    
    #讀取原始訓練資料集的透定欄位
    #data = pd.read_csv('job_class1_5.csv',usecols=['content'],encoding='gb18030')
    #type(data)



    #list to pd.series
    y_series = pd.Series(output_list)
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

    
    
    
   # print(ytest_tfidf)
    modelName="cv_classifier_20190107_100139.pickle"
    mode_path="saveModel/{}".format(modelName)
    
     #開始預測
    predictions=callModel(mode_path,ytest_tfidf)
    
    
    print(predictions)
    #array result to list
    prediction = predictions.tolist()
    return prediction,output_list
    
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


#結果更新至資料庫
def saveDB(position_list,prediction):
    mycursor = conn.cursor()
    
    row = len (position_list)
    for i in range(0,row):
        
        sql = "UPDATE yourator_job SET positionClass = '{}' WHERE id = {}".format(prediction[i],i+1)

        mycursor.execute(sql)

        conn.commit()

    conn.close()

if __name__=='__main__':
    #判斷是否有接到外部參數的user_id的值
    try:
        position_list=readPositionContent()
        prediction,output_list=predJob_class(position_list)    
        
        saveDB(position_list,prediction)
       
    except IndexError as e:
        # do stuff... optionally displaying the error (e)
        print("123")
    
