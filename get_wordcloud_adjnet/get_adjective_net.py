import sqlite3
import pandas as pd

###输入keyword的json列表，返回关系列表
def get_relationship(json_obj):
    keyword = json_obj.get('keyword')
    conn = sqlite3.connect('modwiggler_data.db')
    query_text = "('" + "','".join([x for x in keyword]) + "')"
    relationship = pd.read_sql_query(
        "select distinct adjective_x,adjective_y,relationship from relationship where keyword in {}".format(query_text), conn)
    conn.close()
    if relationship.shape[0] != 0:
        return {'code':1,'state':'sucess','data':relationship.values.tolist()}##返回节点关系列表
    else:
        return {'code':0,'state':'failed','data':'word not found'}


if __name__ == '__main__':
    input_json = {'keyword':['sound','effect']}
    data = get_relationship(input_json)
    print(data)