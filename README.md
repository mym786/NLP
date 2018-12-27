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


## 二、職缺推薦

先利用爬蟲的方式，蒐集104職缺類別的五類 (儲存 job_content.csv中)並匯入至MySQL資料庫--job_content.sql；在104人才資料庫中，蒐集職業五類的履歷。將五類職缺的內容及求職者的履歷利用文本分類演算法，進行訓練MODEL，之後可用來歸類為哪一類職缺類別。

之後求職者再投遞履歷的時候，即可自動產生一份個人報表及職缺推薦(TOP5)。

+ 個人報表：利用五類職缺的字詞分成三類 (學經歷、技能、人格特質) 的詞頻，分別基於詞頻來套用正規化公式，讓分數基於1-10之間，三類總分數累計加總。
+ 職缺推薦：依據求職者履歷歸類為哪一類職缺類別後，可用兩種方式找到兩兩文本的相似程度
  + (1)針對文本中的字詞求得詞向量(可用fasttext, word2vec, word=bedding...)後，然後作均值(所有詞向量加總後除以所有字詞數)的處理，即可得到"文本的向量"，再用文本的向量利用"餘弦相似度"來和其他文本向量來求相似度。


### 104_crawlerBasedPosition.py
1.104求才網站爬蟲，針對職缺五類(1.	管理/行政/財經/法務。2.	行銷/業務/服務。3.	教育/媒體/傳播。4.	軟硬體研發/製造/工程。5.	其他專業 (農林漁牧/餐飲/醫學/軍警/物流/採購)。)將**公司名稱、職缺名稱、工作內容和工作條件** 作為欄位的存取，並依序存入csv檔(依序為 class1_content_output.csv、class2_content_output.csv、class3_content_output.csv、class4_content_output.csv和class5_content_output.csv

### modelForRecommend.py 
1. 讀取資料集：

先讀取job_content.sql中的jobContent, jobCondition, positionClass欄位，將每一筆的jobContent, jobCondition合併後進行jieba斷詞，最後斷詞結果和positionClass欄位的值一起存入csv檔 (job_class1_5.csv)
 
2.訓練資料集： (參考: https://zhuanlan.zhihu.com/p/37157010)

+ 將上一步完成斷詞的資料集分成80%的訓練資料 和 20%的測試資料
+ 訓練三種不同的預測模型：
  + 向量计数器的貝氏(bayes)模型： 先建立一個向量计数(**字詞計數**)器的模型，再利用此模型轉換為訓練集和測試集。
  + 字詞tfidf的貝氏(bayes)模型：先建立一個词语级tf-idf的模型，再利用此模型轉換為訓練集和測試集。
  + ngram 级tf-idf的貝氏(bayes)模型：先建立一個ngram级tf-idf的模型，再利用此模型轉換為訓練集和測試集。

3.預測資料集：

+ 將訓練好的模組後，並將此model用pickle檔儲存(cv_classifier_{時間}.pickle)，並呼叫此模組將**測試**資料集放入
+ 最後將預測結果與測試資料一起儲存csv檔(job_class1_5_predResult.csv)，以做為比較用途。
