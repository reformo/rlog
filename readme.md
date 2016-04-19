# Log Service
**A simple event logging service written in Python** that can be used in mobile or web applications
to report any kind of internal and/or API request/response errors or other events.

This service needs Elasticsearch as data store.

### Installation

Edit the shell script **mapping.sh** according to your Elasticsearch configuration.

```
$ pip3 install-r pip.install
chmod u+xwr mappings.sh
./mapping.sh
```

### Usage

```
$ python3 ./logservice.py --es_server="127.0.0.1" --port=8000
```


### Upstart Service

Create a configuration file  **/etc/init/logservice.conf** with following codes

```
description "Log Service"
author "mehmet@mkorkmaz.com"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid nobody
setgid nogroup

exec python3.4 /home/logservice/service/logservice.py --es_server="127.0.0.1" --port=8000
```

**Service management**

```
sudo service logservice start|stop|restart
```

### API

For API details, use [Postman](https://www.getpostman.com/) and import Rlog.json.postman_collection.