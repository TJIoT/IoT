# IoT_MQTT 温度、湿度和气压数据发布与订阅系统

## 一、简介

**“IoT_MQTT 温度、湿度和气压数据发布与订阅系统”** 是同济大学软件学院物联网课程的期末项目，该项目实现了基于 MQTT 协议的区域温度、湿度和气压数据的发布订阅系统。此系统旨在收集来自各传感器的数据，并通过 MQTT 协议将数据发送到阿里云物联网平台的中心服务器。数据一旦被接收，将用于转发至订阅端和数据分析端进一步的分析和处理，以便用户能够实时监控和评估特定区域的环境状况。

## 二、团队成员👭👩🏻‍🤝‍👩🏻
同济大学21级软件工程 王琳 张恺瑞 叶洁颖 蔡名雅

## 三、时间安排⏱

| 时间  | 完成事项                                                     | 负责人                           | check |
| ----- | ------------------------------------------------------------ | -------------------------------------- | :---: |
| 12.4  | 第一次讨论:分工摸索数据库MySQL、前端：蔡名雅<br>数据处理和分析方法+语言：张恺瑞<br>发布端+订阅端的前后端：叶洁颖+王琳<br>部署服务器：all people | all people                       |   √   |
| 12.14 | 第二次讨论：一起探究到图书馆关灯嘎嘎嘎<br>现场写代码，配环境~~~ | all people                       |   √   |
| 12.18 | 第三次讨论：确定语言+方法，开始写代码<br>发布端前后端：karry,wl<br>订阅端前后端：jy、my<br>确定了Topic主题是自定义的；确定不使用数据库啦，直接都是从文件读，存储到本地文件中；老师的基本要求就是发布订阅能跑通就行；<br>DDL：12.24（再开一次会，仅实现订阅发布基本流程与界面展示，之后再讨论数据分析处理的问题） | all people<br>课后 <br>济事楼326 |   √   |
| 12.24 | 第四次讨论：再次确定订阅端前端和后端；<br>确定数据处理部分；<br>DDL：12.30日早上八点！！！要有能正常连通的发布端和订阅端的演示，数据可视化，数据预测结果！提前写完的就可以写一下文档了；<br>一起过生日喽~~~ | all people<br>晚上<br>F414-6             |   √   |



## 四、特性🎈

- 使用 MQTT 协议收集和分发数据。
- 使用阿里云物联网平台部署服务器。
- 提供实时数据订阅功能。
- 支持温度、湿度和气压数据的采集和分析。
- 采用 Python 编写，易于理解和扩展。



## 五、界面设计

**发布端：**

![img\publish.png](https://github.com/TJIoT/IoT/blob/main/img/publish.png)

**订阅端：**

登录

![img\login.png](https://github.com/TJIoT/IoT/blob/main/img/login.png)

订阅

![img\subscribe.png](https://github.com/TJIoT/IoT/blob/main/img/subscribe.png)

数据可视化

![img\visualization.png](https://github.com/TJIoT/IoT/blob/main/img/visualization.png)

数据预测

![img\image.png](https://github.com/TJIoT/IoT/blob/main/img/image.png)



## 六、安装指南🔍

在开始使用之前，您需要安装 Python 和必要的库，以及配置 MQTT 服务器。

### 6.1 安装 Python

确保您的系统中安装了 Python 3.6 或更高版本。您可以在 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python。

### 6.2 创建虚拟环境

虚拟环境可以帮助您管理项目依赖，并保持您的系统整洁。为了创建一个虚拟环境，请按照以下步骤操作：

1. 打开终端或 Anaconda Prompt（如果您使用 Anaconda）。
2. 创建新的虚拟环境：

```shell
conda env create -f environment.yml
```

这将创建一个新的conda环境，并安装environment.yml中列出的所有必需包。

3. 激活虚拟环境：
   

创建环境后，你可以通过以下命令激活环境：

```shell
conda activate THPSys
```

现在你可以运行项目中的代码了！

### 6.3 安装依赖库

在虚拟环境中，使用 `pip` 安装所需的 Python 库：

```shell
pip install paho-mqtt pandas flask
```

这将安装 `paho-mqtt` 用于 MQTT 通信，`pandas` 用于数据处理，以及 `flask` 用于 Web 服务。



## 七、运行项目🖐

确保您有一个运行的 MQTT 服务器。如果您没有，可以参考这篇 [文章](https://blog.csdn.net/wwwqqq2014/article/details/121079802) 或 [阿里云官方文档](https://help.aliyun.com/zh/iot/?spm=a2c4g.11186623.0.0.59e82028GocuBE)，根据官方指南安装搭建。

将项目代码克隆到本地：

```shell
git clone https://github.com/LinWang1225/IoT_MQTT.git
```

在设置好所有的依赖，并将账号和密码置换成上述搭建好的MQTT服务器之后，您可以通过以下步骤运行项目：

1. 在项目根目录下执行主程序：

```shell
python publish_app.py
python subcribe_app.py
```

2. 开启另一个终端会话，并订阅 MQTT 主题以接收传感器数据：

```shell
python MQTTClient.py
```

3. 你可以通过访问 Web 服务来查看实时数据：

```shell
在浏览器中打开 http://127.0.0.1:5000/
订阅端：
输入自定义的订阅端ClientID；
输入阿里云子账号的AccessKeyId；
输入阿里云子账号的AccessKeySecret；
点击订阅，跳转至success页面即订阅成功。
此时打开阿里云物联网平台，查看订阅消费组可以看到订阅成功的ClientID等信息。
发布端:
点击connect连接到阿里云服务器；
点击“Pub Random”可以发布一条数值随机的包含温湿度气压全部属性的POST消息；
点击“Pub ALL”会发布文件夹内pubulish_data.csv内的所有数据。
左方按键操作状态都会在右侧日志栏给出日志反馈，以便使用者确定消息发布的成功与否。
```



## 帮助😀

如果您遇到任何问题，可以查看 `README.md` 或提交 Issues 至我们的 GitHub 仓库。

---
