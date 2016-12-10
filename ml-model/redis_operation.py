"""该程序包含所有跟Redis有关的操作。其主要作用有：

1) 将最新的报价数据更新在redis缓存中
2) 从redis缓存读取最近一段时间的报价

这里为了方便读者阅读，我们让1) 和2) 序列执行，实际应用中我们可以让1) 和
2)成为并行操作，可以大大减少延迟。
"""

import redis 

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
        value = {timestamp: price}
        self.client.lpush(key, value) 

    def get_latest_quote(self, symbol, read_length= None):
        if read_length is None:
            read_length = self.read_length 
        key = self.price_prefix + symbol
        self.client.lrange(key, 0, read_length) 
