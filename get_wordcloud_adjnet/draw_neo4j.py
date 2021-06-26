import pandas as pd
import sqlite3
from flask import jsonify

def buildnodes(nodelist):  # 构建web显示节点
    nodes = []
    for item in enumerate(nodelist):
        dic = {'data':{'id':item[0],'label':'adj_net','name':item[1]}}
        nodes.append(dic)
    return nodes

def buildedges(edgelist,nodelist):  # 构建web显示节点
    edges = []
    for item in edgelist.values:
        dic = {'data':{'soure':nodelist.index(item[0]),'target':nodelist.index(item[1]),'relationship':item[2]}}
        edges.append(dic)
    return edges

def get_relationship(json_obj):
    keyword = json_obj.get('keyword')
    query_text = "('" + "','".join([x for x in keyword]) + "')"
    conn = sqlite3.connect('modwiggler_data.db')
    relationship = pd.read_sql_query(
        "select distinct adjective_x,adjective_y,relationship from relationship where keyword in {}".format(
            query_text), conn)
    if relationship.shape[0] == 0:
        print('word not found')
    node = relationship.adjective_x.unique().tolist()
    node.extend(relationship.adjective_y.unique().tolist())
    node = list(set(node))
    nodes = buildnodes(node)
    edges = buildedges(relationship, node)
    conn.close()
    return jsonify(elements={"nodes": nodes, "edges": edges})

