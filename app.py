# coding=utf-8
from flask import Flask, jsonify, render_template, request, redirect
from py2neo import Graph, Node, Relationship, NodeMatcher
import os
import re

import jpype

import text_classifier.modelProcess as tm
from text_classifier.modelProcess import Naive_Bayes

app = Flask(__name__)
graph = Graph(
    "http://localhost:7474",
    username="neo4j",
    password="gei509yongde"
)

app.jinja_env.variable_start_string = '{{ '
app.jinja_env.variable_end_string = ' }}'

NodePoint = ""

jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=E:\Software\HanLP\hanlp-1.7.0.jar;E:\Software\HanLP", "-Xms1g",
                 "-Xmx1g")  # 启动JVM，Linux需替换分号;为冒号:

# 初始化model
nb = Naive_Bayes("./data/question/")
# main("./data/question/")


def buildNodes(nodeRecord):
    n = nodeRecord.get(NodePoint)
    a = str(n)
    print(a)
    labels = str(n.labels)

    pattern = re.compile('_\d+')
    iid = str(re.search(pattern, a).group())[1:]

    data = {}

    if labels == ":People":
        data = {"label": labels[1:],
                "id": iid, "name": str(n.get("name"))}
    elif labels == ":Penalty":
        data = {"label": labels[1:],
                "id": iid, "name": str(n.get("name")),
                "sentence_years": str(n.get("sentence_years")),
                "property_penalty_type": str(n.get("property_penalty_type")),
                "property_penalty_amount": str(n.get("property_penalty_amount"))}
    elif labels == ":Drugs":
        data = {"label": labels[1:],
                "id": iid, "name": str(n.get("name")),
                "drug_type_quantity_amount": str(n.get("drug_type_quantity_amount")),
                "drug_unit_price": str(n.get("drug_unit_price"))}
    elif labels == ":Crime":
        data = {"label": labels[1:],
                "id": iid, "name": str(n.get("name"))}
    elif labels == ":Cases":
        data = {"label": labels[1:],
                "id": iid, "name": str(n.get("name")),
                "location": str(n.get("location")),
                "court_name": str(n.get("court_name")),
                "min_birth": str(n.get("min_birth")),
                "min_age": str(n.get("min_age")),
                "people_involved_num": str(n.get("people_involved_num")),
                "year": str(n.get("year"))}

    return {'data': data}


def buildEdges(relationRecord):
    r = relationRecord.get("r")
    a = str(r)
    # print(a)

    pattern = re.compile('\:\w+')
    relationship = str(re.search(pattern, a).group())[1:]

    prerelationship = ['judge', 'contain', 'punish', 'involve']
    aftrelationship = ['judged_by', 'appear', 'punished_by', 'involved_in']

    pattern1 = re.compile(': \d+,')
    pattern2 = re.compile(': \d+}')

    case_id = str(re.search(pattern1, a).group())[2:-1]
    type_id = str(re.search(pattern2, a).group())[2:-1]

    cyto = "MATCH(n:Cases{case_id:" + case_id + "}) return n"
    pattern5 = re.compile('_\d+')
    case_id_real = str(re.search(pattern5, str(graph.run(cyto).data())).group())[1:]

    pattern6 = re.compile(' \w+_')
    type = str(re.search(pattern6, a).group())[1:-1]
    types = {'crime': 'Crime',
             'drug': 'Drugs',
             'penalty': 'Penalty',
             'person': 'People'}

    cyto1 = "MATCH(n:" + types[type] + "{" + type + "_id:" + type_id + "}) return n"

    type_id_real = str(re.search(pattern5, str(graph.run(cyto1).data())).group())[1:]

    if relationship in prerelationship:
        data = {
            "source": case_id_real,
            "target": type_id_real,
            "relationship": relationship
        }
    else:
        data = {
            "source": type_id_real,
            "target": case_id_real,
            "relationship": relationship
        }

    return {'data': data}


@app.route('/')
def index():
    # print(type(request.query_string))
    return render_template('index.html')


@app.route('/<string:question>')
def index_(question):
    return render_template('index.html', question=question)


@app.route('/graph/<string:question>')
def get_graph(question):
    global NodePoint, nb

    question = question.replace(" ", "")

    print("question:", question)

    # nb = Naive_Bayes("./data/question/")
    # nb = Naive_Bayes("./data/question/")
    # print("2222--------------2222")
    jpype.attachThreadToJVM()
    modelIndex, doubleExist, infoMap = nb.predict(question)

    # modelIndex, doubleExist, infoStr = main("./data/question/", question)

    print("modelIndex", modelIndex)
    print("doubleExist", doubleExist)
    print("infoMap", infoMap)

    cyto_type = ["",
                 "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m",
                 "MATCH(n:Cases)-[r]->(m:People{name:'" + infoMap["nPerson"] + "'}",
                 "MATCH(n:Cases)-[r]->(m) ",
                 "MATCH(n:Cases)-[r]->(m",
                 "MATCH(n:Cases) ",
                 "MATCH(n:Cases) where "]
    cyto2 = ") return "

    # print("modelIndex-------------------", modelIndex)
    for i in range(0, 1):
        if modelIndex in range(0, 13):
            """
                doubleExist
                casePerson
                0: 没有出现
                1: 出现case
                2: 出现Person
            """
            print("0, 12")
            if doubleExist == 0 or (infoMap["nPerson"] == "" and infoMap["nCase"] == ""):
                nodes = []
                edges = []
                ans = "Sorry, I can't answer you!"
                break
            if doubleExist == 2:
                cyto = cyto_type[2] + cyto2
                infoMap["nCase"] = str(graph.run(cyto + "n.name").data()[0]['n.name'])
            cyto = "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m) return "
            NodePoint = "n"
            case_nodes = list(map(buildNodes, graph.run(cyto + "n").data()))
            NodePoint = "m"
            type_nodes = list(map(buildNodes, graph.run(cyto + "m").data()))
            nodes = case_nodes + type_nodes
            edges = list(map(buildEdges, graph.run(cyto + "r").data()))

            # 【0】nCase_nPerson 地点
            if modelIndex == 0:
                print(str(graph.run(cyto + "n.location").data()))
                ans = str(graph.run(cyto + "n.location").data()[0]['n.location'])
            # 【1】nCase_nPerson 时间
            elif modelIndex == 1:
                print(str(graph.run(cyto + "n.year").data()))
                ans = str(graph.run(cyto + "n.year").data()[0]['n.year']) + "年"
            # 【2】nCase_nPerson 人数
            elif modelIndex == 2:
                print(str(graph.run(cyto + "n.people_involved_num").data()))
                ans = str(graph.run(cyto + "n.people_involved_num").data()[0]['n.people_involved_num']) + "人"
            # 【3】nCase_nPerson 法院
            elif modelIndex == 3:
                print(str(graph.run(cyto + "n.court_name").data()))
                ans = str("浙江省" + graph.run(cyto + "n.court_name").data()[0]['n.court_name'] + "人民法院")
            # 【4】nCase_nPerson 第一被告
            elif modelIndex == 4:
                cyto = "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m" + ":People" + cyto2
                print(str(graph.run(cyto + "m.name").data()))
                ans = str(graph.run(cyto + "m.name").data()[0]['m.name'])
            # 【5】nCase_nPerson 最小 年龄
            elif modelIndex == 5:
                print(str(graph.run(cyto + "n.min_age").data()))
                ans = str(graph.run(cyto + "n.min_age").data()[0]['n.min_age']) + "岁"
            # 【6】nCase_nPerson 最小 生日
            elif modelIndex == 6:
                print(str(graph.run(cyto + "n.min_birth").data()))
                ans = str(graph.run(cyto + "n.min_birth").data()[0]['n.min_birth'])
            # 【7】nCase_nPerson 罪
            elif modelIndex == 7:
                cyto = "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m:Crime" + cyto2
                print(str(graph.run(cyto + "m.name").data()))
                ans = str(graph.run(cyto + "m.name").data()[0]['m.name'])
            # 【8】nCase_nPerson 刑
            elif modelIndex == 8:
                cyto = "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m:Penalty" + cyto2
                print(str(graph.run(cyto + "m.name").data()))
                ans = str(graph.run(cyto + "m.name").data()[0]['m.name'])
            # 【9】nCase_nPerson 刑期
            elif modelIndex == 9:
                cyto = "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m:Penalty" + cyto2
                print(str(graph.run(cyto + "m.sentence_years").data()))
                ans = str(graph.run(cyto + "m.sentence_years").data()[0]['m.sentence_years'])
            # 【10】nCase_nPerson 罚金
            elif modelIndex == 10:
                cyto = "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m:Penalty" + cyto2
                print(str(graph.run(cyto + "m.property_penalty_amount").data()))
                ans = str(graph.run(cyto + "m.property_penalty_amount").data()[0]['m.property_penalty_amount']) + "元"
            # 【11】nCase_nPerson 毒品
            elif modelIndex == 11:
                cyto = "MATCH(n:Cases{name:'" + infoMap["nCase"] + "'})-[r]->(m:Drugs" + cyto2
                print(str(graph.run(cyto + "m.name").data()))
                ans = str(graph.run(cyto + "m.name").data()[0]['m.name'])
            # 【12】nPerson 案件
            elif modelIndex == 12:
                print(str(graph.run(cyto + "n.name").data()))
                ans = str(graph.run(cyto + "n.name").data()[0]['n.name'])
            else:
                ans = "Sorry, I can't answer you!"
        elif modelIndex in range(13, 18):
            """
                doubleExist
                yearLocation
                0: 没有出现
                1: 出现year
                2: 出现location
                3: year和location都出现
            """
            print("13, 17")
            pre = ""
            plus = ""
            if doubleExist == 0:
                plus = "return "
            elif doubleExist == 1:
                pre = infoMap["nYear"]
                plus = "where n.year = " + infoMap["nYear"] + " return "
            elif doubleExist == 2:
                pre = infoMap["nLocation"]
                plus = "where n.location = '" + infoMap["nLocation"] + "' return "
            elif doubleExist == 3:
                pre = infoMap["nYear"] + infoMap["nLocation"]
                plus = "where n.year = " + infoMap["nYear"] + " and " + \
                       "n.location = '" + infoMap["nLocation"] + "' return "
            cyto = cyto_type[3] + plus
            print("cyto:", cyto)
            NodePoint = "n"
            case_nodes = list(map(buildNodes, graph.run(cyto + "n").data()))
            NodePoint = "m"
            type_nodes = list(map(buildNodes, graph.run(cyto + "m").data()))
            nodes = case_nodes + type_nodes
            edges = list(map(buildEdges, graph.run(cyto + "r").data()))

            # 【13】nYear_nLocation 案件 数量
            if modelIndex == 13:
                szy = 'count(n)'
                print(str(graph.run(cyto_type[5] + plus + szy).data()))
                ans = pre + "总共有" + str(graph.run(cyto_type[5] + plus + szy).data()[0][szy]) + "起案件"
            # 【14】nYear_nLocation 最小 年龄
            elif modelIndex == 14:
                szy = 'min(n.min_age)'
                print(str(graph.run(cyto + szy).data()))
                ans = pre + "最小年龄为" + str(graph.run(cyto + szy).data()[0][szy]) + "岁"
            # 【15】nYear_nLocation 最高 罚金
            elif modelIndex == 15:
                cyto = cyto_type[4] + ":Penalty) " + plus
                szy = 'max(m.property_penalty_amount)'
                print(str(graph.run(cyto + szy).data()))
                ans = pre + "最高罚金为" + str(graph.run(cyto + szy).data()[0][szy]) + "元"
            # 【16】nYear_nLocation 总 罚金
            elif modelIndex == 16:
                cyto = cyto_type[4] + ":Penalty) " + plus
                szy = 'sum(m.property_penalty_amount)'
                print(str(graph.run(cyto + szy).data()))
                ans = pre + "总共罚金为" + str(graph.run(cyto + szy).data()[0][szy]) + "元"
            # 【17】nYear_nLocation 总 人数
            elif modelIndex == 17:
                szy = 'sum(n.people_involved_num)'
                print(str(graph.run(cyto + szy).data()))
                ans = pre + "总共涉及" + str(graph.run(cyto + szy).data()[0][szy]) + "个人"
            else:
                ans = "Sorry, I can't answer you!"
        else:
            print("18, 19")
            plus = ""
            And = ""
            td = ""
            location = ""
            if doubleExist == 2:
                plus = "n.location = '" + infoMap['nLocation'] + "' "
                And = "and "
                cyto = cyto_type[6] + plus + "return "
                location = infoMap['nLocation']
            else:
                cyto = cyto_type[5] + "return "

            print("cyto:", cyto)
            szy = 'count(n)'
            print(str(graph.run(cyto + szy).data()))
            ans1 = float(graph.run(cyto + szy).data()[0][szy])
            # 【18】nLocation 总 团队 犯案 比例
            if modelIndex == 18:
                td = "团队犯案"
                cyto = cyto_type[6] + plus + And + "n.people_involved_num > 1 return "
            # 【19】nLocation 青年 犯罪 比例
            elif modelIndex == 19:
                td = "青年犯罪"
                cyto = cyto_type[6] + plus + And + "n.min_age <= 30 return "
            print(str(graph.run(cyto + szy).data()))
            ans2 = graph.run(cyto + szy).data()[0][szy]

            nodes = []
            edges = []
            ans = location + "总共犯案" + str(int(ans1)) + "例," \
                  + "其中" + td + "有" + str(int(ans2)) + "例" \
                  + ",故" + td + "比例为:百分之" + str(round(ans2 / ans1 * 100, 2))

    print("nodes")
    print(nodes)
    print("edges")
    print(edges)
    print("ans")
    print(ans)
    print("question")
    print(question)
    return jsonify(elements={"nodes": nodes, "edges": edges, "ans": ans, "que": question})


@app.route("/service")
def service():
    original_sentence = request.args['question']
    print("original_sentence:", original_sentence)
    return redirect("/" + original_sentence)


if __name__ == '__main__':
    app.run(debug=True)
