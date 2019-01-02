# -*- coding: utf-8 -*-
"""
Created on Mon Dec 24 18:14:19 2018

@author: Administrator
"""

#訓練module

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



def readJobContent():
    #查詢前，必須先獲取游標
    cur =conn.cursor()
    sql="SELECT jobContent, jobCondition, positionClass FROM job_content Order by id DESC"
    #執行的都是原生SQL語句
    cur.execute(sql)
    job_file=cur.fetchall()
    job_row=len(job_file)
    type(job_row)
    jobs=[]
    types=[]
    job_dict={}
    job_df=pd.DataFrame()
    for i in range(0,job_row):
        print(i)
        job_word=job_file[i][0]+job_file[i][1]
        job_seg=Jieba_segment(job_word)
        job_str = ''.join(str(e) for e in job_seg)
        jobs.append(job_str)
        types.append(job_file[i][2])
        
    job_dict = {
                "content": jobs,
                "class": types
                }
    job_df = pd.DataFrame(job_dict)

    job_df.to_csv("job_class1_5.csv",  encoding='gb18030')
    return job_df
    
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

#=================================================================================#
def pred_model(classifier, feature_vector_train, label, feature_vector_valid, is_neural_net=False):
    # fit the training dataset on the classifier
    classifier.fit(feature_vector_train, label)

    #儲存訓練好的model
    modelName="cv_classifier_{}.pickle".format( time.strftime("%Y%m%d_%H%M%S", time.localtime()))
    mode_path=saveModel(classifier,modelName)
    
    predictions=callModel(mode_path,feature_vector_valid,is_neural_net=False)
    
    """
    # predict the labels on validation dataset
    predictions = classifier.predict(feature_vector_valid)

    if is_neural_net:
        predictions = predictions.argmax(axis=-1)
        
    print(predictions)
    print(y_test)
    """
    return metrics.accuracy_score(predictions,y_test),predictions

def saveModel(classifier,modelName):
    

    #保存Model(注:save文件夹要预先建立，否则会报错)
    mode_path="saveModel/{}".format(modelName)
    with open(mode_path, 'wb') as f:
        pickle.dump(classifier, f)
    return mode_path
    

def trainModel(job_df):

    x=job_df["content"]
    y=job_df["class"]
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x,y,
                                                    test_size = 0.2,
                                                    random_state=87
                                                   )
    
    # label编码为目标变量，主要為不是數值類別的值
    """
    encoder = preprocessing.LabelEncoder()
    y_train = encoder.fit_transform(y_train)
    y_test = encoder.fit_transform(y_test)
    """
    
    #创建一个向量计数器对象#使用向量计数器对象转换训练集和验证集
    count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}', max_features=210)
    count_vect.fit(x)
    xtrain_count = count_vect.transform(x_train)
    xtest_count = count_vect.transform(x_test)
    
    # ngram 级tf-idf
    tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2,3), max_features=210)
    tfidf_vect_ngram.fit(x)
    xtrain_tfidf_ngram = tfidf_vect_ngram.transform(x_train)
    xtest_tfidf_ngram = tfidf_vect_ngram.transform(x_test)

    #词语级tf-idf
    tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', max_features=210)
    tfidf_vect.fit(x)
    xtrain_tfidf = tfidf_vect.transform(x_train)
    xtest_tfidf = tfidf_vect.transform(x_test)


    from sklearn.svm import SVC
    """
    accuracy_SVC,predictions = pred_model(SVC(), xtrain_tfidf_ngram, y_train, xtest_tfidf_ngram)
    print("SVM, N-Gram Vectors: ", accuracy_SVC,predictions)
    """
    #特征为计数向量的朴素贝叶斯
    accuracy_NB1 ,predictions = pred_model(naive_bayes.MultinomialNB(), xtrain_count, y_train, xtest_count)
    print("NB, Count Vectors: ", accuracy_NB1,predictions)

    #特征为词语级别TF-IDF向量的朴素贝叶斯
    accuracy_NB2, predictions = pred_model(naive_bayes.MultinomialNB(), xtrain_tfidf, y_train, xtest_tfidf)
    print("NB, WordLevel TF-IDF: ", accuracy_NB2, predictions)
    
    
    #特征为多个词语级别TF-IDF向量的朴素贝叶斯
    accuracy_NB3, predictions = pred_model(naive_bayes.MultinomialNB(), xtrain_tfidf_ngram, y_train, xtest_tfidf_ngram)
    print ("NB, CharLevel Vectors: ", accuracy_NB3, predictions)


    #將預測結果與實際結果儲存
    saveResult(x_test,y_test,predictions)
        

def callModel(mode_path,feature_vector_valid,is_neural_net=False):
    #读取Model
    with open(mode_path, 'rb') as f:
        clf2 = pickle.load(f)
        #测试读取后的Model
        #print(clf2.predict(x[0:1]))
        
        
     # predict the labels on validation dataset
    predictions = clf2.predict(feature_vector_valid)

    if is_neural_net:
        predictions = predictions.argmax(axis=-1)
        
    #print(predictions)
    #print(y_test)
    return predictions 

"""
    svm =SVC(kernel='rbf', probability=True)
    svm.fit(x_train,y_train)
    svm.predict(x_test)
"""

def saveResult(x_test,y_test,predictions):
    #將預測結果與實際結果儲存
    output_data={}
    output_data=pd.DataFrame({'index':x_test.index, 'content':x_test.values,
                              'origin_class':y_test.values,'pred_class':predictions})
    output_data.to_csv("job_class1_5_predResult.csv",  encoding='gb18030')
    


if __name__=='__main__':
    job_df=readJobContent()
    trainModel(job_df)
