# 分布式数据库的大作业

## 后端

使用ngnix + uwsgi + Django实现

启动命令：
```
uwsgi --ini PMS_uwsgi.ini
```

## 数据库实现

### 配置服务器 config.conf

配置文件：
```
systemLog:
  destination: file
  logAppend: true
  path: /data/mongodb/21000/mongodb.log
storage:
  dbPath: /data/mongodb/21000/
  journal:
    enabled: true
processManagement:
  fork: true
net:
  port: 21000
  bindIp: 127.0.0.1
replication:
  replSetName: conf
sharding:
  clusterRole: configsvr
```

启动后执行：
```
mongod -f server1/conf/cong.conf --shardsvr

config = { 
  _id:"conf", 
  configsvr: true,
  members:[
    {_id:0,host:"127.0.0.1:20000"},
    {_id:1,host:"127.0.0.1:30000"},
    {_id:2,host:"127.0.0.1:40000"}
  ]
}
rs.initiate(config)
rs.status() 
```

### 路由服务器 mongos.conf

配置文件
```
systemLog:
  destination: file
  logAppend: true
  path: /data/mongodb/20000/mongodb.log
processManagement:
  fork: true
net:
  port: 20000
  bindIp: 0.0.0.0
sharding:
  configDB: config/192.168.1.182:21000,192.168.1.186:21000,192.168.1.122:21000
```

启动后命令：（使用mongos命令启动）
```
sh.addShard("gotham/127.0.0.1:23000,127.0.0.1:33000,127.0.0.1:43000");
sh.addShard("nyc/127.0.0.1:24000,127.0.0.1:34000,127.0.0.1:44000");
sh.addShard("foxriver/127.0.0.1:22000,127.0.0.1:32000,127.0.0.1:42000");
sh.status()

sh.shardCollection("pms2.ppp",{"numbering":"hashed"})

sh.addTagRange("pms3.prison",{"numbering":0},{"numbering":19999},"fox")
sh.addTagRange("pms3.prison",{"numbering":20000},{"numbering":39999},"go")
sh.addTagRange("pms3.prison",{"numbering":40000},{"numbering":59999},"n")
```


### 数据服务器

配置文件
```
systemLog:
  destination: file
  logAppend: true
  path: /data/mongodb/27001/mongodb.log
storage:
  dbPath: /data/mongodb/27001/
  journal:
    enabled: true
processManagement:
  fork: true
net:
  port: 27001
  bindIp: 0.0.0.0
replication:
  replSetName: data1
sharding:
  clusterRole: shardsvr
```

启动后执行：
```
mongod -f server3/data/foxriver/foxriver.conf --shardsvr

config = { 
  _id:"gotham", 
  members:[
    {_id:0,host:"127.0.0.1:23000"},
    {_id:1,host:"127.0.0.1:33000"},
    {_id:2,host:"127.0.0.1:43000"}
  ]
}
rs.initiate(config)
rs.status() #查看状态
```

## 参考网站

https://api.mongodb.com/python/current/api/pymongo/index.html

https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html