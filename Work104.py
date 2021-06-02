""" 
# Step 1.0 import packages    --> urllib, requests , BeautifulSoup
# Step 2.0 Data               --> url, headers, formdata, cookies
# Step 3.1 get request object --> urllib.request.Request(Data)
#      3.2 get response       --> urllib.request.urlopen(req).read()
#                             --> HTML string
#                                         ↓
# Step 4.0 using module --> BeautifulSoup( ) = soup
#                  soup --> find( )     
#                       --> select( )     ==> List[Tag.object, Tag.object]
#                                         ==> Tag.object --> can use「find」「select」 
#------------------------------------------------------------------------------------
# 爬 104人力銀行
# --> 使用 關鍵字 
# --> 其搜索結果 (公司資訊、職缺名稱、聯絡資訊、所需技能等結果) 
# --> Excel or csv 逐筆呈現
# --> 將技能數量以 txt 做個別小計
# --> 輸入 關鍵字及其同義詞字典 並計算談及相關的數量
# """

import requests
import os
import random
from bs4 import BeautifulSoup
import pandas as pd
import jieba
import json
import time
import random
import datetime as dt

# load config txt (keyword, page) as Query_String_Para
with open('./config/conf.txt','r',encoding='utf-8') as f:
    kw = requests.utils.quote(f.readline().split('=')[1].split('\n')[0])
    dictFile = f.readline().split('=')[1].split('\n')[0]
page = 1

resultFolder = requests.utils.unquote(kw) + '_' + dt.datetime.now().strftime('%Y_%m_%d')

if not os.path.exists('./'+ resultFolder):
    os.mkdir(resultFolder)

urlSearch = 'https://www.104.com.tw/jobs/search/list?ro=0&kwop=7&keyword={}&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=14&asc=0&page={}&mode=s'.format(kw,page)

userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
headers = {
    'User-Agent':userAgent,
    'Referer': 'https://www.104.com.tw/jobs/search/?ro=0&keyword={}&expansionType=area,spec,com,job,wf,wktm'.format(kw)
    }

# def savefile(resultFolder,company,jobName,address,salary,tools,jobContent,others,welfare):
#     with open('./' + resultFolder + '/' + company + '_' + jobName + '.txt','w+',encoding='utf-8') as f:
#         f.write('公司 : ' + company+'\n')
#         f.write('工作名稱 : ' + jobName+'\n')
#         f.write('地址 : ' + address+'\n')
#         f.write('薪資 : ' + salary+'\n')
#         f.write('擅長工具 : ' + (' ').join(tools)+'\n\n')
#         f.write('工作內容 : \n' + jobContent+'\n\n')
#         f.write('其他條件 : \n' + others+'\n\n')
#         f.write('公司福利 : \n' + welfare+'\n\n================================\n\n')

# for pandas
title = ['Company','Job_Openings','Job_Contents','Salaey','Address','Others','Welfare','Url']
with open('./column/column.txt','r',encoding='utf-8') as f:
    skills = [_.split('\n')[0] for _ in f.readlines()]
DF = pd.DataFrame(columns=title + skills)
skillCountDict = {skill:0 for skill in skills}
n = 0

# for jiba
jieba.load_userdict('./dict/' + dictFile)
with open('./synonym/synonym.txt','r',encoding='utf-8') as f:
    synonymList = [_.split('\n')[0] for _ in f.readlines()]

synonymDict = {synonym.split('=')[0]:[word.lower() for word in synonym.split('=')] for synonym in synonymList }
wordCountDict = {word:0 for word in synonymDict.keys()}
wordJobCountDict = wordCountDict.copy()

while True:
    req = requests.get(urlSearch,headers=headers)

    # jsonDataDict_keys(['status', 'action', 'data', 'statusMsg', 'errorMsg'])
    # dataDict_keys(['query', 'filterDesc', 'queryDesc', 'list', 'count', 'pageNo', 'totalPage', 'totalCount'])
    jsonDataDict = json.loads(req.text)['data']
    jsonDataList = jsonDataDict['list']
    totalPage = jsonDataDict['totalPage']

    for jobDict in jsonDataList:
        if jobDict['jobsource'] == 'hotjob_chr':
            continue

        jobUrl = 'https:' + jobDict['link']['job']
        jobID = jobUrl.split('?')[0].split('/')[-1]

        jobajaxUrl = 'https://www.104.com.tw/job/ajax/content/' + jobID
        headers['Referer'] = jobUrl
        reqjob = requests.get(jobajaxUrl,headers=headers)

        jobdataDict = json.loads(reqjob.text)['data']

        jobName = jobdataDict['header']['jobName']
        company = jobdataDict['header']['custName']
        jobContent = jobdataDict['jobDetail']['jobDescription']
        salary = jobdataDict['jobDetail']['salary']
        address = jobdataDict['jobDetail']['addressRegion'] + jobdataDict['jobDetail']['addressDetail']
        tools = [ _['description'] for _ in jobdataDict['condition']['specialty']]
        others = jobdataDict['condition']['other']
        welfare = jobdataDict['welfare']['welfare']

        print(company)
        print(jobName)
        print('============================')

        # save txt test
        # try:
        #    savefile(resultFolder,company,jobName,address,salary,tools,jobContent,others,welfare)
        # except FileNotFoundError as FNF:
        #     sp = ['/', '|', '?', '"', '*', '>', '<', ':']
        #     for s in sp:
        #         jobName = jobName.replace(s,'_')
        #     savefile(resultFolder,company,jobName,address,salary,tools,jobContent,others,welfare)

        # use pandas make dataframe and save as scv
        DF.loc[n] = [company,jobName,jobContent,salary,address,others,welfare,jobUrl] + [0]*skills.__len__()
        for skill in tools:
            if skill in skills:
                DF.loc[n, skill] = 1
                skillCountDict[skill] += 1

        wordCut = jieba.cut(jobContent.lower())
        wordCutList = [w for w in wordCut]

        for word in synonymDict.keys():
            wordexist = 0
            for w in synonymDict[word]:
                wordCountDict[word] += wordCutList.count(w)
                wordexist += wordCutList.count(w)
            if wordexist > 0:
                wordJobCountDict[word] += 1
        n += 1

    if page < totalPage:
        page += 1
        headers['Referer'] = urlSearch
        urlSearch = 'https://www.104.com.tw/jobs/search/list?ro=0&kwop=7&keyword={}&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=14&asc=0&page={}&mode=s'.format(kw,page) 
    else:
        break

    time.sleep(random.randint(1,2))

with open('./' + resultFolder + '/' + resultFolder + 'skillsCount.txt','w',encoding='utf-8') as f:
    f.write('Skills statistic \n')
    for u,v in dict(sorted(skillCountDict.items(), key=lambda item: item[1], reverse=True)).items():
        f.write(u + ':' + str(v) + '\n')
with open('./' + resultFolder + '/' + resultFolder + 'jiebaCount.txt','w',encoding='utf-8') as f:
    f.write('Hot words statistic \n')
    for u,v in dict(sorted(wordCountDict.items(), key=lambda item: item[1], reverse=True)).items():
        f.write(u + ':' + str(v) + '\n')
with open('./' + resultFolder + '/' + resultFolder + 'jiebaCount_once.txt','w',encoding='utf-8') as f:
    f.write('Hot words statistic (how many jobs have that hot word ) \n')
    for u,v in dict(sorted(wordJobCountDict.items(), key=lambda item: item[1], reverse=True)).items():
        f.write(u + ':' + str(v) + '\n')

# DF = DF.sort_values(by=['Company'], ascending=False)
DF.to_csv('./' + resultFolder + '/' + resultFolder + '_results.csv', index = False, encoding='utf-8-sig')
