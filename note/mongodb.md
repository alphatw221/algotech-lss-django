 'mongodb://'+config.MONGO_DB_USERNAME+':'+urllib.parse.quote_plus(config.MONGO_DB_PASSWORD)+\
    '@34.126.92.142:27017,35.240.200.4:27017,34.126.155.150:27017/'+\
    '?authSource='+config.MONGO_DB_DATABASE_NAME


mongodump --uri="mongodb://[user]:[password]@mongodb0.example.com:27017,mongodb1.example.com:27017,mongodb2.example.com:27017/?authSource=[authSourceDb]&replicaSet=[myReplicaSetName]"


mongodump --uri="mongodb://lss:algo83111T%25%25@34.126.92.142:27017,35.240.200.4:27017,34.126.155.150:27017/?authSource=lss&replicaSet=rs0"


mongorestore --uri="mongodb+srv://lss:agt83111NPP@cluster1.veosu.mongodb.net/" dump/