"""
coinmarketcap.com web scraper
Created on June 6 2021
@author: Jack.M.Liu
"""

import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
from ckiptagger import WS

def create_dicts():
    pos_list=[]
    neg_list=[]
    pos_table = pd.read_csv('dict/pos_words_Chinese.csv',encoding='utf_8_sig')
    neg_table = pd.read_csv('dict/neg_words_Chinese.csv',encoding='utf_8_sig')
    temp_pos_list = pos_table["pos_chi"].tolist()
    temp_neg_list = neg_table["neg_chi"].tolist()

    for w in temp_pos_list:
        if "＃" in str(w):
            pos_list.append(str(w).split("＃")[0])
        else:
            pos_list.append(str(w))

    for w in temp_neg_list:
        if "＃" in str(w):
            neg_list.append(str(w).split("＃")[0])
        else:
            neg_list.append(str(w))
    
    return pos_list, neg_list
    

    #pos_dict = dict(zip(list(pos_table.posword),list(pos_table.score)))
    #neg_dict = dict(zip(list(neg_table.negword),map(lambda a:a*(0-1),list(neg_table.score)) ))
    #global sentiment_dict    
    #sentiment_dict={**pos_dict,**neg_dict}

def get_sentiment(tokens):
    pos_count=0
    neg_count=0
    total_count=0
    for w in tokens:
        if w in pos_list:
            pos_count += 1
            total_count += 1
        elif w in neg_list:
            neg_count += 1
            total_count += 1
        else:
            total_count +=0
    score=pos_count-neg_count
    return score

def get_digi_page():
    url = 'https://www.ptt.cc/bbs/DigiCurrency/index.html'
    response = rq.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    linktext=soup.find_all("a",class_="btn wide") #找上一頁的連結
    linkhref=linktext[1].get('href') 
    page=int(linkhref[23:26]) #擷取數字部分，轉成數字型態
    page+=1 #加一才是最新的那頁
    return page


def search(p): #要爬p頁
    count=1
    page=get_digi_page()
    titles=[]
    emotions=[]
    scores=[]
    years=[]
    dates=[]
    while count < p+1: 
        url='https://www.ptt.cc/bbs/DigiCurrency/index'+str(page)+'.html'
        response = rq.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        posts = soup.find_all("div", class_ = "title")
        for post in posts:
            try:
                inpost=post.find('a')
                inurl='https://www.ptt.cc'+inpost.get('href')
                #print(inurl) 檢查點
                inresponse = rq.get(inurl)
                insoup = BeautifulSoup(inresponse.text, "lxml")
                header = insoup.find_all('span','article-meta-value')
                title = header[2].text # 標題
                timestamp = header[3].text #發文時間
                year=timestamp[-4:]
                date=timestamp[4:10]
                main_container = insoup.find(id='main-container')
                all_text = main_container.text #把標籤內所有文字都抓出來
                pre_text = all_text.split('--')[0] # 把內文跟留言切開
                texts = pre_text.split('\n') # 把每段文字 根據 '\n' 切開 
                contents = texts[2:]  
                content = ''.join(contents) # 內容
                ws_results = ws([content])  #分詞
                words = ws_results[0]
                words = [w for w in words if w not in stopwords] 
                score = get_sentiment(words)
                if score >= 20:
                    emotion = "very positive"
                elif score > 3:
                    emotion = "positive"
                elif score >= -1:
                    emotion = "neutral"
                else:
                    emotion = "negative"
                titles.append(title)
                emotions.append(emotion)
                scores.append(score)
                years.append(year)
                dates.append(date)
            except:
                print('',end='')

        print('\r'+"虛擬貨幣板已完成" +str(count)+"/"+str(p)+"頁..." ,end='')
        page-=1 
        count+=1

    temp_df = pd.DataFrame()
    temp_df["title"]=titles
    temp_df["year"]=years
    temp_df["date"]=dates
    temp_df["score"]=scores
    temp_df["emotion"]=emotions
    return temp_df


if __name__ == "__main__":
    ws = WS("./data")
    stopwords=open('stopwords_cn.txt',encoding='utf8').read()
    pos_list,neg_list = create_dicts()
    df=search(20)
    df.to_csv('only虛擬貨幣板.csv',encoding='utf_8_sig')
