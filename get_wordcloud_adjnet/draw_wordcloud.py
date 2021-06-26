from wordcloud import WordCloud
import sqlite3
from matplotlib import pyplot as plt
import pandas as pd
import time

####输入keyword列表，返回词云图片存储路径
def draw(json_obj):
    conn = sqlite3.connect('modwiggler_data.db')
    keyword = json_obj.get('keyword')
    query_text = "('"+"','".join([x for x in keyword])+"')"
    frequency = pd.read_sql_query(
        "select adjective,frequency from word_frequency where keyword in {}".format(query_text), conn)
    conn.close()
    if frequency.shape[0] != 0:
        frequency = frequency.groupby('adjective').sum().reset_index()
        dic = {}
        for item in frequency.values:
            dic[item[0]] = item[1]
        wc = WordCloud(background_color='white', width=800, height=400).generate_from_frequencies(dic)
        path = './static/images/wordcloud_{}.jpg'.format(time.time())

        plt.imshow(wc)
        plt.savefig(path, dpi=500)
        return {'code':1,'state':'sucess','data':path}#返回图片存储路径{ '../static/images/wordcloud_1622868546.9150689.jpg'}
    else:
        return {'code':0,'state':'failed','data':'word not found'}

if __name__ == '__main__':
    input_json = {'keyword':['effect']}#example
    data = draw(input_json)
    print(data)