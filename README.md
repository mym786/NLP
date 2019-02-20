# NLP


## 一、找職缺的主要字詞

### 104_crawler.py 

104求才網站爬蟲，針對工作內容和工作條件進行分類，並個別存取

----------------------------------------------------------------------------

### data_preprocessing.py

針對104網站爬蟲整理好的「工作內容」和「工作條件」分別進行以下步驟來做為資料預處理：

因為簡體的文字相較於繁體中文而言，對於jieba斷詞前者斷詞結果會比較佳

1.斷詞(將**繁體翻譯完簡體**後進行斷詞，使用外部辭典及jieba套件)

2.停止詞過濾(將**簡體字翻譯為繁體**後，從資料庫的停止詞進行過濾)，「工作內容」和「工作條件」過濾完的結果分別存入兩個txt檔({}_cond_after_filter.txt 和{}_cont_after_filter.txt)

使用**停用詞**字詞表，參考網址：
+ 中國大陸簡體中文與英文版：https://github.com/goto456/stopwords
+ 台灣繁體中文版：https://github.com/tomlinNTUB/Machine-Learning/blob/master/data/%E5%81%9C%E7%94%A8%E8%A9%9E-%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87.txt
+ 英文停用詞表：https://blog.csdn.net/shijiebei2009/article/details/39696523

3.找出「工作內容」和「工作條件」中詞頻數量分別前100多的字詞，結果一起存入csv檔({}_TermCount.csv)

4.利用**TFIDF**找出「工作內容」和「工作條件」中每則刊登職缺的主要關鍵字以及其字詞的tfidf的值，tfidf的值也是反映出關鍵詞在文檔中的重要性的權重，結果一起存入csv檔({}_WordVector.csv)

(完)

--------------------------------------------------------------------------------------------------------------------------


## 二、職缺推薦 (偏向基於知識的推薦系統: 不需要用戶"過去"的喜好與回饋)

先利用爬蟲的方式，蒐集104職缺類別的五類 (儲存 job_content.csv中)並匯入至MySQL資料庫--job_content.sql；在104人才資料庫中，蒐集職業五類的履歷。將五類職缺的內容及求職者的履歷利用文本分類演算法，進行訓練MODEL，之後可用來歸類為哪一類職缺類別。

之後求職者再投遞履歷的時候，即可自動產生一份個人報表及職缺推薦(TOP5)。

+ 個人報表：利用五類職缺的字詞分成三類 (學經歷、技能、人格特質) 的詞頻，分別基於詞頻來套用正規化公式，讓分數基於1-10之間，三類總分數累計加總。
+ 職缺推薦：依據求職者履歷歸類為哪一類職缺類別後，可用兩種方式找到兩兩文本的相似程度

  + (1)此實驗是使用了 **tfidf-weighting word vectors**方法，它是指对句子中的所有词向量根据tfidf权重加权求和，是常用的一种计算sentence embedding的方法，在某些问题上表现很好，相比于简单的对所有词向量求平均，考虑到了tfidf权重，因此句子中更重要的词占得比重就更大。但缺点也是没有考虑到单词的顺序
    --------------------- 
    作者：Johnson0722 
    来源：CSDN 
    原文：https://blog.csdn.net/John_xyz/article/details/79208564 


  + (2)目前針對文本中的字詞求得詞向量(可用fasttext, word2vec, word=bedding...)後，然後作均值(所有詞向量加總後除以所有字詞數)的處理，也就是使用了     average word vectors方法，就是简单的对句子中的所有词向量取平均。是一种简单有效的方法，但缺点也是没有考虑到单词的顺序，即可得到"文本的向量"，再用文本的向量利用"餘弦相似度"來和其他文本向量來求相似度。

![image](https://github.com/yichichou/NLP/blob/master/%E8%81%B7%E7%BC%BA%E5%AA%92%E5%90%88%E7%B3%BB%E7%B5%B1%E6%9E%B6%E6%A7%8B%E5%9C%96.png)

### 104_crawlerBasedPosition.py

1.

104求才網站爬蟲，針對職缺五類(1.	管理/行政/財經/法務。2.	行銷/業務/服務。3.	教育/媒體/傳播。4.	軟硬體研發/製造/工程。5.	其他專業 (農林漁牧/餐飲/醫學/軍警/物流/採購)。)將**公司名稱、職缺名稱、工作內容和工作條件** 作為欄位的存取，並依序存入csv檔(依序為 class1_content_output.csv、class2_content_output.csv、class3_content_output.csv、class4_content_output.csv和class5_content_output.csv

2.

**作為訓練modle的資料集** 


### yourator_crawler.py

1.爬取yourator工作職缺(參考： https://www.yourator.co/events/2019YouratorSpringJobFair )，分別為「公司名稱」、「職缺url」、「職缺名稱」、「職缺內容」。存入csv檔和mysql資料庫中。

2.**用來做工作內容分類的目標預測集推薦給user的資料集**


### ClassifyForCV_Job.py 

1.讀取資料集：

先讀取job_content.sql中的jobContent, jobCondition, positionClass欄位，將每一筆的jobContent, jobCondition合併後進行jieba斷詞，最後斷詞結果和positionClass欄位的值一起存入csv檔 (job_class1_5.csv)
 
2.訓練資料集： (參考: https://zhuanlan.zhihu.com/p/37157010)

+ 將上一步完成斷詞的資料集分成80%的訓練資料 和 20%的測試資料
+ 訓練三種不同的預測模型，以下三種方法都設定向量特徵最大值為5000維度：
  + 向量计数器的貝氏(bayes)模型： 先建立一個向量计数(**字詞計數**)器的模型，再利用此模型轉換為訓練集和測試集。
  + 字詞tfidf的貝氏(bayes)模型：先建立一個词语级tf-idf的模型，再利用此模型轉換為訓練集和測試集。
    + tfidf的貝氏(bayes)模型預測結果:
    
  ![image](https://github.com/yichichou/NLP/blob/master/tfidf_nb_pred.PNG)
  + ngram 级tf-idf的貝氏(bayes)模型：先建立一個ngram级tf-idf的模型，再利用此模型轉換為訓練集和測試集。

3.預測資料集：

+ 將訓練好的模組後，並將此model用pickle檔儲存(cv_classifier_{時間}.pickle) ，並呼叫此模組將**測試**資料集放入

預測結果，以字詞tfidf的貝氏(bayes)模型，正確率最高，因此以此作為之後的預測模型 **cv_classifier_20190107_100139.pickle**

+ 最後將預測結果與測試資料一起儲存csv檔(job_class1_5_predResult.csv)，以做為比較用途。



### jobPredClass.py

1. 預測工作職缺的類別，並儲存在資料庫


2.計算每一個職缺類別(class1~class5)的文本的5000維度向量值，即為 **職缺向量模型**，並儲存：

+ 為了讓使用 **推薦模組的餘弦定理計算兩兩文本(履歷和職缺)的字詞向量距離** 比較省時及效率

+ 將已經預測好職缺類別的工作之後，從資料庫找職缺類別1~5的工作找出來，並計算每個類別中所有職缺的tfidf字詞向量，以dataframe的內容格式，以pickle檔儲存 ( class_{職缺類別}_vector.pickle) ，共五個。

+ pickle檔的格式內容，類似於xml的格式可以自定義的二進位的內容

### cvRecommend.py

1.從外部讀取user的 userid和履歷檔案

2.預測履歷的職缺類別
 
+ 呼叫ClassifyForCV_Job.py已經訓練好的model (cv_classifier_20190107_100139.pickle)，利用字詞tfidf的貝氏(bayes)模型,進行預測。

+ 將原本 **訓練** 的data (job_class1_5.csv) 中的input data 進行fit
 
+ 即可得知履歷為職業五類的哪一類

3.計算DISC分數

+ 將用來計算履歷的disc的txt檔內容，翻譯成簡體中文。

+ 從履歷中的字詞進行和文檔做匹配給予分數


4.計算三力的分數

+ 爬取104中職缺五類的工作職缺，進行斷詞及詞頻的計算，進行人工的標註三個類別，為三力 (學經歷、技能、人格特質) 經由詞頻的計算後，利用正歸化的方式使每一類職缺的每一類字詞，介於1~10分之間。

+ 而每個類別都分別再將這些以正規化公式算好的分數，加總起來，作為母體的分數。

+ 之後將履歷的字詞讀取並先**刪除重複出現的字詞**，再利用字詞分數累加的方式，計算完的分數再除以對應類別的總分，即為每份履歷的三力分數。

5.從預測的職業類別中找相似的職缺TOP5

+ 利用**餘弦定理**，來求**履歷的5000個特徵點**和**某類全部職缺的5000個特徵點**的餘弦距離，距離愈短表示兩個文本愈相似，再找出距離最短的前五個，並以josn records的方式儲存至db

6.結果儲存

