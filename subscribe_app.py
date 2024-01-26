# subscribe_app.py
# Description: Flask web app for subscribing to the IoT platform
import csv
import json

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import datetime
import subscribe_module as module

app = Flask(__name__)
app.secret_key = '******'
product_key = "******"
device_name = "THP-DataSystems"
device_secret = "******"
mqtt_topic_post = f'/sys/{product_key}/{device_name}/thing/event/property/post'  # 用于发布消息的主题
mqtt_topic_set = f'/sys/{product_key}/{device_name}/thing/service/property/set'  # 用于发布消息的主题
import global_var as gv
filename = "out.csv"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #从表单获取参数
        ClientID = request.form['ClientID']
        access_key_id = request.form['access_key_id']
        access_key_secret = request.form['access_secret']
        #尝试连接并订阅
        try:
            gv.global_var.user_initiated_disconnect = False
            module.connect_and_subscribe(ClientID, access_key_id, access_key_secret)            
            return redirect(url_for('subscribe'))#路由到subscribe界面
        except Exception as e:
            flash('订阅失败，请检查输入的ID和Secret。错误信息：' + str(e))  
    # GET请求
    return render_template('login.html')


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    # GET请求
    return render_template('subscribe.html')

#类似地，如果要新建接口，就设置路径和方法，然后在函数中实现接口逻辑即可
#最后的return部分，可以根据需要返回JSON数据或者HTML页面
#json数据里包括时间戳、状态和消息，可以用于前端页面的显示
@app.route('/disconnect', methods=['GET'])
def disconnect():
    try:
        # 调用断开连接的函数
        module.disconnect_mqtt()
        flash('成功断开连接。')
    except Exception as e:
        flash('断开连接时发生错误：' + str(e))
    return redirect(url_for('index'))#路由到login界面

#我们有唯一的一个post主题，而且连接后会马上订阅这个主题，所以不需要再写一个订阅post主题的接口
@app.route('/subTopic', methods=['POST'])
def subTopic():
    # 获取前端传递的JSON数据
    data=request.get_json()
    topic = data.get('topic', '')
    checked = True if data.get("checked") == "1" else False
    #将topic转为字符串形式，并且全部字母变成小写
    topic = str(topic).lower()
    if checked:
        if topic not in gv.global_var.topic_list:
            gv.global_var.topic_list.append(topic)
            return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': 'Topic List: ' + module.format_topiclist(gv.global_var.topic_list)+ '.'})
    if checked==False:
        if topic in gv.global_var.topic_list:
            gv.global_var.topic_list.remove(topic)
            return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': 'Topic List: ' + module.format_topiclist(gv.global_var.topic_list)+ '.'})
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'fail', 'message': 'Topic List: ' + module.format_topiclist(gv.global_var.topic_list)+ '.'})

#读取数组，将指定topic的数据以及相应的时间戳返回给前端
#前端需要每隔1秒调用一次这个接口，以获取最新的数据
#可以参考checkPublishStatus
@app.route('/TopicData', methods=['GET'])
def getTopicData():
    formatted_ans =""
    #遍历receive_data，receive_data的每个元素是一个字典，字典里有topic和data两个键
    #如果字典里的topic和topic_list里的某个元素相同，则将该字典加入ans
    for prop_data in gv.global_var.receive_data:
        if(prop_data['printed']==False):
            prop_data['printed'] = True
            formatted_ans +=module.format_topicData(prop_data)
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': formatted_ans})


#把数据存储到csv文件，并清空receive_data
@app.route('/saveData', methods=['GET', 'POST'])
def saveData():
    with open(filename, 'a', newline='') as file:#采用追加模式打开文件
        writer = csv.writer(file)
        # 通过writer，往写入数据
        for prop_data in gv.global_var.receive_data:
            #在这一行中，第一列是时间，第二列是温度，第三列是湿度，第四列是气压
            row = [prop_data.get('time', ''), prop_data.get('temperature', ''), prop_data.get('humidity', ''),
                   prop_data.get('pressure', '')]
            writer.writerow(row)
    gv.global_var.receive_data.clear()
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': 'STORED DATA SUCCESSFULLY.'})

@app.route('/getChart', methods=['GET'])
def getChart():
    # GET请求
    # 获取查询参数
    variable = request.args.get('variable', default='temperature', type=str)
    return render_template('chart.html', variable=variable)

@app.route('/chart', methods=['GET'])
def getTHPChart():
    topic=request.args.get("variable")
    try:
        if topic == "temperature":
            col=1
        elif topic == "humidity":
            col=2
        elif topic == "pressure":
            col=3
        else:
            # 抛出异常
            raise Exception("Invalid topic")
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            csv_data=[]
            for row in reader:
                #print(row)
                if row[col]!="" :
                    read_data={}
                    read_data["time"] = float(row[0])
                    read_data[topic] = float(row[col])
                    csv_data.append(read_data)
            #对csv_data,按照time从小到大排序
            csv_data.sort(key=lambda x: x["time"])
            x_data=[]
            y_data=[]
            #遍历csv_data，将time和temperature分别存入x_data和y_data
            for data in csv_data:
                #对于放到x_data里的时间戳，需要转换成字符串形式
                x_data.append(module.timestamp_to_time(data["time"]) )
                y_data.append(data[topic])
            #构造要返回的数据结构
            ans_data={
                "isSuccess":True,
                "type":topic,
                "x_data":x_data,
                "y_data":y_data
            }

    except Exception as e:
        ans_data={
            "isSuccess":False,
            "type":topic,
            "x_data":[],
            "y_data":[]
        }
        print("Error:",e)
    finally:
        return jsonify(ans_data)

@app.route('/getPredict', methods=['GET'])

def getPredict():
    return render_template('predict.html')

@app.route('/predict', methods=['GET'])
def getPredictData():
    all_topic=["temperature","humidity","pressure"]
    try:
        csv_data={}
        csv_data["temperature"]=[]
        csv_data["humidity"]=[]
        csv_data["pressure"]=[]
        #根据topic，遍历不同的csv文件
        for topic in all_topic:
            if topic == "temperature":
                predict_file="forecast_data_Tem.csv"
            elif topic == "humidity":
                predict_file="forecast_data_Hum.csv"
            elif topic == "pressure":
                predict_file="forecast_data_Pre.csv"
            else:
                # 抛出异常
                raise Exception("Invalid topic")
            with open(predict_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)#跳过第一行
                for i in range(1,20):#只取前20行
                    row=next(reader)
                    #print(row)
                    if row[0]!="":
                        read_data={}
                        read_data["month"] = row[0]
                        read_data["day"] = row[1]
                        read_data["hour"] = row[2]
                        read_data[topic] = float(row[3])
                        read_data["predict_"+topic] = float(row[4])
                        csv_data[topic].append(read_data)
        data=[]
        for i in range(0,3):
            to_put_into_data={}
            print(all_topic[i])
            to_put_into_data["type"]=all_topic[i]
            to_put_into_data["x_data"]=[]
            to_put_into_data["ry_data"]=[]#真实值
            to_put_into_data["py_data"]=[]#预测值
            #对csv_data[all_topic[i]]，按照month从小到大排序，如果month相同，按照day从小到大排序，如果day相同，按照hour从小到大排序
            csv_data[all_topic[i]].sort(key=lambda x: (float(x["month"]),float(x["day"]),float(x["hour"])))

            for csv_one_data in csv_data[all_topic[i]]:
                #x_data需要先从csv_data找到对应的topic
                to_put_into_data["x_data"].append(module.format_time(str(csv_one_data["month"]),str(csv_one_data["day"]),str(csv_one_data["hour"])))
                to_put_into_data["ry_data"].append(csv_one_data[all_topic[i]])
                to_put_into_data["py_data"].append(csv_one_data["predict_"+all_topic[i]])
            data.append(to_put_into_data)

        #构造要返回的数据结构
        ans_data={
            "isSuccess":True,
            "data":data
        }
        
    except Exception as e:
        ans_data={
            "isSuccess":False,
            "data":[]
        }
        print("Error:",e)
    finally:
        return jsonify(ans_data)


if __name__ == '__main__':
    app.run(debug=True)
