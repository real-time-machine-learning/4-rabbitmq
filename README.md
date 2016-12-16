
# 利用RabbitMQ消息队列架设实时机器学习服务

本章我们将会学习RabbitMQ在实战中的用法，并且应用RabbitMQ搭建消息队列，
整合实时机器学习应用中的各种服务。

## 下载本章实例程序 

下载本章实例程序和数据，只需执行下面操作：

``` shell 
git clone https://github.com/real-time-machine-learning/4-rabbitmq
``` 

## 安装配置软件环境

本章会运用到Docker作为集群配置方法，其余软件均通过Docker配置安装。

 * 如需要复习Docker安装配置方法，[看这里](https://github.com/real-time-machine-learning/3-docker-intro) 
 * 如需复习Scikit Learn基本操作，[看这里](https://github.com/real-time-machine-learning/2-scikit-learn-intro)
 * 如需复习Pandas基本操作，[看这里](https://github.com/real-time-machine-learning/1-pandas-intro)

## 利用RabbitMQ搭建股价预测集群

完成之后我们的集群的构架如下图：

![案例构架](pics/overall-design.png)


--- 

《实时机器学习实战》 彭河森、汪涵
