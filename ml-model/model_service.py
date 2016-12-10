
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

from redis_operation import RedisDataBridge 


time.sleep(30) 

live_data_exchange_name = "stock_price" 
live_data_queue_name = "ml_queue" 

## 创建和RabbitMQ之间的连接
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host = "rabbitmq"))

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

def ProcessPrice(channel, method, properties, body):
    """该函数是读取数据之后触发的函数。执行数据缓存、处理，以及后期预测所有
    工作。
    """ 
    print(body)
    print(str(body)) 
    data = json.loads(str(body)) 
    symbol = data["symbol"]
    price = data["price"]
    timestamp = data["timestamp"]
    
    ## 更新和缓存价格 
    redis_data_bridge.update_quote(symbol, price, timestamp) 
    
    ## 读取历史价格
    ## price_data = redis_data_bridge.get_latest_quote(symbol)

channel_live_data.basic_consume(ProcessPrice,
                                queue = live_data_queue_name,
                                no_ack=True)

channel_live_data.start_consuming() 
