# 【簡介】
+ 根據指定的關鍵字，於 104 人力銀行爬取相關職缺資訊，包含職缺名稱、公司名稱、工作內容、所需技能、薪資等等，並將所有結果輸出一個 Excel 檔
+ 透過 Jieba 工具，針對工作內容進行斷詞分析，並統計出熱門詞彙及其數量，並將結果輸出一個文字檔
+ 統計所需技能的數量，並將結果輸出一個文字檔，以利了解相關職缺較需具備哪些技能

# 【主要使用工具及套件】
+ Python
+ BeautifulSoup
+ Jieba

# 【使用說明】
1. 於 my_dict.txt 字典中新增關鍵字相關詞彙，後續 Jieba 將會讀取此字典進行斷詞
2. 於 conf.txt 第一行設定欲查詢的關鍵字
3. 將欲統計的技能名稱修改於 column.txt 中，一行代表一項技能
4. 於 synonym.txt 新增或修改同義詞辭典內容，將依據此字典的內容，統計詞彙出現的次數
