
"""该模块实现使用Scikit learn对股票走势进行预测，可以所示对Scikit
learn模型的一个增强，其中包含两方面：

1) 增加模型的自动更新功能，通过读取RabbitMQ的消息队列，可以实现模型实时
更新

2) 实现

""" 

import pandas as pd 
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib 



