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