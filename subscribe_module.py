# encoding=utf-8
# subscribe_module.py
import base64
import csv
import hashlib
import hmac
import json
import ssl
import threading
import time
import stomp
import schedule
from datetime import datetime
import global_var as gv

YourHost = "******"
YourClientId = "******"
YourIotInstanceId = "******"
YourConsumerGroupId = "******"
ALIBABA_CLOUD_ACCESS_KEY_ID = "******"
ALIBABA_CLOUD_ACCESS_KEY_SECRET = "******"
conn = None

YourHost = "******"
ClientId = None
YourIotInstanceId = "******"
YourConsumerGroupId = "******"
accessKey = None
accessSecret = None
# ALIBABA_CLOUD_ACCESS_KEY_SECRET = "******"
csv_file = "receive_data.csv"

def disconnect_mqtt():
    global conn, clientId, accessKey, accessSecret
    try:
        if conn and conn.is_connected():
            conn.disconnect()
            gv.global_var.user_initiated_disconnect = True  # 设置断开标志
            # 清除clientID、accessKey和accessSecret
            clientId = None
            accessKey = None
            accessSecret = None
            print("MQTT connection is disconnected.")
    except Exception as e:
        print('Error while trying to disconnect:', e)

def connect_and_subscribe(YourClientId, accessKey_id, accessKey_secret):
    # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例使用环境变量获取 AccessKey 的方式进行调用，仅供参考
    global clientId, accessKey, accessSecret, conn
    accessKey =  accessKey_id # os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID']
    accessSecret = accessKey_secret # os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
    consumerGroupId = YourConsumerGroupId
    # iotInstanceId：实例ID。
    iotInstanceId = YourIotInstanceId
    clientId = YourClientId
    # 签名方法：支持hmacmd5，hmacsha1和hmacsha256。
    signMethod = "hmacsha1"
    timestamp = current_time_millis()
    # userName组装方法，请参见AMQP客户端接入说明文档。
    # 若使用二进制传输，则userName需要添加encode=base64参数，服务端会将消息体base64编码后再推送。具体添加方法请参见下一章节“二进制消息体说明”。
    username = clientId + "|authMode=aksign" + ",signMethod=" + signMethod \
                    + ",timestamp=" + timestamp + ",authId=" + accessKey \
                    + ",iotInstanceId=" + iotInstanceId \
                    + ",consumerGroupId=" + consumerGroupId + "|"
    signContent = "authId=" + accessKey + "&timestamp=" + timestamp
    # 计算签名，password组装方法，请参见AMQP客户端接入说明文档。
    password = do_sign(accessSecret.encode("utf-8"), signContent.encode("utf-8"))

    try:
        #  接入域名，请参见AMQP客户端接入说明文档。这里直接填入域名，不需要带amqps://前缀
        conn =stomp.Connection([(YourHost, 61614)], heartbeats=(0,300))
        conn.set_ssl(for_hosts=[(YourHost, 61614)], ssl_version=ssl.PROTOCOL_TLS)
        # conn.set_listener('', MyListener(conn))
        # 实例化MyListener时传入凭据
        listener = MyListener(conn, clientId, accessKey, accessSecret)
        conn.set_listener('', listener)
        conn.connect(username, password, wait=True)
        # 清除历史连接检查任务，新建连接检查任务
        schedule.clear('conn-check')
        schedule.every(1).seconds.do(do_check, conn).tag('conn-check')
        # connect_and_subscribe(conn)

        # 启动一个新线程以保持连接检查
        # 异步线程运行定时任务，检查连接状态
        thread = threading.Thread(target=connection_check_timer)
        thread.start()
    except Exception as e:
        # 可以抛出自定义异常或记录错误
        # raise CustomConnectionError('连接失败: {}'.format(e))
        print('connecting failed')
        raise e

class MyListener(stomp.ConnectionListener):
    def __init__(self, conn, client_id, access_key, access_secret):
        self.conn = conn
        self.client_id = client_id
        self.access_key = access_key
        self.access_secret = access_secret

    def on_error(self, frame):
        print('received an error "%s"' % frame.body)

    def on_message(self, frame):
        print('received a message "%s"' % frame.body)
        transform_data(frame)


    def on_heartbeat_timeout(self):
        print('on_heartbeat_timeout')

    def on_connected(self, headers):
        print("successfully connected")
        self.conn.subscribe(destination='/topic/#', id=1, ack='auto')
        print("successfully subscribe")

    def on_disconnected(self):
        print('disconnected')
        # connect_and_subscribe(self.conn)
        # 使用保存的凭据重新连接
        # connect_and_subscribe(self.client_id, self.access_key, self.access_secret)

def current_time_millis():
    return str(int(round(time.time() * 1000)))

def do_sign(secret, sign_content):
    m = hmac.new(secret, sign_content, digestmod=hashlib.sha1)
    return base64.b64encode(m.digest()).decode("utf-8")

# 检查连接，如果未连接则重新建连
def do_check(conn):
    global clientId, accessKey, accessSecret
    if clientId is None or accessKey is None or accessSecret is None:
        print('please input clientId, accessKey and accessSecret')
        return
    print('check connection, is_connected: %s', conn.is_connected())
    if (not conn.is_connected()):
        try:
            # 只有在确保不是因为用户主动断开连接时才尝试重新连接
            if not gv.global_var.user_initiated_disconnect:
                connect_and_subscribe(clientId, accessKey, accessSecret)
        except Exception as e:
            print('Error while trying to reconnect:', e)

# 定时任务方法，检查连接状态
def connection_check_timer():
    while 1:
        schedule.run_pending()
        time.sleep(10)

#把时间戳转换成字符串
def timestamp_to_time(timestamp):
    if(type(timestamp) == float):
        dt_obj = datetime.fromtimestamp(timestamp / 1000.0)
    else:
        dt_obj = datetime.fromtimestamp(timestamp / 1000)
    return dt_obj.strftime('%Y-%m-%d T %H:%M:%S')
# 将时间字符串转换为时间戳
def time_to_timestamp(time_str):
    dt_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
    return int(dt_obj.timestamp()) * 1000
def transform_data(frame):
    str_result = frame.body
    print(type(frame.body))#str类型
    print(str_result)#{"deviceType":"CustomCategory","iotId":"6kKJ5DcsITYMMbJdQvYdk0kqp0","requestId":"123","checkFailedData":{},"productKey":"k0kqpFwvVRy","gmtCreate":1703778965509,"deviceName":"THP-DataSystems","items":{"CurrentHumidity":{"value":83,"time":1703778965505},"CurrentTemperature":{"
    result= json.loads(str_result)
    prop_data= {}
    prop_data["time"] = int(result['items']['DetectTime']['value'])
    prop_data["temperature"] = float(result['items']['CurrentTemperature'].get("value", None))
    prop_data["humidity"] = float( result['items']['CurrentHumidity'].get("value", None))
    prop_data["pressure"] = int( result['items']['CurrentPressure'].get("value", None))
    ans_data={}
    print(str(len(gv.global_var.topic_list)))
    for topic in gv.global_var.topic_list:
        if prop_data[topic] is not None:
            ans_data[topic] = prop_data[topic]
    if (ans_data != {}):
        ans_data['time'] = prop_data['time']
        ans_data["printed"] = False
        gv.global_var.receive_data.append(ans_data)
        print(format_topicData(ans_data))

def format_topicData(prop_data):
    formatted_ans = "time:"+timestamp_to_time(prop_data["time"])+" "
    formatted_ans +=( " ".join([f"{k}:{v}" for k, v in prop_data.items() if k != "printed" and k!="time"]) + "\n")
    return formatted_ans
def format_time(month,day,hour):
    return "2014-"+month+"-"+day+" "+hour+":00"
def format_topiclist(topic_list):
    formatted_ans = ""
    for topic in topic_list:
        formatted_ans+= topic + " "
    return formatted_ans
    
# 读取数据，整理
#写一个函数，它从csv中读取数据，然后存进receive_data里
def read_data():
    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            gv.global_var.receive_data = []
            for row in reader:
                prop_data = {}
                for i in range(0,3):
                    if row[i] != "":
                        if i == 0:
                            prop_data["time"] = int(row[i])
                        elif i == 1:
                            prop_data["temperature"] = float(row[i])
                        elif i == 2:
                            prop_data["humidity"] = float(row[i])
                        elif i == 3:
                            prop_data["pressure"] = int(row[i])
                if prop_data:
                    gv.global_var.receive_data.append(prop_data)
            print("Data reading complete. Total entries getted:", len(gv.global_var.receive_data))
            return gv.global_var.receive_data
     #处理异常
    except Exception as e:
        print('Error while trying to read data:', e)
        return None


