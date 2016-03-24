# /usr/bin/sharpener

This is a worker that will listen to a queue from RabbitMQ, converts the images specified in the message and post a message to the given exchange about the result.

# Installation


```
    1. Have imagemagic installed
    2. if you want sshfs mounts eg. use destination_server or source_sever make sure to have the ssh keys installed with ssh-copy-id
    3. To make sshfs wpork faster  edit ~/.ssh/config and add

       ```
          ControlMaster auto
          ControlPath /tmp/ssh_mux_%h_%p_%r

       ```
   
```

Simply check out this repository and run:

```
    [sudo] python3 setup.py install [--record files.txt]
```

# Usage



You can run the worker by executing the following command:

```
     [-h] [--broker_ip BROKER_IP]
                  [--incoming_queue INCOMING_QUEUE]
                  [--result_exchange RESULT_EXCHANGE]
                  [--result_routing RESULT_ROUTING] [--username USERNAME]
                  [--password PASSWORD] [--broker_port BROKER_PORT]
                  [--result_queue RESULT_QUEUE] [--topic_type TOPIC_TYPE]
```

Information about every parameter can be consulted with:

```
    sharpener -h
```

The worker can be configured with a jp2worker.conf file that has be located in /etc/viaa-workers. If it doesn't exists the command line arguments will be used. You can use command line arguments to overrule property values.

```
[DEFAULT]
BROKER_IP=192.168.56.101                #The ip of the RabbitMQ Broker
BROKER_PORT=5672                        #The port of the RabbitMQ Broker, comment out if not needed. This will default to 5672
INCOMING_QUEUE=incoming_queue           #The name of the queue the worker will listen to
RESULT_EXCHANGE=result_exchange         #The name of result exchange where the worker will publish its result messages to
RESULT_ROUTING=result_routing           #The name of the routing key to be used to publish messages
RESULT_QUEUE=result_queue               #The name of the result queue if this doesn't exist yet. Comment out if not needed
TOPIC_TYPE=direct                       #The name of the topic type for the result queue. Comment out if not needed
USERNAME=guest                          #The username to access the RabbitMQ broker
PASSWORD=guest                          #The password to access the RabbitMQ broker
```
#TODO
optional add a user to mount the dirs (defaults to tcochet) so make sure the user tcochet has read permissions on source and write on destination


# Documentation
example message:
```
{
    "correlation_id":"test_tina002",
    "source_server":"do-tst-app-01.do.viaa.be",
    "source_path":"/home/tcochet",
    "source_file":"test/tiff/test2_sharp.tif",
    "destination_server":"do-mgm-mgm-01.do.viaa.be",
    "destination_path":"/home/tcochet/test/",
    "destination_file":"m0000.tif",
    "level":"0x.1"
}
```
