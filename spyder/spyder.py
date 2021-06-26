import requests
import re
from bs4 import BeautifulSoup
import sqlite3
from nltk.tag import pos_tag
from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm
from Config import Config

config = Config()
url = config.url
conn = sqlite3.connect(config.database)
cursor = conn.cursor()
##Create a table to store data
sql = "create table if not exists spyder_data (nid int,url vachar(200), title varchar(2000),keyword varchar(20),adjective varchar(100),content text)"
cursor.execute(sql)

#url selector
selector1 = '#page-body > div > div > ul.topiclist.forums > li > dl > dt > div > a.forumtitle'#https://modwiggler.com/forum/
selector2 = '#page-body > div.forumbg > div > ul.topiclist.topics > li > dl > dt > div > a'#https://modwiggler.com/forum/viewforum.php?f=16
selector3 = '#page-body > div.action-bar.bar-top > div.pagination > ul > li > a'#https://modwiggler.com/forum/viewforum.php?f=16 Page turn button
selector4 = '#page-body > div.forumbg > div > ul.topiclist.topics > li > dl > dt > div > a'#https://modwiggler.com/forum/viewtopic.php?f=16&t=180766
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

def get_root(url, selector, pat):##get url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}
    forum_list = []
    try:
        strhtml = requests.get(url, headers=headers)
        soup = BeautifulSoup(strhtml.text, 'lxml')
        data = soup.select(selector)
        pattern = re.compile(pat)
        max_page_num = [100]##set a base page number to contral turn page button number
        if 'start=' in pat:
            try:
                for item in data:
                    res = pattern.findall(item.get('href'))
                    try:
                        max_page_num.append(int(res[0]))
                    except:
                        pass
                max_page_num = max(max_page_num)
            except:
                pass
            forum_list.extend([url + '&start=' + str(_) for _ in range(0, int(max_page_num + 1), 100) if _ != 0])
        else:
            for item in data:
                res = pattern.findall(item.get('href'))
                forum_list.append((url + res[0]))
    except:
        pass
    return forum_list#return url list under input url



###word tokenizer and tagging
###输入帖子下面的对话内容，返回目标词和目标词前面的形容词以及对话
tokenizer = RegexpTokenizer(r'\w+')##切分标点符号
word_list = ['sound', 'sounding', 'tone', 'timbre', 'texture', 'note', 'effect', 'Quality', 'quality']
def find_adj(tmp):
    tmp1 = tmp.replace('\n','')
    tmp1 = tmp1.replace("'",'”')
    text=tokenizer.tokenize(tmp1)
    text = pos_tag(text)##tagging
    for idx in range(len(text)):
        for word in word_list:
            if text[idx][0] == word and text[idx-1][1] in ('JJ','JJR','JJS'):###get adj
                yield text[idx][0],text[idx-1][0],tmp1

def process(k, failed_url):###这里k是获取到的每个帖子的url，这部分的功能是翻页获取每个帖子的内容
    conn = sqlite3.connect("modwiggler_data.db")
    cursor = conn.cursor()
    f1 = open(failed_url, 'a+', encoding='utf8')#Save if the url error

    for leaf_url in tqdm(k):
        leaf_url_list3 = []
        try:
            strhtml = requests.get(leaf_url, headers=headers)
            soup = BeautifulSoup(strhtml.text, 'lxml')
            data = soup.select('#page-body > div.action-bar.bar-top > div.pagination > ul > li > a')
            pattern = re.compile(r'&start=(.*)')
            if data == []:
                leaf_url_list3.append(leaf_url)
            else:
                max_num = 0
                for item in data:
                    try:
                        res = pattern.findall(item.get('href'))
                        if int(res[0]) > max_num:
                            max_num = int(res[0])
                    except:
                        leaf_url_list3.append(leaf_url)
                ##拼接当前url获取翻页的url
                leaf_url_list3.extend([leaf_url + '&start=' + str(_) for _ in range(0, max_num + 1, 25) if _ != 0])###每个帖子的翻页按钮url
                leaf_url_list3.append(leaf_url)
            leaf_url_list3 = set(leaf_url_list3)
            ##get nid and title
            nid = re.findall(r'&t=(.*)', leaf_url)[0]
            leaf_url_name = soup.title.string#title

            for url_leaf in leaf_url_list3:##对于每个帖子的翻页url，获取当前页下的keyword,adj和对话
                strhtml = requests.get(url_leaf, headers=headers)
                soup = BeautifulSoup(strhtml.text, 'lxml')
                data = soup.select('div.content')
                for item in data:
                    text = item.text.replace('\n', '')
                    text = text.replace("'", '"')
                    for item in find_adj(text):
                        if item:
                            sql = "insert into spyder_data (nid,url,title,keyword,adjective,content) values ('%d','%s','%s','%s','%s','%s')" % (
                            int(nid), leaf_url, leaf_url_name, item[0], item[1].lower(), item[2])
                            cursor.execute(sql)
                            conn.commit()
        except Exception as e:
            f1.write(leaf_url + '\n')#Save if the url error
            f1.flush()
            print('wrong', leaf_url, e)
    f1.close()
    cursor.close()
    conn.commit()
    conn.close()

def get_data():
    root_list = get_root(url, selector1, './(.*)&sid')##get url under https://modwiggler.com/forum/先获取根url下的url
    leaf_url_list = []
    ###https://modwiggler.com/forum/viewforum.php?f=16 get url turn page button获取每个模块翻页的url
    for root_url in tqdm(root_list):
        leaf_url_list.append(root_url)
        leaf_url_list.extend(get_root(root_url,selector3,r'start=(.*)'))
    leaf_url_list2 = []
    filad_list = []
    for leaf_url in tqdm(leaf_url_list):##在每个模块的url下获取帖子的url
        forum_list = []
        try:
            strhtml = requests.get(leaf_url, headers=headers)
            soup = BeautifulSoup(strhtml.text, 'lxml')
            data = soup.select(selector4)
            pattern = re.compile(r'./(.*)&sid=')
            for item in data:
                res = pattern.findall(item.get('href'))
                forum_list.append(url + res[0])
            leaf_url_list2.extend(forum_list)
        except:
            filad_list.append(leaf_url)
            print('wrong', leaf_url)
    k = leaf_url_list2[0:1000]  ###chose first 1000 url to catch content
    process(k, config.file_name)

if __name__ == '__main__':
    get_data()

