# publish_app.py
# Function: 用于发布消息的Flask应用程序
import subprocess
from linkkit import linkkit
from flask import Flask, render_template, request, jsonify
import datetime
from MQTTClient import MQTTClient
import csv
import json
import time
import threading

publish_file = "THPData/THP_data.csv"
# 定义变量
product_key = "******"
device_name = "THP-DataSystems"
device_secret = "******"
username = f"{device_name}&{product_key}"
password = "******"
mqtt_broker = f"{product_key}.******"  # MQTT代理服务器的域名或IP地址
mqtt_port = 1883  # MQTT代理服务器的端口
mqtt_topic_post = f'/sys/{product_key}/{device_name}/thing/event/property/post'  # 用于发布消息的主题
mqtt_topic_set = f'/sys/{product_key}/{device_name}/thing/service/property/set'  # 用于发布消息的主题


app = Flask(__name__)
mqtt_client = MQTTClient(product_key, device_name, device_secret)

'''# 一机一密认证
lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key=product_key,
    device_name=device_name,
    device_secret=device_secret
)'''

# 全局变量，用于存储状态
publish_status = {
    'count': 0,
    'complete': False,
    'error': None
}
stop_publishing = False # 用于停止发布数据的标志

# 读取public_file中的数据，并按照第一列的数据从小到大排序生成信文档，排序完成后写回文件
def sort_data(publish_file):
    with open(publish_file, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        data.sort(key=lambda x: int(x[0]))
    with open(publish_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# 读取并发布数据的后台线程
def read_and_publish_data(topic, publish_file):
    global publish_status, stop_publishing
    try:
        # ... 发布数据的代码 ...
        # 确保更新 publish_status['count'] 和 publish_status['complete'] ...
        sort_data(publish_file) # 排序数据
        with open(publish_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if stop_publishing:
                    break
                if len(row) == 4:
                    # 从行中提取数据并构建属性字典
                    prop_data = {
                        "DetectTime": str(int(row[0])),  # 假设 CSV 文件中的时间戳已经是毫秒格式
                        "CurrentTemperature": float(row[1]),
                        "CurrentHumidity": float(row[2]),
                        "CurrentPressure": int(row[3])
                    }
                    # 构造上报数据结构
                    payload = {
                        "id": "123",
                        "version": "1.0",
                        "params": prop_data,
                        "method": "thing.event.property.post"
                    }
                    # 上报属性
                    rc, request_id = mqtt_client.lk.publish_topic(
                        topic,
                        json.dumps(payload)
                    )
                    publish_status['count'] += 1
                    if rc == 0:
                        print(f"Posted {publish_status['count']} entries so far.")
                    else:
                        print(f"thing post property failed, rc={rc}")
                        publish_status['error'] = f"No.{publish_status['count']} post failed, rc={rc}"
                        publish_status['complete'] = True
                    time.sleep(1)  # 防止发送过快，根据平台限制可能需要调整
            print("Data posting complete. Total entries posted:", {publish_status['count']})
    except Exception as e:
        publish_status['error'] = str(e)
    finally:
        publish_status['complete'] = True
        stop_publishing = False    # 重置停止标志

@app.route('/')
def index():
    return render_template('publish.html')  # 确保HTML文件名与实际文件名相匹配

@app.route('/connect', methods=['POST'])
def connect():
    if not mqtt_client.is_connected():
        mqtt_client.connect()
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'connected', 'message': 'Connecting...'})
    else:
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'already_connected', 'message': 'Already connected.'})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if mqtt_client.is_connected():
        mqtt_client.disconnect()
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'disconnected', 'message': 'Disconnected successfully.'})
    else:
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'already_disconnected', 'message': 'Already disconnected.'})


@app.route('/subPost', methods=['POST'])
def subPost():
    if not mqtt_client.is_connected():
        mqtt_client.connect()
    mqtt_client.subscribe(mqtt_topic_post)
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': 'Subscribed to topic: /thing/event/property/post.'})

@app.route('/unSubPost', methods=['POST'])
def connunSubPostect():
    if not mqtt_client.is_connected():
        mqtt_client.connect()
    mqtt_client.unsubscribe(mqtt_topic_post)
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': 'Unsubscribed to topic: /thing/event/property/post.'})

@app.route('/publishRandom', methods=['POST'])
def publishRandom():
    if not mqtt_client.is_connected():
        mqtt_client.connect()
    # 发布随机数据
    mqtt_client.post_random_data(mqtt_topic_post)
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': 'Random data published.'})

@app.route('/startPublish', methods=['POST'])
def start_publish():
    if not mqtt_client.is_connected():
        mqtt_client.connect()
    global publish_status,stop_publishing
    stop_publishing = False  # 确保停止标志为False，以便开始新的发布流程
    publish_status = {'count': 0, 'complete': False, 'error': None}
    thread = threading.Thread(target=read_and_publish_data, args=(mqtt_topic_post, publish_file))
    thread.start()
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'started', 'message': 'Data publishing started.'})

@app.route('/publishStatus', methods=['GET'])
def publish_status():
    if not mqtt_client.is_connected():
        mqtt_client.connect()
    global publish_status
    return jsonify(publish_status)

@app.route('/stopPublish', methods=['POST'])
def stop_publish():
  global stop_publishing
  stop_publishing = True # 设置停止标志为真
  return jsonify({'message': 'Stopping publishing process...'})

if __name__ == '__main__':
    app.run(debug=True)
