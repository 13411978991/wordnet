from flask import Blueprint,Response,request
import json
from get_wordcloud_adjnet.draw_wordcloud import draw
from get_wordcloud_adjnet.get_adjective_net import get_relationship
from get_wordcloud_adjnet.draw_neo4j import  get_relationship as get_relationship_v2

blueprint = Blueprint('index',__name__,url_prefix='/index',template_folder='template',static_folder='static')

@blueprint.route('/wordcloud',methods=['GET'])
def show_wordcloud():
    req_json = request.get_json()
    folder = draw(req_json)
    return Response(json.dumps(folder))

@blueprint.route('/adj_net',methods=['GET'])
def get_adj_net():
    req_json = request.get_json()
    relationship = get_relationship(req_json)
    return Response(json.dumps((relationship)))

@blueprint.route('/adj_net_v2',methods=['GET'])
def get_adj_net_v2():
    req_json = request.get_json()
    relationship = get_relationship_v2(req_json)
    return relationship