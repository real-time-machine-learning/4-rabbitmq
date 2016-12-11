"""该程序包含所有跟Redis有关的操作。其主要作用有：

1) 将最新的报价数据更新在redis缓存中
2) 从redis缓存读取最近一段时间的报价

这里为了方便读者阅读，我们让1) 和2) 序列执行，实际应用中我们可以让1) 和
2)成为并行操作，可以大大减少延迟。
"""

import redis 
import json 
import pandas as pd 
import pickle 

def parse_response_core(input_blob):
    """ 将从Redis读取的数据转换为dict格式""" 
    return pickle.loads(input_blob)
    
def parse_response(input_blob_list):
    """该函数将input_blob_list转换为一个list，每个元素是一个dict，最后返回
    pandas DataFrame""" 
    parsed_list = list(map(parse_response_core, input_blob_list))
    return pd.DataFrame(parsed_list)    

class RedisDataBridge():
    """该类负责更新数据和读取历史数据两方面工作。

    使用该类将会将数据存在redis中，其中键是 price_prefix+[股票代码]　
    """ 
    def __init__(self, host, read_length = 12, price_prefix = ""):
        """初始化该类的对象，需要设置redis服务器地址(host)和读取记录的长度(默认
        12)个""" 
        self.client = redis.Redis(host = host) 
        self.read_length = read_length 
        self.price_prefix = price_prefix 

    def update_quote(self, symbol, price, timestamp):
        """更新队列中股票报价 """ 
        key = self.price_prefix + symbol
        value = {"timestamp": timestamp, "price": price}
        self.client.lpush(key, pickle.dumps(value)) 

    def get_latest_quote(self, symbol, read_length= None):
        if read_length is None:
            read_length = self.read_length 
        key = self.price_prefix + symbol
        result_blob = self.client.lrange(key, 0, read_length) 
        result = parse_response(result_blob)        
        return result
