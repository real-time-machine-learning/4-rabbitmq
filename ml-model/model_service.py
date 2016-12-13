
"""这里我们试图打造一个RPC 服务，可以通过它预测苹果公司股票变动情况。该程序需要完成以下几个操作：

1) 监听RabbitMQ队列，从中读取实时股票报价数据
2) 将实时股票报价数据写入到Redis高速缓存中
3) 从Redis高速缓存中读取最近10秒报价
4) 将报价送入预测服务进行预测
5) 将预测结果送入RabbitMQ预测结果处理队列
"""

import pika 
import time 
import json 
import logging 
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib 
import pandas as pd 
from timeseriesutil import * 

from redis_operation import RedisDataBridge 

rabbitmq_host = "rabbitmq" 
live_data_exchange_name = "stock_price" 
live_data_queue_name = "ml_queue" 

result_exchange_name = "prediction_result" 
result_queue_name = "prediction_result_queue" 

## 设置日志等级，以便于在Docker输出中观察运行情况
logging.getLogger().setLevel(logging.INFO) 

## 创建和RabbitMQ之间的连接，如果遇见连接失败的情况（可能是RabbitMQ的服
## 务器正在启动中），等待若干秒之后重试连接。
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host = rabbitmq_host, 
                              connection_attempts = 10, 
                              retry_delay = 20))
logging.info("成功连接RabbitMQ %s" % rabbitmq_host) 

## 创建和RabbitMQ之间的频道：注意连接是一个独立TCP/IP协议连接，而频道是
## 其中的一个逻辑分隔。这一个频道将会专门为新的报价数据所用，我们后面将
## 会创建其他频道，为机器学习操作所用
channel_live_data = connection.channel()

## 创建一个交换中心，采用fanout模式
channel_live_data.exchange_declare(exchange = live_data_exchange_name, 
                                   type = "fanout")

## 创建一个队列，为该客户端独享
channel_live_data.queue_declare(queue = live_data_queue_name, 
                                exclusive = True) 

## 将队列和交换中心联系在一起
channel_live_data.queue_bind(exchange = live_data_exchange_name, 
                             queue = live_data_queue_name) 

## 创建和Redis高速缓存之间的连接: 
redis_data_bridge = RedisDataBridge("redis", read_length = 12) 

## 我们利用机器学习模型对前来的数据进行预测分析之后，需要将结果传入下游
## 系统中进行使用。这里我们仍然利用RabbitMQ，将分析完成的数据放入一个
## RabbitMQ的扇形交换中心，下游使用预测结果的服务只需读取对应该扇形交换
## 中心的队列即可。
channel_results = connection.channel()

## 创建分发预测结果的交换中心
channel_results.exchange_declare(exchange = result_exchange_name,
                                 type = "fanout") 

## 创建对预测结果进行储存的队列
channel_results.queue_declare(queue = result_queue_name,
                              exclusive = True) 

## 将预测结果储存队列和交换中心绑定在一起。
channel_results.queue_bind(exchange = result_exchange_name,
                           queue = result_queue_name)

## 准备机器学习预测模型
model = joblib.load("saved-stock-pipeline.PyData") 

def ProcessPrice(channel, method, properties, body):
    """该函数是读取数据之后触发的函数。执行数据缓存、处理，以及后期预测所有
    工作。
    """ 
    data = json.loads(body.decode("utf-8")) 
    symbol = data["symbol"]
    timestamp = data["timestamp"]
    price = data["price"]
    
    ## 更新和缓存价格 
    redis_data_bridge.update_quote(symbol, price, timestamp) 
    
    ## 读取历史价格
    price_data = redis_data_bridge.get_latest_quote(symbol, read_length = 11)
    logging.info(price_data) 
    
    ## 进行一点小小的数据处理 
    if price_data.shape[0] >= 11:
        prediction = model.predict(price_data) 
        
        logging_data = {"symbol": symbol, 
                        "timestamp": timestamp,
                        "prediction": prediction} 
        channel_results.basic_publish(exchange = result_exchange_name,
                                      body = logging_data)
                                      
        


channel_live_data.basic_consume(ProcessPrice,
                                queue = live_data_queue_name,
                                no_ack=True)

logging.info("成功完成初始化，开始接收消息")
channel_live_data.start_consuming() 
