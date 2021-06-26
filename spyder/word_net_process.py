import sqlite3
import pandas as pd
from nltk.corpus import wordnet

conn = sqlite3.connect('modwiggler_data.db')
cursor = conn.cursor()

def isin(x1,x2,dic):
    if x2 in dic[x1]:
        return 1
    else:
        return 0
def relationship(x):
    if x == 0:
        return 'synonyms'
    else:
        return 'antonyms'


df = pd.read_sql_query("select distinct keyword,adjective,row_number() over(partition by keyword) as cnt from word_frequency",conn)
df['value'] = 1
tmp1 = df.merge(df,on=['keyword','value'],how='inner')##笛卡尔积合并，每两个单词为一组
tmp2 = tmp1[tmp1['cnt_x']<tmp1['cnt_y']]####避免出现a-b,b-a两种词对同时出现
tmp3 = tmp2[['keyword','adjective_x','adjective_y']]
dic_syn = {}#获取同义词词表
dic_ant = {}#获取反义词词表
for item in df.adjective.values:
    synonyms = []
    antonyms = []
    for syn in wordnet.synsets(item):##获取所有形容词的同义词、反义词表
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                for ant in l.antonyms():
                    antonyms.append(ant.name())
    dic_syn[item] = set(synonyms)
    dic_ant[item] = set(antonyms)

tmp3['is_ant']=tmp3.apply(lambda x: isin(x[1],x[2],dic_ant),axis=1)##匹配同义词反义词表
tmp3['is_syn']=tmp3.apply(lambda x: isin(x[1],x[2],dic_syn),axis=1)
tmp4 = tmp3[(tmp3['is_ant']==1)|(tmp3['is_syn']==1)]##选取有同义词和反义词关系的词对
tmp4['relationship'] = tmp4['is_ant'].map(lambda x:relationship(x))
tmp4 = tmp4[['keyword','adjective_x','adjective_y','relationship']]

cursor.execute("create table relationship (keyword varchar(100),adjective_x varchar(100),adjective_y varchar(100),relationship varchar(100))")
conn.commit()

for item in tmp4.values:
    cursor.execute("insert into relationship values('%s','%s','%s','%s')"%(item[0],item[1],item[2],item[3]))
conn.commit()
conn.close()