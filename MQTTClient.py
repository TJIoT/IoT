# MQTTClient.py
import json
import random
import time
from linkkit import linkkit
import csv
from datetime import datetime

class MQTTClient:
    def __init__(self, product_key, device_name, device_secret):
        self.lk = linkkit.LinkKit(
            host_name="cn-shanghai",
            product_key=product_key,
            device_name=device_name,
            device_secret=device_secret
        )
        self.product_key = product_key
        self.device_name = device_name
        self.device_secret = device_secret
        self.mqtt_topic_post = f'/sys/{product_key}/{device_name}/thing/event/property/post'
        self.connected = False
        # 设置回调函数
        self.lk.on_connect = self.on_connect
        self.lk.on_disconnect = self.on_disconnect
        self.lk.on_publish = self.on_publish
        self.lk.on_message = self.on_message
        # 从云端控制台下载物模型文件，该文件需要集成到应用工程中
        self.lk.thing_setup("tsl.json")

    def on_connect(self, session_flag, rc, userdata):
        if rc == 0:
            self.connected = True
            print(f"MQTT Connected (session_flag={session_flag}, rc={rc})")
        else:
            print(f"MQTT Connection failed (rc={rc})")

    def on_disconnect(self, rc, userdata):
        self.connected = False
        print(f"MQTT Disconnected (rc={rc})")

    def on_publish(self, mid, userdata):
        print(f"Message published (mid={mid})")

    def on_message(self, topic, payload, qos, userdata):
        print(f"Message received (topic={topic}, payload={payload}, qos={qos})")

    def connect(self):
        self.lk.connect_async()
        self.lk.start_worker_loop()  # 开启循环
        print("MQTT client connecting...")
        # self._connect_event.wait(timeout=10)  # Wait up to 10 seconds for connection
        if not self.connected:
            print("MQTT client connection timed out.")
        return self.connected

    def disconnect(self):
        self.lk.disconnect()
        print("MQTT client disconnecting...")

    def publish(self, topic, message):
        result, mid = self.lk.publish_topic(topic, json.dumps(message))
        return result, mid
    
    def subscribe(self, topic):
        result, mid = self.lk.subscribe_topic(topic)
        return result, mid
    
    def unsubscribe(self, topic):
        result, mid = self.lk.unsubscribe_topic(topic)
        return result, mid

    def is_connected(self):
        return self.connected
    
    # 上报随机数据
    def post_random_data(self, topic):
        # 上报随机属性
        prop_data = {
            "CurrentTemperature": random.randint(-10.0, 40.0),
            "CurrentHumidity": random.randint(0.0, 100.0),
            "CurrentPressure": random.randint(900, 1100),
            "DetectTime": str(int(round(time.time() * 1000)))
        }
        # 构造上报数据结构
        payload = {
            "id": "123",
            "version": "1.0",
            "params": prop_data,
            "method": "thing.event.property.post"
        }
        # 上报属性
        rc, request_id = self.lk.publish_topic(topic, json.dumps(payload))
        if rc == 0:
            print("thing post property success:%r, request id:%r" % (rc, request_id))
        else:
            print("thing post property failed, rc=%d" % rc)
    
    # 读取数据并上报
    '''def read_and_post_data(self, publish_file, topic):
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
                    rc, request_id = self.lk.publish_topic(
                        topic,
                        json.dumps(payload)
                    )
                    if rc == 0:
                        print(f"thing post property success:{rc}, request id:{request_id}")
                    else:
                        print(f"thing post property failed, rc={rc}")
                    count += 1
                    print(f"Posted {count} entries so far.")
                    time.sleep(1)  # 防止发送过快，根据平台限制可能需要调整
            print("Data posting complete. Total entries posted:", count)'''