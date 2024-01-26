# main.py
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import csv
import time
import sys
from linkkit import linkkit
import os
import random

input_file = "THPData/merged_data.csv"
output_file = "THPData/THP_data.csv"
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

# Read the input file and process the data
with open(input_file, 'r') as file:
    reader = csv.reader(file)
    next(reader, None)  # Skip the header
    processed_rows = []
    
    for row in reader:
        if len(row) > 0:
            # 注意这里的时间格式更改为 '%Y-%m-%dT%H:%M:%S' 以匹配您文件中的时间戳格式
            try:
                timestamp = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S").timestamp() * 1000
                processed_row = [str(int(timestamp))] + [col for col in row[1:] if col.strip() != ""]
                processed_rows.append(processed_row)
            except ValueError as e:
                print(f"Error parsing date for row: {row[0]}, Error: {str(e)}")
                continue

print("read over")

# Write the processed data to the output file
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(processed_rows)
    print("write over")


# 一机一密认证
lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key=product_key,
    device_name=device_name,
    device_secret=device_secret
)

# 从云端控制台下载物模型文件，该文件需要集成到应用工程中
lk.thing_setup("tsl.json")

connected = False # 增加一个全局变量来跟踪连接状态
# 连接到物联网平台后的回调，成功连接session_flag为0
def on_connect(session_flag, rc, userdata):
    global connected
    if rc == 0: # 连接成功
        connected = True
        print("on_connect:%d,rc:%d,userdata:" % (session_flag, rc))
    else:
        print("Connection failed with error code:", rc)
    
# 断开连接后的回调
def on_disconnect(rc, userdata):
    print("on_disconnect:rc:%d,userdata:" % rc)
    pass

# 订阅主题成功后的回调
def on_subscribe(mid, qos, userdata):
    print("on_subscribe mid:%d,qos:%s,userdata:" % (mid, qos))
    pass

# 取消订阅主题成功后的回调
def on_unsubscribe(mid, userdata):
    print("on_unsubscribe mid:%d,userdata:" % mid)
    pass

# 发布消息成功后的回调
def on_publish(mid, userdata):
    print("on_publish mid:%d,userdata:" % mid)
    pass

# 收到消息后的回调
def on_message(topic, payload, qos, userdata):
    print("on_message topic:%s,payload:%s,qos:%d,userdata:" % (topic, payload, qos))
    pass

# 当出现网络波动时，程序自动循环调用连接，显示效果为两个回调函数一直调用
lk.on_connect = on_connect
lk.on_disconnect = on_disconnect

lk.on_subscribe = on_subscribe # 订阅主题成功后的回调
lk.on_unsubscribe = on_unsubscribe # 取消订阅主题成功后的回调

lk.on_publish = on_publish # 发布消息成功后的回调
lk.on_message = on_message # 收到消息后的回调

lk.connect_async() # 异步连接
lk.start_worker_loop() # 开启循环

print("linkkit init success")

# 假设有一个函数可以获取当前的属性值
def get_current_property_values():
    # 这里应当是从传感器或其他源获取实际的数据
    property_values = {
        # 假设的湿度传感器值
        "CurrentHumidity": {
            "value": random.randint(0, 100),
            "time": 1524448722000
        },
        # 假设的温度传感器值
        "CurrentTemperature": {
            "value": 23.0,
            "time": 1524448722000
        },
        # 当前时间的Unix时间戳（毫秒）
        "DetectTime": {
            "value": int(round(time.time() * 1000)),
            "time": 1524448722000
        },
        # 假设的压力传感器值
        "CurrentPressure": {
            "value": 1044,
            "time": 1524448722000
        },
    }
    
    # 创建符合特定格式的数据结构
    data_structure = {
        "id":"123",
        "version":"1.0",
        "params":property_values,
        "method":"thing.event.property.post"
    }
    
    return data_structure

# 读取数据并上报
def read_and_post_data(publish_file, linkkit_instance):
    with open(publish_file, 'r') as file:
        reader = csv.reader(file)
        count = 0
        for row in reader:
            if len(row) == 4:
                # 从行中提取数据并构建属性字典
                prop_data = {
                    "DetectTime": int(row[0]),  # 假设 CSV 文件中的时间戳已经是毫秒格式
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
                rc, request_id = linkkit_instance.publish_topic(
                    mqtt_topic_post,
                    json.dumps(payload)
                )
                if rc == 0:
                    print(f"thing post property success:{rc}, request id:{request_id}")
                else:
                    print(f"thing post property failed, rc={rc}")
                count += 1
                print(f"Posted {count} entries so far.")
                time.sleep(1)  # 防止发送过快，根据平台限制可能需要调整
        print("Data posting complete. Total entries posted:", count)

# 增加while循环，保证物联网平台是连接上之后再开始通信的
while True:
    try: 
        msg = input() # 输入任意字符，开始通信
    except KeyboardInterrupt:
        sys.exit() # 退出程序
    if not connected:
        print("Waiting for connection...")
        time.sleep(1) # 等待一段时间让连接尝试完成
        continue # 跳过本次循环迭代
    else:
        if msg == "1":
            lk.disconnect() # 断开连接
        elif msg == "2":
            lk.connect_async() # 重新连接
        elif msg == "3": # 输入为3时，订阅post这个主题，每个主题只需要订阅一次，会在物联网平台的设备topic中显示
            rc, mid = lk.subscribe_topic(mqtt_topic_post) # 订阅主题
            if rc == 0:
                print("subscribe success, topic=%s" % mqtt_topic_post)
            else:
                print("subscribe failed, rc=%d" % rc)
        elif msg == "4": # 输入为4时，取消订阅post这个主题
            rc, mid = lk.unsubscribe_topic(mqtt_topic_post)
            if rc == 0:
                print("unsubscribe success, topic=%s" % mqtt_topic_post)
            else:
                print("unsubscribe failed, rc=%d" % rc)
            '''elif msg == "5": # 输入为5时，发布消息到receier这个主题
            rc, mid = lk.publish_topic(lk.to_full_topic("user/receiver"), "hello world")
            if rc == 0:
                print("publish success, topic=%s" % lk.to_full_topic("user/receiver"))
            else:
                print("publish failed, rc=%d" % rc)'''
        elif msg == "6": # 输入为6时，同时订阅多个topic
            rc, mid = lk.subscribe_topic([(mqtt_topic_post, 1),
                                          (mqtt_topic_set, 1),])
            if rc == 0:
                print("subscribe multiple topics success:%r, mid:%r" % (rc, mid))
            else:
                print("subscribe failed, rc=%d" % rc)
        elif msg == "7": # 输入为7时，取消订阅多个topic
            rc, mid = lk.unsubscribe_topic([mqtt_topic_post,
                                            mqtt_topic_set])
            if rc == 0:
                print("unsubscribe multiple topics success:%r, mid:%r" % (rc, mid))
            else:
                print("unsubscribe failed, rc=%d" % rc)
        elif msg == "8": # RRPC请求
            lk.on_message = on_message # 收到消息后的回调
        elif msg == "11": # 属性上报
            # 属性上报
            '''
            prop_data = {
                "CurrentTemperature":25.5,
                "CurrentHumidity":60.3,
                "CurrentPressure":1013,
                "DetectTime":int(round(time.time() * 1000))
            }'''
            # 获取当前的属性值
            property_values = get_current_property_values()
            # 准备上报的JSON数据
            payload = json.dumps(property_values)
            print(payload)  # 打印包含当前时间戳的属性值

            rc, request_id = lk.thing_post_property(payload)
            if rc == 0:
                print("thing post property success:%r, request id:%r" % (rc, request_id))
            else:
                print("thing post property failed, rc=%d" % rc)
        elif msg == "12": # 属性上报
            # 上报随机属性
            prop_data = {
                "CurrentTemperature": random.randint(-10.0, 40.0),
                "CurrentHumidity": random.randint(0.0, 100.0),
                "CurrentPressure": random.randint(900, 1100),
                "DetectTime": int(round(time.time() * 1000))
            }
            # 构造上报数据结构
            payload = {
                "id": "123",
                "version": "1.0",
                "params": prop_data,
                "method": "thing.event.property.post"
            }
            # 上报属性
            rc, request_id = lk.publish_topic(mqtt_topic_post, json.dumps(payload))
            if rc == 0:
                print("thing post property success:%r, request id:%r" % (rc, request_id))
            else:
                print("thing post property failed, rc=%d" % rc)
        elif msg == "13": # 属性批量上报
            # 属性上报
            read_and_post_data(publish_file, lk)
        elif msg == "98": # 打印topic列表
            ret = lk.dump_user_topics()
            print("dump user topics:%r" % ret)
        elif msg == "99": # 退出程序
            lk.destruct()
            print("destructed")
        else:
            sys.exit()



# MQTT配置参数
MQTT_BROKER = '******.******'  # MQTT代理服务器的域名或IP地址
MQTT_PORT = 1883                  # MQTT代理服务器的端口
MQTT_TOPIC = '/sys/******/THP-DataSystems/thing/event/property/post'        # 用于发布消息的主题

def on_connect(client, userdata, flags, rc):
    """
    连接到MQTT代理服务器的回调函数

    Parameters:
        client (mqtt.Client): MQTT客户端实例
        userdata: 用户数据
        flags: 连接标志
        rc (int): 连接结果代码

    Returns:
        None
    """
    print(f"Connected with result code {rc}")

# 将时间字符串转换为时间戳
def time_to_timestamp(time_str):
    dt_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
    return int(dt_obj.timestamp()) * 1000

# 读取数据文件并解析为字典的函数
def read_data(file_path):
    with open(file_path, 'r') as file:
        # 用于存储所有解析后的数据的字典
        combined_data = {}
        # 逐行读取和解析JSON
        for line in file:
            # 解析当前行的JSON数据
            line_data = json.loads(line)
            # 将解析后的字典合并到总字典中
            combined_data.update(line_data)
    return combined_data

# 合并温度、湿度和气压数据的函数
def merge_data(temperature_data, humidity_data, pressure_data):
    merged_data = {}
    for time_str in humidity_data:
        merged_data[time_str] = {
            "temperature": temperature_data.get(time_str, None),
            "humidity": humidity_data.get(time_str, None),
            "pressure": pressure_data.get(time_str, None)
        }
    return merged_data

# 读取数据
temperature_data = read_data('THPData/temperature.txt')
humidity_data = read_data('THPData/humidity.txt')
pressure_data = read_data('THPData/pressure.txt')

# 合并数据
merged_dict = merge_data(temperature_data, humidity_data, pressure_data)

# 写入合并后的数据到表格
def write_data_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['time', 'temperature', 'humidity', 'pressure'])
        for time_str, values in data.items():
            temperature = values.get('temperature', '')
            humidity = values.get('humidity', '')
            pressure = values.get('pressure', '')
            writer.writerow([time_str, temperature, humidity, pressure])

# 写入数据到表格
write_data_to_csv(merged_dict, 'THPData/merged_data.csv')

# 转换时间并准备数据用于发布
publish_data = []
for time_str, data in merged_dict.items():
    if all(value is not None for value in data.values()):
        timestamp = time_to_timestamp(time_str)
        data['timestamp'] = timestamp
        publish_data.append(data)

# 连接到MQTT代理并发送数据
client = mqtt.Client()
client.username_pw_set('THP-DataSystems&******', '******')  # 替换为你的用户名和密码
client.on_connect = on_connect

# 连接到MQTT代理
client.connect(MQTT_BROKER, MQTT_PORT, 60)
# 开始网络循环
client.loop_start()
# 给予一点时间来完成连接
time.sleep(1)  # 可能需要更长时间


# 发布合并后的数据
for data in publish_data:
    client.publish(MQTT_TOPIC, json.dumps(data))

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully.")

# 设置回调函数
client.on_publish = on_publish

# 在发送完所有数据之后，停止网络循环并断开连接
client.loop_stop()
client.disconnect()
